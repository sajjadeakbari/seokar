# seokar/analyzer.py

from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any

class Seokar:
    """
    Analyzes HTML content for various on-page SEO elements.
    """
    def __init__(self, html_content: str, url: Optional[str] = None):
        """
        Initializes the Seokar analyzer.

        :param html_content: The HTML content string to analyze.
        :param url: The original URL of the HTML content (optional).
        """
        if not isinstance(html_content, str):
            raise TypeError("html_content must be a string.")
        self.html_content = html_content
        self.url = url
        self.soup = BeautifulSoup(self.html_content, 'html.parser')

    def _get_tag_content(self, tag_name: str, attribute: Optional[str] = None, attr_value: Optional[str] = None) -> Optional[str]:
        """Helper to get content of a specific tag."""
        tag = None
        if attribute and attr_value:
            tag = self.soup.find(tag_name, {attribute: attr_value})
        elif tag_name == 'title': # title tag doesn't have attributes like name/property for selection
            tag = self.soup.find(tag_name)
        
        if tag:
            if tag_name == 'link' and 'href' in tag.attrs: # for canonical
                 return tag.attrs.get('href', '').strip()
            if 'content' in tag.attrs:
                return tag.attrs.get('content', '').strip()
            return tag.string.strip() if tag.string else ''
        return None

    def _get_all_meta_tags_by_prefix(self, prefix_attr: str, prefix_value: str) -> Dict[str, str]:
        """Helper to get all meta tags with a specific attribute prefix (e.g., property="og:" or name="twitter:")."""
        tags = {}
        for tag in self.soup.find_all('meta'):
            attr_val = tag.get(prefix_attr)
            if attr_val and attr_val.startswith(prefix_value):
                content = tag.get('content')
                if content: # Only add if content exists
                    tags[attr_val] = content.strip()
        return tags
        
    def _get_heading_texts(self, heading_level: str) -> List[str]:
        """Helper to get text content of specified heading level tags."""
        return [h.get_text(strip=True) for h in self.soup.find_all(heading_level) if h.get_text(strip=True)]

    # --- Title ---
    def get_title(self) -> Optional[str]:
        """Returns the content of the <title> tag."""
        return self._get_tag_content('title')

    def get_title_length(self) -> int:
        """Returns the character length of the title."""
        title = self.get_title()
        return len(title) if title else 0

    # --- Meta Description ---
    def get_meta_description(self) -> Optional[str]:
        """Returns content of the <meta name="description"> tag."""
        return self._get_tag_content('meta', 'name', 'description')

    def get_meta_description_length(self) -> int:
        """Returns character length of the meta description."""
        desc = self.get_meta_description()
        return len(desc) if desc else 0

    # --- Meta Robots ---
    def get_meta_robots(self) -> List[str]:
        """Returns content of the <meta name="robots"> tag as a list of directives."""
        robots_content = self._get_tag_content('meta', 'name', 'robots')
        if robots_content:
            return [directive.strip().lower() for directive in robots_content.split(',') if directive.strip()]
        return []

    # --- Canonical URL ---
    def get_canonical_url(self) -> Optional[str]:
        """Returns the URL specified in the <link rel="canonical"> tag."""
        return self._get_tag_content('link', 'rel', 'canonical')

    # --- Open Graph ---
    def get_open_graph_tags(self) -> Dict[str, str]:
        """Returns a dictionary of all Open Graph tags (e.g. og:title, og:image)."""
        return self._get_all_meta_tags_by_prefix('property', 'og:')

    # --- Twitter Cards ---
    def get_twitter_card_tags(self) -> Dict[str, str]:
        """Returns a dictionary of all Twitter Card tags (e.g. twitter:card, twitter:title)."""
        return self._get_all_meta_tags_by_prefix('name', 'twitter:')

    # --- Headings ---
    def get_h1_tags(self) -> List[str]:
        """Returns a list of text content from all <h1> tags."""
        return self._get_heading_texts('h1')

    def get_h2_tags(self) -> List[str]:
        """Returns a list of text content from all <h2> tags."""
        return self._get_heading_texts('h2')

    def get_h3_tags(self) -> List[str]:
        """Returns a list of text content from all <h3> tags."""
        return self._get_heading_texts('h3')

    def get_h4_tags(self) -> List[str]:
        """Returns a list of text content from all <h4> tags."""
        return self._get_heading_texts('h4')

    def get_h5_tags(self) -> List[str]:
        """Returns a list of text content from all <h5> tags."""
        return self._get_heading_texts('h5')

    def get_h6_tags(self) -> List[str]:
        """Returns a list of text content from all <h6> tags."""
        return self._get_heading_texts('h6')

    def get_all_heading_tags(self) -> Dict[str, List[str]]:
        """Returns a dictionary where keys are heading tag names (e.g., 'h1') 
           and values are lists of their text content.
           Only includes heading levels that are present in the document.
        """
        all_headings = {}
        for i in range(1, 7):
            tag_name = f"h{i}"
            headings = self._get_heading_texts(tag_name)
            if headings: # Only add if there are headings of this level
                all_headings[tag_name] = headings
        return all_headings

    def get_all_seo_data(self) -> Dict[str, Any]:
        """
        Returns a dictionary containing all extracted SEO data.
        """
        return {
            "title": self.get_title(),
            "title_length": self.get_title_length(),
            "meta_description": self.get_meta_description(),
            "meta_description_length": self.get_meta_description_length(),
            "meta_robots": self.get_meta_robots(),
            "canonical_url": self.get_canonical_url(),
            "open_graph_tags": self.get_open_graph_tags(),
            "twitter_card_tags": self.get_twitter_card_tags(),
            "headings": self.get_all_heading_tags()
            # "h1_tags": self.get_h1_tags(), # Redundant if using "headings"
            # ... could add individual hX here if desired, but get_all_heading_tags is more comprehensive
        }
