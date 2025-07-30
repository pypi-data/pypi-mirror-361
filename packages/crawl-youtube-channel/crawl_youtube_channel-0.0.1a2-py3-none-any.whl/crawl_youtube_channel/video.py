import os
import tempfile

import yt_dlp


async def url_to_mp4_bytes(video_url: str):
    import crawl_youtube_channel.util
    return crawl_youtube_channel.util.Video.from_bytes(await crawl_youtube_channel.util.youtube_to_media_bytes(video_url, 'best[ext=mp4]'))
    # ydl_opts = {'format': 'best'}
    # ydl_opts = {
    #     'format': 'best[ext=mp4]',  # Video format
    #     # 'writesubtitles': True,     # Download subtitles
    #     # 'writeautomaticsub': True,  # Auto-generated subtitles
    # }
    # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #     ydl.download([video_url])
    
    with tempfile.NamedTemporaryFile() as tmp:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': tmp.name,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # Read the file into bytes
        with open(tmp.name, 'rb') as f:
            data = f.read()
        
        # # Clean up
        # os.unlink(tmp.name)
        
        return data





