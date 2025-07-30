import asyncio
import time

from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

import crawl_youtube_channel.util


async def get_youtube_comments(video_url, raw: bool = False) -> list[crawl_youtube_channel.util.Comment] | list[dict]:
    video_id = crawl_youtube_channel.util.extract_video_id(video_url)
    
    # Get comments
    youtube_api = build('youtube', 'v3', developerKey=crawl_youtube_channel.util.API_KEY)

    comments = []
    comments_response = youtube_api.commentThreads().list(part='id,snippet,replies', videoId=video_id, maxResults=100).execute()
    comments += comments_response['items']

    while comments_response.get('nextPageToken'):
        await asyncio.sleep(0.1)
        comments_response = youtube_api.commentThreads().list(part='id,snippet,replies', videoId=video_id, maxResults=100, pageToken=comments_response['nextPageToken']).execute()
        comments += comments_response['items']
    
    if raw:
        return comments
    
    return [crawl_youtube_channel.util.Comment.from_dict(c) for c in comments]
