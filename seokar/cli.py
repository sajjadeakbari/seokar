#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Seokar Welcome Message Module

This module provides a visually appealing welcome message for the Seokar SEO analysis library.
It's designed to be executed as a console script upon successful installation.
"""

import sys
from typing import NoReturn


class ANSIColors:
    """Container for ANSI color codes used in terminal formatting"""
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def display_welcome_message() -> NoReturn:
    """
    Display a comprehensive welcome message for Seokar installation.
    
    This function prints a formatted message with:
    - Library introduction
    - Quick start example
    - Resource references
    - Visual separators and styling
    
    The function terminates the program with exit code 0 after display.
    """
    colors = ANSIColors()
    
    message_template = f"""
{colors.BOLD}{colors.GREEN}====================================================={colors.RESET}
{colors.BOLD}{colors.BLUE}    _.-=-._ _.-=-._  {colors.YELLOW}Welcome to Seokar!{colors.BLUE}  _.-=-._ _.-=-._    {colors.RESET}
{colors.BOLD}{colors.GREEN}====================================================={colors.RESET}

{colors.BOLD}🎉 Seokar has been successfully installed! 🎉{colors.RESET}

Seokar is your powerful, world-class library for in-depth SEO analysis.
Get ready to uncover deep insights into web page performance, content quality,
technical health, and security.

{colors.BOLD}{colors.YELLOW}🚀 Quick Start Example:{colors.RESET}
   Here's how you can perform your first SEO analysis:

   {colors.BLUE}from seokar.analyzer import SeokarAnalyzer

   analyzer = SeokarAnalyzer(url="https://example.com")
   result = analyzer.analyze()

   print(result.to_markdown()) # For a human-readable report
   # print(result.to_dict())   # For structured data (e.g., JSON){colors.RESET}

{colors.BOLD}{colors.YELLOW}🌐 Explore more:{colors.RESET}
   Visit our official website for comprehensive documentation, advanced usage,
   and community support: {colors.UNDERLINE}https://sajjadakbari.ir{colors.RESET}

{colors.BOLD}{colors.GREEN}====================================================={colors.RESET}
"""
    print(message_template)
    sys.exit(0)


def main() -> None:
    """Main entry point for the welcome message script"""
    display_welcome_message()


if __name__ == "__main__":
    main()
