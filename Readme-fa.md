# Seokar - کتابخانه جامع تحلیل سئو داخلی (On-Page) 🐍

[![PyPI version](https://badge.fury.io/py/seokar.svg)](https://badge.fury.io/py/seokar)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/seokar)

**Seokar** یک کتابخانه قدرتمند و جامع پایتون است که برای تحلیل عمیق سئو داخلی (On-Page) محتوای HTML طراحی شده است. این ابزار به توسعه‌دهندگان و متخصصان سئو کمک می‌کند تا صفحات وب را ممیزی کرده، مشکلات را شناسایی و توصیه‌های عملی برای بهبود دیده‌شدن در موتورهای جستجو و تجربه کاربری دریافت کنند.

---

## ✨ ویژگی‌های کلیدی

- **تحلیل جامع:** پوشش طیف گسترده‌ای از فاکتورهای سئو داخلی:
  - **متا تگ‌ها:** عنوان (Title)، توضیحات متا (Meta Description)، متا روبات‌ها (Meta Robots)، URL کانونیکال (Canonical URL)، ویوپورت (Viewport)، مجموعه کاراکتر (Charset)، زبان HTML.
  - **فاوآیکون (Favicon):** تشخیص لینک فاوآیکون یا استفاده از پیش‌فرض.
  - **ساختار عناوین (Heading Structure):** تعداد تگ‌های H1-H6، سلسله‌مراتب و کیفیت محتوای آن‌ها.
  - **کیفیت محتوا (Content Quality):** طول محتوا، تشخیص محتوای ضعیف (Thin Content)، نسبت متن به HTML، خوانایی (شاخص Flesch Reading Ease)، چگالی کلمات کلیدی.
  - **سئو تصاویر (Image SEO):** وجود و کیفیت متن جایگزین (`alt`).
  - **تحلیل لینک‌ها (Link Analysis):** لینک‌های داخلی/خارجی، ویژگی‌های `nofollow`, `sponsored`, `ugc`، انواع انکر تکست (Anchor Text).
  - **تگ‌های شبکه‌های اجتماعی (Social Media Tags):** اعتبارسنجی تگ‌های Open Graph (og:*) و Twitter Card (twitter:*).
  - **داده‌های ساختاریافته (Structured Data):** تشخیص JSON-LD، Microdata، RDFa به همراه انواع Schema.org.
- **توصیه‌های عملی:** پیشنهادات واضح و مبتنی بر شدت مشکل برای رفع ایرادات (INFO, GOOD, WARNING, ERROR, CRITICAL).
- **امتیاز سلامت سئو (SEO Health Score):** امتیاز کلی (۰-۱۰۰٪) بر اساس شدت مشکلات یافت‌شده.
- **گزارش‌دهی دقیق:** دیکشنری با ساختار مناسب شامل تمام نتایج، مشکلات و توصیه‌ها.
- **کشینگ امن برای ریسه‌ها (Thread-Safe Caching):** بهینه‌سازی تحلیل‌های تکراری با استفاده از کشینگ امن.
- **پایتون مدرن:** تایپینگ دقیق (Strict typing)، `dataclasses`، و `__slots__` برای بهینه‌سازی حافظه.
- **ثابت‌های قابل تنظیم:** امکان تنظیم آسان آستانه‌های سئو و کلمات توقف (Stop Words).

---

## 🚀 نصب

برای نصب Seokar، دستور زیر را در ترمینال خود اجرا کنید:

```bash
pip install seokar
```

---

## 🛠️ استفاده پایه

در اینجا یک مثال ساده از نحوه استفاده از Seokar برای تحلیل محتوای HTML آورده شده است:

```python
from seokar import Seokar, SEOResultLevel, __version__

print(f"Seokar Version: {__version__}")

# نمونه محتوای HTML برای تحلیل
sample_html_content = """
<!DOCTYPE html>
<html lang="fa-IR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>صفحه آزمایشی من - تحلیل سئو</title>
    <meta name="description" content="یک توضیح کوتاه اما شیرین برای صفحه آزمایشی.">
    <link rel="canonical" href="https://example.com/test-page">
    <link rel="icon" href="/favicon.ico">
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://example.com/test-page">
    <meta property="og:title" content="صفحه آزمایشی من - تحلیل سئو">
    <meta property="og:description" content="یک توضیح کوتاه اما شیرین برای صفحه آزمایشی.">
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://example.com/test-page">
    <meta property="twitter:title" content="صفحه آزمایشی من - تحلیل سئو">
    <meta property="twitter:description" content="یک توضیح کوتاه اما شیرین برای صفحه آزمایشی.">
</head>
<body>
    <h1>عنوان اصلی صفحه</h1>
    <p>این یک پاراگراف نمونه با چند کلمه کلیدی است. سئو برای هر وب‌سایتی مهم است. کلمه کلیدی.</p>
    <img src="image.jpg" alt="توضیح تصویر اول">
    <img src="another-image.png"> <!-- تصویر بدون متن جایگزین -->
    <p>محتوای بیشتر برای افزایش طول متن. ما در حال تلاش برای بهبود سئو این صفحه هستیم.</p>
    <h2>یک عنوان فرعی H2</h2>
    <p>لینک به <a href="https://example.com">سایت خارجی</a> و یک <a href="/internal-page" rel="nofollow">لینک داخلی نوفالو</a>.</p>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "صفحه آزمایشی من - تحلیل سئو",
      "description": "یک توضیح کوتاه اما شیرین برای صفحه آزمایشی."
    }
    </script>
</body>
</html>
"""
```

# ایجاد یک نمونه از Seokar
# می‌توانید URL را نیز به جای محتوای HTML ارسال کنید:
```
# analyzer = Seokar(url="https://example.com")
analyzer = Seokar(html_content=sample_html_content, target_url="https://example.com/test-page", target_keyword="کلمه کلیدی")
```
# انجام تحلیل
```
report = analyzer.analyze()
```
# چاپ امتیاز کلی سلامت سئو
```
print(f"امتیاز سلامت سئو: {report['seo_health']['score']}%")
```
# چاپ مشکلات یافت‌شده
```
print("\nمشکلات یافت‌شده:")
if report['issues']:
    for issue in report['issues']:
        print(f"- [{issue['level']}] {issue['message']} (عنصر: {issue['element_type']})")
        if 'recommendation' in issue:
            print(f"  توصیه: {issue['recommendation']}")
else:
    print("هیچ مشکلی یافت نشد. عالی!")
```
# برای مشاهده گزارش کامل:
```
# import json
# print(json.dumps(report, indent=2, ensure_ascii=False))

```

---

## 📊 درک گزارش

گزارش تحلیل بازگردانده شده توسط `Seokar.analyze()` یک دیکشنری با ساختار مشخص است که شامل چندین بخش می‌باشد:

| نام بخش          | توضیحات                                                                                             |
|-------------------|-----------------------------------------------------------------------------------------------------|
| `seo_health`      | خلاصه سلامت کلی سئو با امتیاز (۰-۱۰۰) و تعداد مشکلات بر اساس شدت                                     |
| `basic_seo`       | متادیتای پایه استخراج شده از صفحه مانند عنوان، توضیحات متا، URL کانونیکال و زبان                       |
| `headings`        | جزئیات مربوط به عناوین (h1-h6) شامل تعداد و صحت سلسله‌مراتب                                           |
| `content_quality` | طول محتوا، نسبت متن به HTML، امتیاز خوانایی، هشدارهای محتوای ضعیف                                    |
| `image_seo`       | تحلیل تصاویر برای وجود و کیفیت ویژگی `alt`                                                          |
| `links`           | جزئیات لینک‌های داخلی و خارجی، ویژگی‌هایی مانند nofollow، sponsored، ugc                             |
| `social_tags`     | اعتبارسنجی تگ‌های Open Graph و Twitter Card                                                         |
| `structured_data` | داده‌های ساختاریافته یافت‌شده مانند JSON-LD، Microdata، RDFa به همراه انواع schema.org                 |
| `issues`          | لیستی از تمام مشکلات یافت‌شده، هرکدام با شدت، پیام، نوع عنصر آسیب‌دیده و توصیه‌ها                     |

---

### سطوح نتایج سئو (SEO Result Levels)

هر مشکل یا یافته در گزارش دارای یک سطح اهمیت است:

| نام سطح   | توضیحات                               |
|-----------|--------------------------------------|
| INFO      | نکات اطلاعاتی، بدون مشکل              |
| GOOD      | عملکرد خوب، سیگنال‌های مثبت           |
| WARNING   | مشکلات بالقوه، نیاز به بررسی دارد     |
| ERROR     | مشکلات قطعی که نیاز به اصلاح دارند     |
| CRITICAL  | مشکلات شدید، نیازمند اصلاح فوری      |

---

## 🔍 جداول جزئیات (نمونه)

در ادامه، نمونه‌ای از اطلاعاتی که در هر بخش از گزارش ممکن است مشاهده کنید، آمده است.

### ۱. خلاصه متا تگ‌ها

| تگ              | یافت شد | مقدار نمونه                               | اهمیت       |
|-----------------|----------|-------------------------------------------|--------------|
| Title           | بله      | "صفحه آزمایشی من - تحلیل سئو"             | بسیار زیاد  |
| Meta Description| بله      | "یک توضیح کوتاه اما شیرین..."             | زیاد         |
| Meta Robots     | خیر     | N/A                                       | متوسط       |
| Canonical URL   | بله      | https://example.com/test-page             | بسیار زیاد  |
| Viewport        | بله      | width=device-width, initial-scale=1.0     | زیاد        |
| Charset         | بله      | UTF-8                                     | زیاد         |
| HTML Language   | بله      | fa-IR                                     | متوسط       |

---

### ۲. بررسی اجمالی تگ‌های عناوین (Headings)

| تگ    | تعداد | مورد انتظار | وضعیت          | نکات                                   |
|-------|--------|-------------|----------------|----------------------------------------|
| H1    | ۱      | ۱           | خوب (Good)     | تعداد عالی برای عنوان اصلی             |
| H2    | ۱      | ≥ ۰         | خوب (Good)     | تعداد مناسب برای زیرعنوان‌ها           |
| H3-H6 | ۰      | ≥ ۰         | خوب (Good)     | مشکلی وجود ندارد                        |

---

### ۳. معیارهای کیفیت محتوا

| معیار              | مقدار          | محدوده پیشنهادی         | وضعیت        |
|--------------------|----------------|-------------------------|---------------|
| طول متن            | ۱۸۰ کلمه        | > ۳۰۰ کلمه ترجیح داده می‌شود| هشدار (Warning)|
| نسبت متن به HTML   | ۴۵٪            | > ۲۵٪                   | خوب (Good)    |
| شاخص خوانایی Flesch| ۶۰.۰           | ۵۰-۷0 (آسان برای خواندن) | خوب (Good)    |
| محتوای ضعیف        | خیر            | خیر                      | خوب (Good)    |
| چگالی کلمه کلیدی   | ۱.۵٪ (برای "کلمه کلیدی") | ۱-۳٪ بهینه             | خوب (Good)    |

---

### ۴. خلاصه سئو تصاویر

| بررسی             | تعداد یافته‌شده | تعداد موفق | وضعیت          |
|-------------------|----------------|-------------|----------------|
| تصاویر با Alt     | ۲              | ۱           | هشدار (Warning)|
| تصاویر بدون Alt   | ۱              | N/A         | نیازمند اصلاح  |

---

### ۵. تحلیل لینک‌ها

| نوع            | تعداد | نکات                                     |
|----------------|--------|------------------------------------------|
| لینک‌های داخلی | ۱      | ساختار لینک‌دهی داخلی مناسب             |
| لینک‌های خارجی | ۱      | یک لینک با nofollow (برای سئو مناسب است) |
| ویژگی Nofollow | ۱      | استفاده صحیح از ویژگی nofollow          |
| Sponsored/UGC  | ۰      | لینک sponsored یا UGC یافت نشد          |

---

### ۶. تگ‌های شبکه‌های اجتماعی

| نوع تگ      | یافت شد | وضعیت       |
|--------------|----------|--------------|
| Open Graph   | بله      | خوب (Good)  |
| Twitter Card | بله      | خوب (Good)  |

---

### ۷. انواع داده‌های ساختاریافته

| نوع           | یافت شد | نکات                                   |
|----------------|----------|----------------------------------------|
| JSON-LD        | بله      | Schema.org نوع WebPage یافت شد          |
| Microdata      | خیر      |                                        |
| RDFa           | خیر      |                                        |

---

## 📚 منابع و مراجع

- [راهنمای شروع سئو گوگل](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [مبانی سئو در شبکه توسعه‌دهندگان موزیلا (MDN)](https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Cross_browser_testing/SEO)
- [داده‌های ساختاریافته Schema.org](https://schema.org/docs/gs.html)

---

## 📝 مجوز (License)

Seokar تحت مجوز MIT منتشر شده است. برای جزئیات بیشتر به فایل [LICENSE](./LICENSE) (در صورت وجود در ریشه پروژه) مراجعه کنید.

---

## 📬 تماس و پشتیبانی

برای گزارش مشکلات، ارائه پیشنهادات یا مشارکت، لطفاً یک Issue یا Pull Request در [مخزن GitHub](https://github.com/yourusername/seokar) (آدرس مخزن خود را جایگزین کنید) ایجاد نمایید.

از اینکه از Seokar استفاده می‌کنید سپاسگزاریم!  
موفق باشید در تحلیل‌های سئو!
