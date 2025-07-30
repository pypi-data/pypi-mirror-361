import os
import json
import time
import sqlite3
import asyncio
import datetime
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv('.env')

from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import (
    JsonCssExtractionStrategy,
    LLMExtractionStrategy,
)

import buelon

# from pydantic.dataclasses import dataclass

import crawl_youtube_channel.util


def upload_row(table: list[dict]):
    db = buelon.helpers.postgres.get_postgres_from_env()

    db.upload_table('amazon_ads_api_docs', table, id_column=['url', 'success'])


def store_bytes(key: str, value: bytes, data_type: str):
    if not isinstance(key, str) or not isinstance(value, bytes):
        raise ValueError(f'`key` must be str and `value` must be bytes')
    
    db = buelon.helpers.postgres.get_postgres_from_env()
    db.upload_table('amazon_ads_api_docs_data', [{'key': key, 'value': value, 'data_type': data_type}], id_column=['key'])


async def download_media_with_crawler(crawler, media_url, wait_time: int | float | None = None):
    """Download media using the same browser session as the crawler"""
    if isinstance(wait_time, (float, int)):
        await asyncio.sleep(wait_time)

    browser_manager = crawler.crawler_strategy.browser_manager
    
    # Get the browser and create a new context
    browser = browser_manager.browser
    context = await browser.new_context()
    
    # Make the request
    response = await context.request.get(media_url)
    
    if response.ok:
        return await response.body()
    else:
        raise Exception(f"Failed to download media: {response.status}")


async def result_to_row_and_links(crawler, result):
    if result.success:
        print(f"Successfully crawled: {result.url}")
        print(f"Title: {result.metadata.get('title', 'N/A')}")
        print(f"Word count: {len(result.markdown.split())}")
        print(f"Number of links: {len(result.links.get('internal', [])) + len(result.links.get('external', []))}")
        print(f"Number of images: {len(result.media.get('images', []))}")
        print("---")

        if isinstance(result.media, dict):
            for k, v in result.media.items():
                if isinstance(k, str) and isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict) and isinstance(item.get('src'), str):
                            try:
                                data = await download_media_with_crawler(crawler, item['src'], 0.1)
                                if isinstance(data, bytes):
                                    store_bytes(item['src'], data, k)
                            except: pass
        
        return {
            'success': bool(result.success),
            'url': f'{result.url}',
            'title': f"{result.metadata.get('title', 'N/A')}",
            'markdown': f'{result.markdown}',
            'word_count': len(f'{result.markdown}'.split()),
            'internal_links': json.dumps(result.links.get('internal', [])),
            'external_links': json.dumps(result.links.get('external', [])),
            'media': json.dumps(result.media),
            'error': None,
            'updated': datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc)
        }, result.links.get('internal', []), result.links.get('external', []), 
    else:
        print(f"Failed to crawl: {result.url}")
        print(f"Error: {result.error_message}")
        print("---")
        return {
            'success': bool(result.success),
            'url': None,
            'title': None,
            'markdown': None,
            'word_count': 0,
            'internal_links': '[]',
            'external_links': '[]',
            'media': '{"images": [], "videos": [], "audios": []}',
            'error': f"{result.error_message}",
            'updated': datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc)
        }, [], []


def section_to_obj(section: list[str]):
    if len(section) != 5:
        print(f'not 5 but {len(section)}')
        return None
    
    try:
        image_etc = section[0]
        image_url = image_etc.replace('[ ![](', '').split(')')[0].strip()

        title_and_url = section[1]
        s = title_and_url.replace('### [', '').split('](')
        title = s[0].strip()
        url = s[1].split('"')[0].strip()

        views_and_time = section[-1]
        views = views_and_time.split('views')[0].strip()
        time_tag = views_and_time.split('views')[1].strip()

        return crawl_youtube_channel.util.YouTubeThumbnail(
            # image=image_url,
            id=crawl_youtube_channel.util.extract_video_id(url),
            title=title,
            url=url,
            # views=views,
            # time=time_tag,
        )
    except Exception as e:
        print('e', e)
        return None 


def markdown_to_objs(markdown: str) -> list[crawl_youtube_channel.util.YouTubeThumbnail]:
    sections = []
    current_section = []
    last_line = ''

    for line in markdown.splitlines():
        current_section.append(line)

        if '•' in last_line and 'views' in line:
            sections.append(current_section)
            current_section = []
            
        last_line = line
    
    res = {}

    for section in sections:
        ytt = section_to_obj(section)

        if ytt:
            res[ytt.url] = ytt
    
    return list(res.values())


async def aget_channel_videos(channel_url='https://www.youtube.com/@Junglr/videos'):
    browser_config = BrowserConfig(
        verbose=True,
    )
    crawler_config = CrawlerRunConfig(
        scan_full_page=True,
        delay_before_return_html=5.0,
        scroll_delay=2.0,
        cache_mode=CacheMode.BYPASS,
        session_id='session_123',
        css_selector='.style-scope.ytd-rich-item-renderer'
    )

    # Initialize the AsyncWebCrawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=channel_url,
            config=crawler_config,
        )
        
        obj = markdown_to_objs(result.markdown)
    
    return obj


def channel_thumbnail_extraction_strategy():
    schema = {
        "name": "KidoCode Courses",
        "baseSelector": ".style-scope.ytd-rich-item-renderer",
        "fields": [
            {
                "name": "title",
                "selector": "a.yt-simple-endpoint.focus-on-expand.style-scope.ytd-rich-grid-media",
                "type": "text",
            },
            {
                "name": "url",
                "selector": "a.yt-simple-endpoint.focus-on-expand.style-scope.ytd-rich-grid-media",
                "type": "attribute",
                "attribute": "href",
            },
            # {  ## images are dynamically shown, so it will not load all images at once. e.i. you can't pull images normally
            #     "name": "image",
            #     "selector": "ytd-thumbnail a img.yt-core-image, yt-image img, img[src*='ytimg.com']",  # "img.yt-core-image",  # yt-core-image.yt-core-image--fill-parent-height.yt-core-image--fill-parent-width.yt-core-image--content-mode-scale-aspect-fill.yt-core-image--loaded
            #     "type": "attribute",
            #     "attribute": "src",
            # },
        ],
    }

    return JsonCssExtractionStrategy(schema)


async def aget_channel_videos_v2(channel_url='https://www.youtube.com/@Junglr/videos'):
    browser_config = BrowserConfig(
        verbose=True,
        # headless=False,
    )
    crawler_config = CrawlerRunConfig(
        # word_count_threshold=0,
        scan_full_page=True,
        delay_before_return_html=5.0,
        scroll_delay=2.0,
        cache_mode=CacheMode.BYPASS,
        session_id='session_123',
        # css_selector='.style-scope.ytd-rich-item-renderer',
        extraction_strategy=channel_thumbnail_extraction_strategy(),
        wait_for_images=True,
        # simulate_user=True,
        # wait_for='js:() => {'
        #      '  const items = document.querySelectorAll(".style-scope.ytd-rich-item-renderer");'
        #      '  if (items.length === 0) return false;'
        #      '  return Array.from(items).every(item => item.querySelector("img.yt-core-image"));'
        #      '}',#"js:() => window.loaded === true"
        # page_timeout=60000 * 5,
    )

    # Initialize the AsyncWebCrawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=channel_url,
            config=crawler_config,
        )

        # return result
        thumbnails = {}  # []
        
        for data in json.loads(result.extracted_content):
            t = crawl_youtube_channel.util.YouTubeThumbnail(
                **data,
                id=crawl_youtube_channel.util.extract_video_id(data['url']),
                # views='',
                # time='',
            )
            if t.url.startswith('/'):
                t.url = f'https://www.youtube.com{t.url}'
            thumbnails[t.id] = t  # .append(t)
        
        return list(thumbnails.values())


def get_channel_videos_v2(channel_url='https://www.youtube.com/@Junglr/videos'):
    return asyncio.run(aget_channel_videos_v2(channel_url))

def get_channel_videos(channel_url='https://www.youtube.com/@Junglr/videos'):
    return asyncio.run(aget_channel_videos(channel_url))


if __name__ == '__main__':
    get_channel_videos()

