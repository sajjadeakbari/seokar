import sys

def welcome_message():
    """
    Displays a welcome message and initial setup instructions for Seokar.
    This function is intended to be called via a console script.
    """
    # ANSI escape codes for colors
    COLOR_BLUE = "\033[94m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_RESET = "\033[0m"
    COLOR_BOLD = "\033[1m"
    COLOR_UNDERLINE = "\033[4m"

    message = f"""
{COLOR_BOLD}{COLOR_GREEN}====================================================={COLOR_RESET}
{COLOR_BOLD}{COLOR_BLUE}    _.-=-._ _.-=-._  {COLOR_YELLOW}Welcome to Seokar!{COLOR_BLUE}  _.-=-._ _.-=-._    {COLOR_RESET}
{COLOR_BOLD}{COLOR_GREEN}====================================================={COLOR_RESET}

{COLOR_BOLD}🎉 Seokar has been successfully installed! 🎉{COLOR_RESET}

Seokar is your powerful, world-class library for in-depth SEO analysis.
Get ready to uncover deep insights into web page performance, content quality,
technical health, and security.

{COLOR_BOLD}{COLOR_YELLOW}✨ Before you dive in, a quick but important step:{COLOR_RESET}
   Seokar utilizes NLTK for advanced text analysis (e.g., readability, keyword density).
   Please download the necessary 'punkt' data by running the following command:

   {COLOR_BLUE}{COLOR_UNDERLINE}python -m nltk.downloader punkt{COLOR_RESET}

{COLOR_BOLD}{COLOR_YELLOW}🚀 Quick Start Example:{COLOR_RESET}
   Here's how you can perform your first SEO analysis:

   {COLOR_BLUE}from seokar.analyzer import SeokarAnalyzer

   analyzer = SeokarAnalyzer(url="https://example.com")
   result = analyzer.analyze()

   print(result.to_markdown()) # For a human-readable report
   # print(result.to_dict())   # For structured data (e.g., JSON){COLOR_RESET}

{COLOR_BOLD}{COLOR_YELLOW}🌐 Explore more:{COLOR_RESET}
   Visit our official website for comprehensive documentation, advanced usage,
   and community support: {COLOR_UNDERLINE}https://sajjadakbari.ir{COLOR_RESET}

{COLOR_BOLD}{COLOR_GREEN}====================================================={COLOR_RESET}
"""
    print(message)
    sys.exit(0) # Exit cleanly after printing the message

if __name__ == "__main__":
    welcome_message()
