# Plugin Development Guide

SeoKar Pro supports plugins to extend functionality.

## Creating a Plugin

1. Create a class inheriting from `BasePlugin`
2. Implement required methods
3. Register your plugin

Example plugin:

```python
from typing import List, Optional
from seokar.plugins import BasePlugin
from seokar.core.models import BacklinkInfo

class MyBacklinkPlugin(BasePlugin):
    async def get_backlinks(self, url: HttpUrl) -> List[BacklinkInfo]:
        return [
            BacklinkInfo(
                url="https://example.com",
                domain_authority=80,
                spam_score=10,
                anchor_text="Example"
            )
        ]
        
    async def get_pagespeed(self, url: HttpUrl) -> Optional[PageSpeedMetrics]:
        return None
```

## Available Plugin Types

### Backlink Plugins
Implement `get_backlinks()` to provide backlink data.

### PageSpeed Plugins
Implement `get_pagespeed()` to provide performance metrics.

## Registering Plugins

```python
from seokar import SEOAnalyzer
from my_plugins import MyBacklinkPlugin

analyzer = SEOAnalyzer()
analyzer.plugins.register("my_plugin", MyBacklinkPlugin())
```

## Built-in Plugins

### AhrefsPlugin
Provides backlink data using Ahrefs API.

```python
from seokar.plugins.ahrefs import AhrefsPlugin

plugin = AhrefsPlugin(api_key="your-key")
```

### GooglePagespeedPlugin
Provides PageSpeed metrics using Google API.

```python
from seokar.plugins.google import GooglePagespeedPlugin

plugin = GooglePagespeedPlugin(api_key="your-key")
```

### SemrushPlugin
Provides SEMrush data integration.

```python
from seokar.plugins.semrush import SemrushPlugin

plugin = SemrushPlugin(api_key="your-key")
```
