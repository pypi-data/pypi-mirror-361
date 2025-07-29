import asyncio
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from llmscraper import LLMScraper

class Story(BaseModel):
    title: str
    points: int
    by: str
    comments_url: str

class HackerNews(BaseModel):
    top: list[Story] = Field(..., description="Top 5 stories on Hacker News", min_length=5, max_length=5)

async def main():
    client = AsyncOpenAI()
    scraper = LLMScraper(client)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://news.ycombinator.com")

        result = await scraper.generate(page, HackerNews, {"format": "raw_html","model": "gpt-4o", "temperature": 0.0})
        
        print("--- Generated Code ---")
        print(result['code'])
        print("----------------------")

        eval_result = await page.evaluate(result['code'])
        
        # Validate with Pydantic
        data = HackerNews.model_validate(eval_result)

        print("--- Parsed Result ---")
        print(data.model_dump_json(indent=2))
        print("---------------------")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
