import abc
from typing import Optional, Dict
from ..models import SEOResult


class BaseAnalysisPlugin(abc.ABC):
    """
    Base abstract class for all Seokar analysis plugins.
    Ensures a consistent interface for third-party analysis modules.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor for the base analysis plugin.
        """
        pass

    @abc.abstractmethod
    def analyze(self, html_content: str, url: str) -> Optional[SEOResult]:
        """
        Abstract method to perform SEO analysis on the given HTML content and URL.

        Args:
            html_content: The HTML content of the page.
            url: The URL of the page being analyzed.

        Returns:
            An SEOResult object if analysis is successful, otherwise None.
        """
        pass

    @abc.abstractmethod
    def get_plugin_info(self) -> Dict[str, str]:
        """
        Abstract method to return information about the plugin.

        Returns:
            A dictionary containing 'name', 'version', and 'description' of the plugin.
        """
        pass
