from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build


async def get_youtube_transcript(video_url):
    import youtube.util
    video_id = youtube.util.extract_video_id(video_url)
    
    # Get transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except:
        transcript = None
    
    return youtube.util.Transcript(
        parts=[youtube.util.TranscriptPart(**{'index': i, **part}) for i, part in enumerate(transcript)]
    )

