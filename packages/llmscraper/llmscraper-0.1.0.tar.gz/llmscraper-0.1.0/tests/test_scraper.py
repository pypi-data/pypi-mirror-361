import pytest
import instructor
from pydantic import BaseModel, Field
from typing import List
from playwright.async_api import Page
from llmscraper import LLMScraper
from openai import AsyncOpenAI
import os

MODEL="gpt-4o-mini"  # Specify the model to use

# Pydantic models (equivalent to Zod schemas)
class Story(BaseModel):
    title: str
    points: int
    by: str
    commentsURL: str

class HackerNews(BaseModel):
    top: List[Story] = Field(
        ..., max_length=5, description="Top 5 stories on Hacker News"
    )

class ExamplePage(BaseModel):
    h1: str = Field(..., description="The main heading of the page")
    description: str = Field(..., description="The description text on the page")

class ExamplePageH1(BaseModel):
    h1: str = Field(..., description="The main heading of the page")


@pytest.fixture
def raw_scraper() -> LLMScraper:
    # Assumes OPENAI_API_KEY is set in the environment
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return LLMScraper(client)

# Fixtures
@pytest.fixture
def scraper() -> LLMScraper:
    # Assumes OPENAI_API_KEY is set in the environment
    client = instructor.from_openai(AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY")))
    return LLMScraper(client)


# Tests
@pytest.mark.asyncio(loop_scope="session")
async def test_scrape_example_text(page: Page, scraper: LLMScraper):
    await page.goto("https://example.com")
    result = await scraper.run(page, ExamplePage, {"format": "html","model": MODEL})
    assert result['data'].h1 == "Example Domain"
    assert "domain" in result['data'].description


@pytest.mark.asyncio(loop_scope="session")
async def test_scrape_hn_top_5(page: Page, scraper: LLMScraper):
    await page.goto("https://news.ycombinator.com")
    result = await scraper.run(page, HackerNews, {"model": MODEL})
    assert len(result['data'].top) == 5
    # Pydantic validation is implicit on model creation


@pytest.mark.asyncio(loop_scope="session")
async def test_scrape_hn_top_5_image(page: Page, scraper: LLMScraper):
    await page.goto("https://news.ycombinator.com")
    result = await scraper.run(page, HackerNews, {"format": "image","model": MODEL})
    assert len(result['data'].top) == 5


@pytest.mark.asyncio(loop_scope="session")
async def test_scrape_hn_top_5_markdown(page: Page, scraper: LLMScraper):
    await page.goto("https://news.ycombinator.com")
    result = await scraper.run(page, HackerNews, {"format": "markdown", "model": MODEL})
    assert len(result['data'].top) == 5


@pytest.mark.asyncio(loop_scope="session")
async def test_scrape_hn_top_5_raw_html(page: Page, scraper: LLMScraper):
    await page.goto("https://news.ycombinator.com")
    result = await scraper.run(page, HackerNews, {"format": "raw_html", "model": MODEL})
    assert len(result['data'].top) == 5

@pytest.mark.asyncio(loop_scope="session")
async def test_scrape_hn_code_generation(page: Page, raw_scraper: LLMScraper):
    await page.goto("https://news.ycombinator.com")
    result = await raw_scraper.generate(page, HackerNews, {"model": MODEL})
    code = result['code']
    result_data = await page.evaluate(code)
    result = HackerNews.model_validate(result_data)
    assert len(result.top) == 5


@pytest.mark.asyncio(loop_scope="session")
async def test_scrape_example_streaming(page: Page, scraper: LLMScraper):
    await page.goto("https://example.com")
    result = await scraper.stream(page, ExamplePageH1, {"model": MODEL})
    stream = result['stream']

    text = ""
    async for item in await stream:
        if item.h1:
            text = item.h1

    assert text == "Example Domain"


@pytest.mark.asyncio(loop_scope="session")
async def test_scrape_hn_streaming_array(page: Page, scraper: LLMScraper):
    await page.goto("https://news.ycombinator.com")
    result = await scraper.stream(page, Story, {"format": "raw_html", "output": "array", "model": MODEL})
    stream = result['stream']

    items = []
    async for item in await stream:
        items.append(item)
    assert len(items) == 30
    for item_data in items:
        Story.model_validate(item_data)
