"""YouTube transcript extraction functionality."""
import sys
from typing import List
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from .schemas import TranscriptSegment, TranscriptResponse
from .config import YouTubeConfig

class YouTubeTranscriptExtractor:
    """Handles extraction of transcripts from YouTube videos."""

    def __init__(self, config: YouTubeConfig):
        """Initialize with configuration."""
        self.config = config

    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from various URL formats."""
        patterns = [
            r'(?:v=|/v/|youtu\.be/)([^"&?/\s]{11})',  # Standard and shortened URLs
            r'(?:embed/|e/)([^"&?/\s]{11})',          # Embed URLs
            r'^([^"&?/\s]{11})$'                      # Direct video ID
        ]
        
        for pattern in patterns:
            if match := re.search(pattern, url):
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {url}")

    async def get_transcript(self, url: str, language: str | None = None) -> TranscriptResponse:
        """Get transcript for a YouTube video.
        
        Args:
            url: YouTube video URL or ID
            language: Preferred language code (e.g., 'en', 'es')
        
        Returns:
            TranscriptResponse with transcript text and metadata
        
        Raises:
            ValueError: If video ID cannot be extracted
            TranscriptsDisabled: If transcripts are disabled for the video
            NoTranscriptFound: If no transcript is available
        """
        print(f"[INFO] Getting transcript for URL: {url}", file=sys.stderr)
        
        try:
            video_id = self._extract_video_id(url)
        except ValueError as e:
            print(f"[ERROR] Failed to extract video ID: {str(e)}", file=sys.stderr)
            raise

        language = language or self.config.default_language
        print(f"[INFO] Using language: {language}", file=sys.stderr)

        try:
            print(f"[INFO] Fetching transcript list for video: {video_id}", file=sys.stderr)
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            try:
                print(f"[INFO] Attempting to get transcript in {language}", file=sys.stderr)
                transcript = transcript_list.find_transcript([language])
            except NoTranscriptFound:
                print(f"[INFO] No transcript found in {language}, trying auto-translation", file=sys.stderr)
                transcript = transcript_list.find_manually_created_transcript()
                transcript = transcript.translate(language)

            print("[INFO] Fetching transcript segments", file=sys.stderr)
            segments = transcript.fetch()
            
            # Convert to our schema format
            transcript_segments = [
                TranscriptSegment(
                    text=segment['text'],
                    start=segment['start'],
                    duration=segment['duration']
                )
                for segment in segments
            ]

            # Combine all text for full transcript
            full_text = ' '.join(segment['text'] for segment in segments)
            print(f"[INFO] Successfully extracted transcript with {len(segments)} segments", file=sys.stderr)

            return TranscriptResponse(
                text=full_text,
                language=language,
                segments=transcript_segments
            )

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            error_msg = f"Failed to get transcript for video {video_id}: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise type(e)(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error getting transcript: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise RuntimeError(error_msg)
