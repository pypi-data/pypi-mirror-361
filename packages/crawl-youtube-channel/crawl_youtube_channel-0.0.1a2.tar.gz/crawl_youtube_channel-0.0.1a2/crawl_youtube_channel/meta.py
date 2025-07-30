import time
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

import crawl_youtube_channel.util


async def get_youtube_meta(video_url) -> crawl_youtube_channel.util.Meta:
    
    video_id = crawl_youtube_channel.util.extract_video_id(video_url)
    
    # Get metadata via API
    youtube_api = build('youtube', 'v3', developerKey=crawl_youtube_channel.util.API_KEY)
    meta = youtube_api.videos().list(part='snippet,statistics', id=video_id).execute()

    return crawl_youtube_channel.util.Meta.from_dict(meta)

