from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build


async def get_youtube_transcript(video_url):
    import crawl_youtube_channel.util
    video_id = crawl_youtube_channel.util.extract_video_id(video_url)
    
    # Get transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except:
        transcript = None
    
    return crawl_youtube_channel.util.Transcript(
        parts=[crawl_youtube_channel.util.TranscriptPart(**{'index': i, **part}) for i, part in enumerate(transcript)]
    )

