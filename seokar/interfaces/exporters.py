import abc
from typing import Any, Optional, Dict, List


class BaseReportExporter(abc.ABC):
    """
    Base abstract class for all Seokar report exporters.
    Ensures a consistent interface for modules responsible for exporting analysis data.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor for the base report exporter.
        """
        pass

    @abc.abstractmethod
    def export(self, report_data: Any, output_path: Optional[str] = None) -> Optional[str]:
        """
        Abstract method to export report data to a specific format.

        Args:
            report_data: The data to be exported (e.g., SEOResult, SEOSummaryReport).
            output_path: Optional file path for the output. If None, the exported
                         data should be returned as a string.

        Returns:
            The path to the output file if saved to disk, or the exported data
            as a string if output_path is None. Returns None on failure.
        """
        pass

    @abc.abstractmethod
    def get_exporter_info(self) -> Dict[str, Any]: # Changed from Dict[str, str] to Dict[str, Any] because supported_formats is List[str]
        """
        Abstract method to return information about the exporter.

        Returns:
            A dictionary containing 'name', 'supported_formats' (list of strings),
            and 'description' of the exporter.
        """
        pass
