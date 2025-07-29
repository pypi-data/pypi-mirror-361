from bs4 import BeautifulSoup

def cleanup_html(html_content: str) -> str:
    """
    Cleans the HTML by removing unnecessary tags and attributes.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    elements_to_remove = [
        'script', 'style', 'noscript', 'iframe', 'svg', 'img', 'audio',
        'video', 'canvas', 'map', 'source', 'dialog', 'menu', 'menuitem',
        'track', 'object', 'embed', 'form', 'input', 'button', 'select',
        'textarea', 'label', 'option', 'optgroup', 'aside', 'footer',
        'header', 'nav', 'head'
    ]

    attributes_to_remove_prefixes = [
        'style', 'src', 'alt', 'title', 'role', 'tabindex', 'on', 'data-'
    ]
    
    # Using a set for faster lookups
    attributes_to_remove_prefixes_set = set(attributes_to_remove_prefixes)

    for element in soup.find_all(True):
        if element.name in elements_to_remove:
            element.decompose()
            continue

        attrs = dict(element.attrs)
        for attr_name in attrs:
            for prefix in attributes_to_remove_prefixes_set:
                if attr_name.startswith(prefix):
                    del element[attr_name]
                    break
    
    return str(soup)

def get_text_from_html(html_content: str) -> str:
    """
    Cleans HTML and extracts only the text content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    # You can also run cleanup_html first for more aggressive cleaning
    # cleaned_html = cleanup_html(html_content)
    # soup = BeautifulSoup(cleaned_html, 'html.parser')
    return soup.get_text(separator='\n', strip=True)
