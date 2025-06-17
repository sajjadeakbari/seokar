import pytest
from seokar import SEOAnalyzer
from seokar.plugins import AhrefsPlugin

@pytest.fixture
def mock_analyzer():
    return SEOAnalyzer()

@pytest.fixture
def mock_ahrefs_plugin():
    return AhrefsPlugin(api_key="test-key")
