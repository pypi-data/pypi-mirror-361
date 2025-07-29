import logging
from ipaddress import IPv4Address, IPv4Network
from typing import ClassVar, Union

from pydantic import Field, field_validator

from policy_inspector.model.base import MainModel

logger = logging.getLogger(__name__)


class AddressObject(MainModel):
    """Base class representing a network address object."""

    singular: ClassVar[str] = "Address Object"
    plural: ClassVar[str] = "Address Objects"

    name: str = Field(..., description="Name of the address object.")
    description: str = Field(default="", description="Object description")
    tags: set[str] = Field(default_factory=set, description="Tags")

    def __str__(self):
        return f"{self.name}[{str(getattr(self, 'value', ''))}]"

    def __repr__(self):
        return self.__str__()

    def is_covered_by(self, other: "AddressObject") -> bool:
        raise NotImplementedError("To be implement in child class")

    @classmethod
    def parse_json(cls, elements: list[dict]) -> list["AddressObject"]:
        """Parse JSON data from PAN-OS API response"""
        type_map = {
            "ip-netmask": AddressObjectIPNetwork,
            "ip-range": AddressObjectIPRange,
            "fqdn": AddressObjectFQDN,
        }

        address_objects = []
        for data in elements:
            key_name = next(k for k in type_map if k in data)
            subclass = type_map[key_name]

            data_tag: Union[dict, None] = data.get("tag", None)
            if not data_tag:
                tags = set()
            else:
                tags = set(data_tag.get("member", []))

            model = subclass(
                name=data.get("@name"),
                value=data[key_name],
                description=data.get("description", ""),
                tags=tags,
            )
            address_objects.append(model)
        return address_objects

    @classmethod
    def parse_csv(cls, elements: list[dict]) -> list["AddressObject"]:
        """Parse CSV row from spreadsheet import"""
        address_objects = []
        for data in elements:
            type_map = {
                "IP Address": AddressObjectIPNetwork,
                "IP Range": AddressObjectIPRange,
                "FQDN": AddressObjectFQDN,
            }
            addr_type = data.get("Type", "")
            try:
                subclass = type_map[addr_type]
            except KeyError as ex:
                raise ValueError(f"Unknown 'Type'='{addr_type}'") from ex

            tags = data.get("Tag", "")
            tags = tags.split(";") if tags else set()
            model = subclass(
                name=data["Name"],
                value=data["Address"],
                description=data.get("Description", ""),
                tags=tags,
            )
            address_objects.append(model)
        return address_objects


class AddressObjectIPNetwork(AddressObject):
    """Represents an IPv4 network range using CIDR notation."""

    value: IPv4Network = Field(
        ..., description="IPv4 network address and mask in CIDR format"
    )

    @field_validator("value", mode="before")
    @classmethod
    def convert(cls, v) -> IPv4Network:
        """Convert string to IPv4Network instance.

        Raises:
            ValueError: For invalid network formats
        """
        try:
            return IPv4Network(v, strict=False)
        except ValueError as ex:
            raise ValueError(f"value '{v}' is not a valid IPv4 network") from ex

    def is_covered_by(self, other: "AddressObject") -> bool:
        """Check if this network is fully contained within another object.

        Returns:
            True if either:
            - Contained within another IP network
            - Fully inside an IP range
        """
        if isinstance(other, AddressObjectIPNetwork):
            return self.value.subnet_of(other.value)
        if isinstance(other, AddressObjectIPRange):
            return (
                self.value.network_address >= other.value[0]
                and self.value.broadcast_address <= other.value[1]
            )
        return False


class AddressObjectIPRange(AddressObject):
    """Represents a contiguous range of IPv4 addresses."""

    value: tuple[IPv4Address, IPv4Address] = Field(
        ..., description="Address IP range value"
    )

    @field_validator("value", mode="before")
    @classmethod
    def convert(cls, v) -> tuple[IPv4Address, IPv4Address]:
        """Convert string or list to IPv4Address tuple."""
        if isinstance(v, str):
            parts = tuple(v.split("-"))
            return tuple(map(IPv4Address, parts))
        if isinstance(v, (tuple, list)):
            return tuple(map(IPv4Address, v))
        return v

    @field_validator("value", mode="after")
    @classmethod
    def validate(cls, v):
        """Ensure valid IP range ordering.

        Raises:
            ValueError: If end address precedes start address
        """
        if v[0] > v[1]:
            raise ValueError("last IP address must be greater than first")
        return v

    def is_covered_by(self, other: "AddressObject") -> bool:
        """Check if this range is fully contained within another object.

        Returns:
            True if either:
            - Fully inside another IP network
            - Contained within another IP range
        """
        if isinstance(other, AddressObjectIPNetwork):
            network_start = other.value.network_address
            network_end = other.value.broadcast_address
            return (
                self.value[0] >= network_start and self.value[1] <= network_end
            )
        if isinstance(other, AddressObjectIPRange):
            return (
                self.value[0] >= other.value[0]
                and self.value[1] <= other.value[1]
            )
        return False


class AddressObjectFQDN(AddressObject):
    """Represents a fully qualified domain name."""

    value: str = Field(..., description="Address FQDN value")

    # @field_validator("value", mode="after")
    # @classmethod
    # def validate(cls, v: str) -> str:
    #     """Normalize and validate FQDN format.
    #
    #     Raises:
    #         ValueError: For invalid domain name formats
    #     """
    #     v = v.lower()
    #     fqdn_regex = r"^([a-z0-9-]{1,63}\.)+[a-z0-9-]{2,63}$"
    #     if not re.match(fqdn_regex, v):
    #         raise ValueError(
    #             f"Invalid FQDN={v}. Not matches regex: {fqdn_regex}"
    #         )
    #     return v

    def is_covered_by(self, other: "AddressObject") -> bool:
        """Check FQDN equivalence.

        Returns:
            True if both FQDNs match exactly (case-insensitive)
        """
        if isinstance(other, AddressObjectFQDN):
            return self.value.lower() == other.value.lower()
        return False
