from setuptools import setup, find_packages

setup(
    name="seokar",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.24.0",
        "beautifulsoup4>=4.12.0",
        "typer>=0.9.0",
        "pydantic>=2.0",
        "aiohttp>=3.8.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.0",
            "mypy>=1.8.0",
            "ruff>=0.1.0",
            "black>=24.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.5.0",
            "twine>=5.0.0",
            "types-requests>=2.31.0",
        ],
        "ahrefs": ["ahrefs-api>=2.0.0"],
        "semrush": ["semrush-api>=1.5.0"],
        "google": ["google-api-python-client>=2.0.0"],
    },
    entry_points={
        "console_scripts": [
            "seokar=seokar.cli.main:app",
        ],
    },
)
