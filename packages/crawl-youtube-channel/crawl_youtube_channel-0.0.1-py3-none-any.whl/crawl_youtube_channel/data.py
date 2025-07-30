import asyncio

import youtube.util


def get_youtube_data(video_url: str) -> youtube.util.YouTubeData:
    return asyncio.run(aget_youtube_data(video_url))


async def aget_youtube_data(video_url: str) -> youtube.util.YouTubeData:
    import youtube.meta
    import youtube.comments
    import youtube.transcript
    import youtube.audio
    import youtube.video

    return youtube.util.YouTubeData(
        audio=await youtube.audio.url_to_m4a_bytes(video_url),
        meta=await youtube.meta.get_youtube_meta(video_url),
        comments=await youtube.comments.get_youtube_comments(video_url),
        transcript=await youtube.transcript.get_youtube_transcript(video_url),
        video=await youtube.video.url_to_mp4_bytes(video_url),
    )


