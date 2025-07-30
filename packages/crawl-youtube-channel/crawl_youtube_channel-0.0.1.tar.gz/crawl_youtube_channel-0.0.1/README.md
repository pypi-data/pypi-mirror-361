# Crawl YouTube Channel

This Python package provides tools to crawl and extract data from YouTube channels.

## Features

*   Crawl an entire YouTube channel for video information.
*   Extract metadata, comments, transcripts, audio, and video for each video.
*   Provides a base class to easily implement your own video processing and storage logic.
*   Includes a `Sqlite3YouTubeVideoProcessor` for storing data in a local SQLite database.
*   Provides data classes for easy access to crawled data.

## Prerequisites

*   Python 3.10+
*   Google Cloud YouTube API Key

## Installation

1.  **Install the package:**

    ```bash
    pip install crawl-youtube-channel
    ```

2.  **Set up your environment:**

    Create a `.env` file in your project root and add your Google Cloud YouTube API key:

    ```
    GOOGLE_CLOUD_YOUTUBE_API_KEY=your_api_key
    ```

## Usage

To use the crawler, you need to implement the `YouTubeVideoProcessorBase` abstract class. This class defines how to check for existing videos and how to process new ones.

Here is a basic skeleton for a custom processor:

```python
import asyncio
from crawl_youtube_channel import YouTubeVideoProcessorBase, YouTubeVideo

class MyVideoProcessor(YouTubeVideoProcessorBase):
    async def check_video(self, video_id: str) -> bool:
        # Implement logic to check if the video has already been processed.
        # Return True if it exists, False otherwise.
        ...

    async def process_video(self, v: YouTubeVideo) -> None:
        # Implement logic to save or process the video data.
        # For example, save it to a database, a file, or another service.
        ...

async def main():
    # Initialize your custom processor
    processor = MyVideoProcessor()

    # Start crawling the channel
    await processor.process_channel(channel_url='https://www.youtube.com/@YourFavoriteChannel/videos')

if __name__ == '__main__':
    asyncio.run(main())
```

For a concrete implementation example, see the `Sqlite3YouTubeVideoProcessor` class in the source code, which stores video data in a SQLite database.

## Data Models

The following data classes are used to structure the crawled data:

*   `YouTubeVideo`: The main container for all video-related data.
*   `YouTubeThumbnail`: Basic information about a video thumbnail.
*   `YouTubeData`: Contains detailed information about a video, including:
    *   `Meta`: Video metadata (title, description, tags, etc.).
    *   `Comment`: A YouTube comment, including replies.
    *   `Transcript`: The video's transcript.
    *   `audio`: The audio file in M4A format (as bytes).
    *   `video`: The video file in MP4 format (as bytes).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
