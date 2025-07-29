import asyncio
from playwright.async_api import async_playwright
import instructor
from pydantic import BaseModel
from openai import AsyncOpenAI
from llmscraper import LLMScraper

class Story(BaseModel):
    title: str
    points: int
    by: str
    comments_url: str

async def main():
    client = instructor.from_openai(AsyncOpenAI())
    scraper = LLMScraper(client)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://news.ycombinator.com")

        result = await scraper.stream(page, Story, {"format": "html","model": "gpt-4o", "temperature": 0.0})
        
        async for data in await result['stream']:
            print(data.model_dump())

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
