from enum import Enum

class AnalysisMode(str, Enum):
    BASIC = "basic"
    FULL = "full"
    COMPETITOR = "competitor"

DEFAULT_USER_AGENT = "SeoKar/2.0 (+https://github.com/sajjadeakbari/seokar)"
MAX_CONCURRENT_REQUESTS = 5
