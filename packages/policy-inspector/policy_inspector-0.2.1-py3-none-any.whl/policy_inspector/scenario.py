import logging
from typing import TYPE_CHECKING, Optional, TypeVar

if TYPE_CHECKING:
    from policy_inspector.panorama import PanoramaConnector

logger = logging.getLogger(__name__)

ScenarioResults = TypeVar("ScenarioResults")
AnalysisResult = TypeVar("AnalysisResult")


class Scenario:
    """
    Base class for defining security scenarios and checks.

    Attributes:
        name: Scenario display name.
        panorama: PanoramaConnector instance for data retrieval.
        _scenarios: A set of all registered subclasses of Scenario.
    """

    name: Optional[str] = None

    _scenarios: dict[str, type["Scenario"]] = {}

    def __init__(self, panorama: "PanoramaConnector", **kwargs) -> None:
        """
        Initialize a Scenario instance.

        Args:
            panorama: PanoramaConnector instance for data retrieval.
            **kwargs: Additional keyword arguments for subclass customization.
        """
        self.panorama = panorama
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init_subclass__(cls, **kwargs) -> None:
        """Registers subclasses automatically in the `scenarios` set."""
        super().__init_subclass__(**kwargs)
        cls._scenarios[str(cls)] = cls

    def __str__(self):
        return self.name or self.__class__.__name__

    @classmethod
    def get_available(cls) -> dict[str, type["Scenario"]]:
        """
        Retrieve all registered ``Scenario`` subclasses.

        Returns:
            A set containing all subclasses of ``Scenario``.
        """
        return cls._scenarios

    @classmethod
    def from_name(cls, name: str) -> type["Scenario"]:
        return cls._scenarios[name]

    def show(self, formats, *args, **kwargs):
        """
        Show scenario results in the given formats using registered show functions.
        """
        for fmt in formats:
            show_func = None
            from policy_inspector.utils import get_show_func

            show_func = get_show_func(self, fmt)
            if show_func:
                show_func(self, *args, **kwargs)
            else:
                logger.warning(
                    f"No show function registered for {type(self).__name__} and format '{fmt}'"
                )

    def export(self, formats, *args, **kwargs):
        """
        Export scenario results in the given formats using registered export functions.
        """
        for fmt in formats:
            export_func = None
            from policy_inspector.utils import get_export_func

            export_func = get_export_func(self, fmt)
            if export_func:
                export_func(self, *args, **kwargs)
            else:
                logger.warning(
                    f"No export function registered for {type(self).__name__} and format '{fmt}'"
                )

    def execute(self) -> ScenarioResults:
        """
        Execute the scenario logic.

        Warnings:
            This method must be implemented by subclasses.

        Returns:
            The results of executing.
        """
        raise NotImplementedError

    def analyze(self, results: ScenarioResults) -> AnalysisResult:
        """
        Analyze the results obtained from executing a scenario.

        Warnings:
            This method must be implemented by subclasses.

        Args:
            results: The results to analyze.

        Returns:
            The analysis outcome.
        """
        raise NotImplementedError

    def execute_and_analyze(self) -> AnalysisResult:
        """Execute the scenario and analyze the results."""
        results = self.execute()
        return self.analyze(results)
