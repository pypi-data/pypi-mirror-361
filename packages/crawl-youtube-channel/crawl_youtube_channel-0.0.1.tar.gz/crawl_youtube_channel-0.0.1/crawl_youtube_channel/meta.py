import time
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

import youtube.util


async def get_youtube_meta(video_url) -> youtube.util.Meta:
    
    video_id = youtube.util.extract_video_id(video_url)
    
    # Get metadata via API
    youtube_api = build('youtube', 'v3', developerKey=youtube.util.API_KEY)
    meta = youtube_api.videos().list(part='snippet,statistics', id=video_id).execute()

    return youtube.util.Meta.from_dict(meta)

