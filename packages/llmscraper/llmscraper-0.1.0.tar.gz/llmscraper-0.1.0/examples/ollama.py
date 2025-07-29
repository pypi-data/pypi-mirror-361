import asyncio
import instructor
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from llmscraper import LLMScraper

MODEL="qwen2.5:3b"
# Point the OpenAI client to the Ollama server
client = instructor.from_openai(AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required, but unused
))

class ExamplePage(BaseModel):
    h1: str = Field(..., description="The main heading of the page")

async def main():
    # Initialize scraper with the Ollama client
    scraper = LLMScraper(client)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")

        result = await scraper.run(page, ExamplePage, {"format": "html", "model": MODEL})
        
        print(result['data'].model_dump_json(indent=2))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
