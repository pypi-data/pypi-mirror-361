import asyncio
import json
import os
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field, create_model
from typing import List, Any, Optional
from openai import AsyncOpenAI
import instructor
from llmscraper import LLMScraper


def model_from_json(json_str: str, name: str = "DynamicModel") -> type[BaseModel]:
    """
    Build a pydantic model from a (very small subset of) JSON-Schema.
    Currently supports:
      - type: object / array / string / number / integer / boolean
      - required
    Nested objects & arrays are handled recursively.
    """
    schema: dict[str, Any] = json.loads(json_str)

    def build(schema_dict: dict[str, Any], model_name: str) -> Any:
        t = schema_dict.get("type")

        # primitives ---------------------------------------------------------
        if t == "string":
            return str
        if t == "number":
            return float
        if t == "integer":
            return int
        if t == "boolean":
            return bool

        # array --------------------------------------------------------------
        if t == "array":
            item_schema = schema_dict.get("items", {})
            return List[build(item_schema, f"{model_name}Item")]

        # object -------------------------------------------------------------
        if t == "object":
            props = schema_dict.get("properties", {})
            required = set(schema_dict.get("required", []))

            fields: dict[str, tuple[Any, Any]] = {}
            for prop_name, prop_schema in props.items():
                field_type = build(prop_schema, f"{model_name}_{prop_name.capitalize()}")
                default = ... if prop_name in required else None
                fields[prop_name] = (field_type, default)

            return create_model(model_name, **fields)  # type: ignore

        # fallback -----------------------------------------------------------
        return Any

    return build(schema, name)

# 1. Define the scraper tool
class ScrapeWebsite(instructor.OpenAISchema):
    """Scrape a website with a given schema and URL"""
    url: str = Field(..., description="The URL of the website to scrape")
    json_schema: str = Field(..., description="The JSON schema to extract data into")

    async def execute(self):
        # Convert JSON schema string back to a Pydantic model
        #schema_dict = json.loads(self.json_schema)
        DynamicModel = model_from_json(self.json_schema)

        client = instructor.from_openai(AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY")))
        scraper = LLMScraper(client)

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(self.url)
            
            result = await scraper.run(page, DynamicModel, {"model": "gpt-4o", "format": "html"})
            
            await browser.close()
            return result['data'].model_dump()

# 2. Define the schema for the data we want from the website
class Story(BaseModel):
    title: str
    summary: str

class TopStories(BaseModel):
    stories: List[Story]

# 3. Run the tool-using model
async def main():
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": "List top 2 stories from news.ycombinator.com and summarize them.",
            }
        ],
        functions=[ScrapeWebsite.openai_schema],
    )
    func_call = response.choices[0].message.function_call
    func = ScrapeWebsite.model_validate_json(func_call.arguments)
    result = await func.execute()

    print("\n--- Final Result ---")
    print(json.dumps(result, indent=2))
    print("--------------------")

if __name__ == "__main__":
    asyncio.run(main())
