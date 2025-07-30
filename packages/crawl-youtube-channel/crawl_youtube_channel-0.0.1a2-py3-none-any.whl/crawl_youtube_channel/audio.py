import os
import tempfile

import yt_dlp


async def url_to_m4a_bytes(video_url: str):
    import crawl_youtube_channel.util
    return crawl_youtube_channel.util.Audio.from_bytes(await crawl_youtube_channel.util.youtube_to_media_bytes(video_url, 'bestaudio[ext=m4a]/bestaudio'))
    with tempfile.NamedTemporaryFile() as tmp:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
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





