import asyncio
import instructor
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field
from typing import List
from llmscraper import LLMScraper

class Story(BaseModel):
    title: str
    points: int
    by: str
    comments_url: str = Field(..., alias="commentsURL")

class HackerNews(BaseModel):
    top: List[Story] = Field(..., description="Top 5 stories on Hacker News", min_length=5, max_length=5)

async def main():
    client = instructor.from_provider("openai/gpt-4o-mini", async_client=True)
    scraper = LLMScraper(client)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://news.ycombinator.com")

        result = await scraper.run(page, HackerNews, {"format": "html"})
        
        for story in result['data'].top:
            print(story.model_dump_json(indent=2))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
