from typing import Type, TypeVar, Any
from playwright.async_api import Page
from pydantic import BaseModel

from .preprocess import preprocess, PreProcessOptions
from .models import (
    generate_completions, 
    stream_completions, 
    generate_code,
    ScraperLLMOptions,
    ScraperGenerateOptions
)

T = TypeVar("T", bound=BaseModel)

class LLMScraper:
    def __init__(self, client: Any):
        self.client = client

    async def run(
        self,
        page: Page,
        schema: Type[T],
        options: PreProcessOptions = None,
    ) -> dict:
        # The `options` dictionary can contain both preprocessing and LLM-specific
        # parameters. This line filters the dictionary to create `llm_opts`,
        # which includes only the keys defined in the `ScraperLLMOptions`
        # TypedDict. `__annotations__` is used to get the set of valid keys
        # from the TypedDict for this filtering.
        llm_opts: ScraperLLMOptions = {k: v for k, v in options.items() if k in ScraperLLMOptions.__annotations__} if options else {}
        preprocessed = await preprocess(page, options)
        return await generate_completions(self.client, preprocessed, schema, llm_opts)

    async def stream(
        self,
        page: Page,
        schema: Type[T],
        options: PreProcessOptions = None,
    ):
        # The `options` dictionary can contain both preprocessing and LLM-specific
        # parameters. This line filters the dictionary to create `llm_opts`,
        # which includes only the keys defined in the `ScraperLLMOptions`
        # TypedDict. `__annotations__` is used to get the set of valid keys
        # from the TypedDict for this filtering.
        llm_opts: ScraperLLMOptions = {k: v for k, v in options.items() if k in ScraperLLMOptions.__annotations__} if options else {}
        preprocessed = await preprocess(page, options)
        return await stream_completions(self.client, preprocessed, schema, llm_opts)

    async def generate(
        self,
        page: Page,
        schema: Type[T],
        options: PreProcessOptions = None,
    ) -> dict:
        # The `options` dictionary can contain both preprocessing and LLM-specific
        # parameters. This line filters the dictionary to create `generate_opts`,
        # which includes only the keys defined in the `ScraperGenerateOptions`
        # TypedDict. `__annotations__` is used to get the set of valid keys
        # from the TypedDict for this filtering.
        generate_opts: ScraperGenerateOptions = {k: v for k, v in options.items() if k in ScraperGenerateOptions.__annotations__} if options else {}
        
        preprocessed = await preprocess(page, options)
        return await generate_code(self.client, preprocessed, schema, generate_opts)

__all__ = [
    "LLMScraper",
    "PreProcessOptions",
    "ScraperLLMOptions",
    "ScraperGenerateOptions"
]
