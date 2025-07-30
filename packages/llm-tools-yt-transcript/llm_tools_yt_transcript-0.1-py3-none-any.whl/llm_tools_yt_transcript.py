import re
import requests

import llm
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url_or_id):
    if len(url_or_id) == 11 and not '/' in url_or_id:
        return url_or_id
    
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)
        return transcript.to_raw_data()
    except Exception as e:
        raise Exception(f"Failed to fetch transcript for video {video_id}: {e}")


def get_video_metadata(video_id):
    try:
        # Use YouTube's oEmbed API to get video metadata
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch metadata for video {video_id}: {e}")


def yt_transcript(input: str) -> str:
    """
    input: a youtube video id or url
    Returns: a stringified json object with metadata and transcript of a youtube video
    """
    video_id = extract_video_id(input)
    transcript = get_transcript(video_id)
    metadata = get_video_metadata(video_id)
    metadata['transcript'] = transcript

    return metadata


@llm.hookimpl
def register_tools(register):
    register(yt_transcript)
