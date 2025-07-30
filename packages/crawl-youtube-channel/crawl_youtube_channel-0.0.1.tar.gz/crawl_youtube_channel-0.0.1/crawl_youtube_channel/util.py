import os
import json
import gzip
import base64
import tempfile
from dataclasses import dataclass, asdict

import yt_dlp


API_KEY = os.environ['GOOGLE_CLOUD_YOUTUBE_API_KEY'] 


def extract_video_id(video_url: str):
    query = video_url.split('?')[-1]
    kvs = [tuple(kv.split('=')) for kv in query.split('&')]

    for k, v in kvs:
        if k == 'v':
            return v
    
    raise ValueError('Could not parse url to get video id')


def string_to_bytes(s: str) -> str:
    return gzip.decompress(base64.b64decode(s.encode('utf-8')))


def bytes_to_sting(b: bytes) -> str:
    return base64.b64encode(gzip.compress(b)).decode('utf-8')


@dataclass
class TranscriptPart:
    index: int
    text: str
    start: float
    duration: float


@dataclass
class Transcript:
    parts: list[TranscriptPart]


@dataclass
class Reply:
    id: str
    text: str
    author: str
    photo: str
    channel: str

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            id=obj['id'],
            text=obj.get('textDisplay'),
            author=obj.get('authorDisplayName'),
            photo=obj.get('authorProfileImageUrl'),
            channel=obj.get('authorChannelUrl')
        )


@dataclass
class Comment:
    id: str
    text: str
    author: float
    photo: float
    channel: str
    replies: list[Reply]

    @classmethod
    def from_dict(cls, obj: dict):
        comment = obj.get('snippet', {}).get('topLevelComment', {}).get('snippet', {})
        return cls(
            id=obj['id'],
            text=comment.get('textDisplay'),
            author=comment.get('authorDisplayName'),
            photo=comment.get('authorProfileImageUrl'),
            channel=comment.get('authorChannelUrl'),
            replies=[Reply.from_dict({**r.get('snippet', {}), 'id': r['id']}) for r in obj.get('replies', {}).get('comments', [])]
        )


@dataclass
class Meta:
    title: str
    description: str
    thumbnail_default: str
    thumbnail_high: str
    tags: list[str]

    views: str
    likes: str
    favorites: str
    comment_count: str

    @classmethod
    def from_dict(cls, obj: dict):
        if not obj.get('items', []):
            return
        item = obj['items'][0]
        statistics = item.get('statistics', {})
        meta = item.get('snippet', {})
        thumbnails = meta.get('thumbnails', {})
        return cls(
            title=meta.get('title'),
            description=meta.get('description'),
            thumbnail_default=thumbnails.get('default', {}).get('url'),
            thumbnail_high=thumbnails.get('high', {}).get('url'),
            tags=meta.get('tags'),

            views=statistics.get('viewCount'),
            likes=statistics.get('likeCount'),
            favorites=statistics.get('favoriteCount'),
            comment_count=statistics.get('commentCount'),
        )


@dataclass
class YouTubeData:
    meta: Meta
    comments: list[Comment]
    transcript: Transcript
    audio: bytes
    video: bytes


@dataclass
class YouTubeThumbnail:
    # image: str
    id: str
    title: str
    url: str
    # views: str
    # time: str


@dataclass
class YouTubeVideo:
    id: str
    thumbnail: YouTubeThumbnail
    data: YouTubeData

    def to_json(self, *args, **kwargs) -> str:
        return json.dumps({
            'id': self.id,
            'thumbnail': asdict(self.thumbnail),
            'data': {
                'meta': asdict(self.data.meta),
                'comments': [
                    asdict(c) for c in self.data.comments
                ],
                'transcript': asdict(self.data.transcript),
                'audio': bytes_to_sting(self.data.audio),
                'video': bytes_to_sting(self.data.video),
            }
        }, *args, **kwargs)
    
    @classmethod
    def from_json(cls, s: str) -> 'YouTubeVideo':
        obj = json.loads(s)
        data = obj['data']
        return YouTubeVideo(
            id=obj['id'],
            thumbnail=YouTubeThumbnail(**obj['thumbnail']),
            data=YouTubeData(
                meta=Meta(**data['meta']),
                comments=[Comment(**{**c, 'replies': [Reply(**r) for r in c['replies']]}) for c in data['comments']],
                transcript=Transcript(
                    parts=[TranscriptPart(**part) for part in data['transcript']['parts']] 
                ),
                audio=string_to_bytes(data['audio']),
                video=string_to_bytes(data['video']),
            )
        )
    
    def to_bytes(self):
        return self.to_json().encode('utf-8')
    
    @classmethod
    def from_bytes(cls, b: bytes):
        return cls.from_json(b.decode('utf-8'))
    
    def clone(self) -> 'YouTubeVideo':
        return YouTubeVideo.from_json(self.to_json())


async def youtube_to_media_bytes(video_url, format_selector):
    """Download video/audio directly to bytes object"""
    
    # Create temporary file with proper extension
    if 'video' in format_selector or 'mp4' in format_selector:
        suffix = '.mp4'
    elif 'audio' in format_selector or 'm4a' in format_selector:
        suffix = '.m4a'
    else:
        suffix = '.tmp'
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_filename = tmp_file.name
    
    try:
        os.remove(tmp_filename)
    except: pass
    
    ydl_opts = {
        'format': format_selector,
        'outtmpl': tmp_filename,
        'quiet': True,  # Suppress logs
        'no_warnings': True,  # Suppress warnings
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # Read the file into bytes
        with open(tmp_filename, 'rb') as f:
            data = f.read()
        
        return data
    
    except Exception as e:
        print(f"Download error: {e}")
        return None
    
    finally:
        # Clean up - make sure file is deleted
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)
    # with tempfile.NamedTemporaryFile() as tmp:
    #     ydl_opts = {
    #         'format': media_format,  # 'bestaudio[ext=m4a]/bestaudio',
    #         'outtmpl': tmp.name,
    #     }
        
    #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #         ydl.download([video_url])
        
    #     # Read the file into bytes
    #     with open(tmp.name, 'rb') as f:
    #         data = f.read()
        
    #     # # Clean up
    #     # os.unlink(tmp.name)
        
    #     return data


