seokar/
├── __init__.py              # Exports core functionality
├── analyzer.py              # Main analysis engine (همان فایل ارتقا یافته)
├── constants/               # تمام ثابت‌های سئو
│   ├── __init__.py          # Core constants
│   ├── core.py              # Basic SEO (title, meta, etc.)
│   ├── technical.py         # Technical SEO standards
│   ├── content.py           # Content quality metrics
│   ├── local.py             # Local SEO parameters
│   ├── schema.py            # Schema.org requirements
│   └── security.py          # Security headers
├── models.py                # Data structures (همان مدل‌های ارتقا یافته)
├── utils/                   # ابزارهای کمکی
│   ├── __init__.py
│   ├── helpers.py           # URL validation, text processing
│   ├── network.py           # HTTP requests, caching
│   └── text_analysis.py     # NLP tools
├── exceptions.py            # Custom exceptions
├── interfaces/              # برای توسعه پلاگین‌ها
│   ├── __init__.py
│   ├── analysis.py          # Base analysis interface
│   └── exporters.py         # Report export interfaces
└── tests/                   # تست‌های کامل
    ├── __init__.py
    ├── test_analyzer.py     # تست‌های آنالایزر
    ├── test_models.py
    ├── test_constants/
    │   ├── test_core.py
    │   └── test_technical.py
    └── test_utils/
        ├── test_helpers.py
        └── test_network.py
