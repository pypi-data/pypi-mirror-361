from typing import List, Type, TypeVar, Optional, TypedDict, Literal, Any, Iterable
import instructor
from pydantic import BaseModel

from .preprocess import PreProcessResult

T = TypeVar("T", bound=BaseModel)

DEFAULT_PROMPT = 'You are a sophisticated web scraper. Extract the contents of the webpage'
DEFAULT_CODE_PROMPT = "Provide a scraping function in JavaScript that extracts and returns data according to a schema from the current page. The function must be an IIFE. No comments or imports. No console.log. The code you generate will be executed straight away, you shouldn't output anything besides runnable code."

class ScraperLLMOptions(TypedDict, total=False):
    model: str
    prompt: str
    temperature: float
    max_tokens: int
    top_p: float
    mode: Literal['auto', 'json', 'tool']
    output: Literal['object', 'array']

class ScraperGenerateOptions(TypedDict, total=False):
    model: str
    prompt: str
    temperature: float
    max_tokens: int
    top_p: float

def strip_markdown_backticks(text: str) -> str:
    return text.strip().replace("```javascript", "").replace("```", "").strip()

def prepare_user_content(page: PreProcessResult):
    if page['format'] == 'image':
        return [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{page['content']}"}}
        ]
    return page['content']

async def generate_completions(
    client: Any,
    page: PreProcessResult,
    schema: Type[T],
    options: Optional[ScraperLLMOptions] = None,
) -> dict:
    if options is None:
        options = {}
    
    user_content = prepare_user_content(page)
    prompt = options.get('prompt', DEFAULT_PROMPT)

    if isinstance(user_content, list):
        # Multimodal case for images
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}] + user_content,
            }
        ]
    else:
        # Text-only case
        messages = [
            {
                "role": "user",
                "content": f"{prompt}\n\n{user_content}",
            }
        ]
    params = {
        'response_model':schema,
        'messages':messages,
    }
    if 'model' in options:
        params['model'] = options.get("model")
    if 'temperature' in options:
        params['temperature'] = options.get('temperature')
    if 'max_tokens' in options:
        params['max_tokens'] = options.get('max_tokens')

    response = await client.chat.completions.create(
        **params
    )
    
    return {
        'data': response,
        'url': page['url'],
    }

async def stream_completions(
    client: Any,
    page: PreProcessResult,
    schema: Type[T],
    options: Optional[ScraperLLMOptions] = None,
):
    if options is None:
        options = {}

    user_content = prepare_user_content(page)
    prompt = options.get('prompt', DEFAULT_PROMPT)

    if isinstance(user_content, list):
        # Multimodal case for images
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}] + user_content,
            }
        ]
    else:
        # Text-only case
        messages = [
            {
                "role": "user",
                "content": f"{prompt}\n\n{user_content}",
            }
        ]

    params = {
        'messages':messages,
        'stream': True,
    }
    if options.get("output") == "array":
        params['response_model'] = Iterable[schema]
    else:
        params['response_model'] = instructor.Partial[schema]

    if 'model' in options:
        params['model'] = options.get("model")
    if 'temperature' in options:
        params['temperature'] = options.get('temperature')
    if 'max_tokens' in options:
        params['max_tokens'] = options.get('max_tokens')

    stream = client.chat.completions.create(
        **params
    )
    
    return {
        'stream': stream,
        'url': page['url'],
    }

async def generate_code(
    client: Any,
    page: PreProcessResult,
    schema: Type[T],
    options: Optional[ScraperGenerateOptions] = None,
) -> dict:
    if options is None:
        options = {}

    user_content = f"Website: {page['url']}\nSchema: {schema.model_json_schema()}\nContent: {page['content']}"
    messages=[
        {"role": "system", "content": options.get('prompt', DEFAULT_CODE_PROMPT)},
        {"role": "user", "content": user_content},
    ]
    params = {
        'messages':messages,
    }
    if 'model' in options:
        params['model'] = options.get("model")
    if 'temperature' in options:
        params['temperature'] = options.get('temperature')
    if 'max_tokens' in options:
        params['max_tokens'] = options.get('max_tokens')

    response = await client.chat.completions.create(
        **params
    )
    
    code = strip_markdown_backticks(response.choices[0].message.content)
    
    return {
        'code': code,
        'url': page['url'],
    }
