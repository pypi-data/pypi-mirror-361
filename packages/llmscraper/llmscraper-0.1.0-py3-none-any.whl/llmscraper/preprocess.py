import base64
from typing import Literal, Union, Callable, Awaitable, TypedDict
from playwright.async_api import Page
import html2text

from .cleanup import cleanup_html, get_text_from_html

CLEANUP_JS = """
(() => {
})();
"""

class PreProcessOptionsBase(TypedDict, total=False):
    format: Literal['html', 'text', 'markdown', 'raw_html']

class PreProcessOptionsImage(TypedDict):
    format: Literal['image']
    full_page: bool

class PreProcessOptionsCustom(TypedDict):
    format: Literal['custom']
    format_function: Callable[[Page], Union[str, Awaitable[str]]]

PreProcessOptions = Union[PreProcessOptionsBase, PreProcessOptionsImage, PreProcessOptionsCustom]

class PreProcessResult(TypedDict):
    url: str
    content: str
    format: str

async def preprocess(page: Page, options: PreProcessOptions = None) -> PreProcessResult:
    if options is None:
        options = {'format': 'html'}

    url = page.url
    content = ""
    format_type = options.get('format', 'html')

    if format_type == 'raw_html':
        content = await page.content()
    
    elif format_type == 'markdown':
        body = await page.content()
        h = html2text.HTML2Text()
        content = h.handle(body)

    elif format_type == 'text':
        body = await page.content()
        # Using BeautifulSoup for text extraction as it's generally better for plain text
        content = get_text_from_html(body)

    elif format_type == 'html':
        await page.evaluate(CLEANUP_JS)
        content = await page.content()

    elif format_type == 'image':
        full_page = options.get('full_page', False)
        image_bytes = await page.screenshot(full_page=full_page)
        content = base64.b64encode(image_bytes).decode('utf-8')

    elif format_type == 'custom':
        format_function = options.get('format_function')
        if not format_function or not callable(format_function):
            raise ValueError('format_function must be provided in custom mode')
        
        result = format_function(page)
        if isinstance(result, Awaitable):
            content = await result
        else:
            content = result

    return {
        'url': url,
        'content': content,
        'format': format_type,
    }
