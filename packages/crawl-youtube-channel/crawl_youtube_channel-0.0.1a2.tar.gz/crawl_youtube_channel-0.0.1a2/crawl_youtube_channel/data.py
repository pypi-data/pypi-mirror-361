import asyncio

import crawl_youtube_channel.util


def get_youtube_data(video_url: str) -> crawl_youtube_channel.util.YouTubeData:
    return asyncio.run(aget_youtube_data(video_url))


async def aget_youtube_data(video_url: str) -> crawl_youtube_channel.util.YouTubeData:
    import crawl_youtube_channel.meta
    import crawl_youtube_channel.comments
    import crawl_youtube_channel.transcript
    import crawl_youtube_channel.audio
    import crawl_youtube_channel.video

    return crawl_youtube_channel.util.YouTubeData(
        audio=await crawl_youtube_channel.audio.url_to_m4a_bytes(video_url),
        meta=await crawl_youtube_channel.meta.get_youtube_meta(video_url),
        transcript=await crawl_youtube_channel.transcript.get_youtube_transcript(video_url),
        comments=await crawl_youtube_channel.comments.get_youtube_comments(video_url),
        video=await crawl_youtube_channel.video.url_to_mp4_bytes(video_url),
    )


