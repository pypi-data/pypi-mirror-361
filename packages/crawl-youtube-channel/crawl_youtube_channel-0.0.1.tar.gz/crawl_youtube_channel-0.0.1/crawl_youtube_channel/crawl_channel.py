import asyncio
import random
import sqlite3
from abc import ABC, abstractmethod

from youtube.channel import aget_channel_videos_v2
from youtube.util import YouTubeThumbnail, YouTubeData, YouTubeVideo
from youtube import aget_youtube_data


class YouTubeVideoProcessorBase(ABC):
    @abstractmethod
    async def check_video(self, video_id: str) -> None:
        pass

    @abstractmethod
    async def process_video(self, v: YouTubeVideo) -> None:
        pass

    async def wait_between_processes(self):
        # wait 5-15 minutes
        await asyncio.sleep(60.0 * (5.0 + (random.random() * 10.0)))

    async def process_channel(
        self, 
        channel_url: str = 'https://www.youtube.com/@Junglr/videos'
    ) -> None:
        thumbnails: list[YouTubeThumbnail] = await aget_channel_videos_v2(channel_url)

        for thumbnail in thumbnails:
            if not await self.check_video(thumbnail.id):
                data: YouTubeData = await aget_youtube_data(thumbnail.url)

                video = YouTubeVideo(
                    id=thumbnail.id,
                    thumbnail=thumbnail,
                    data=data,
                )

                await self.process_video(video)

                del video

                await self.wait_between_processes()


class Sqlite3YouTubeVideoProcessor(YouTubeVideoProcessorBase):
    def __init__(self, db_path: str = '.youtube_crawler_db'):
        super().__init__()
        self.db_path = db_path
        self.init()

    def init(self):
        conn = self.connect()

        # create kv store
        conn.execute('''
            CREATE TABLE IF NOT EXISTS kv (
                key TEXT PRIMARY KEY,
                value BLOB
            )
        ''')

        # index
        conn.execute('''
            CREATE INDEX IF NOT EXISTS kv_key_idx ON kv (key)
        ''')

    def connect(self):
        return sqlite3.connect(self.db_path)

    async def check_video(self, video_id: str) -> None:
        conn = self.connect()
        
        conn.execute('''
            SELECT * FROM kv WHERE key = ?
        ''', (video_id,))

        return bool(conn.fetchone())

    async def process_video(self, v: YouTubeVideo) -> None:
        conn = self.connect()

        conn.execute('''
            INSERT INTO kv (key, value) VALUES (?, ?)
        ''', (v.id, v.to_bytes()))
    
    async def get_video(self, video_id: str) -> YouTubeVideo:
        conn = self.connect()

        conn.execute('''
            SELECT value FROM kv WHERE key = ?
        ''', (video_id,))

        row = conn.fetchone()

        if row is None:
            return None

        return YouTubeVideo.from_bytes(row[0])

