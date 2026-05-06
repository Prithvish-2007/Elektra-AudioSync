"""
Pydantic Models for Request/Response Validation
"""

from pydantic import BaseModel
from typing import Optional, List


class SongMetadata(BaseModel):
    """Song metadata for indexing."""
    title: str
    artist: str


class MatchResult(BaseModel):
    """Result of audio matching."""
    song_id: Optional[str] = None
    delta_t: Optional[int] = None
    vote_count: Optional[int] = None
    total_fingerprints: int
    confidence: float
    message: Optional[str] = None


class IndexResponse(BaseModel):
    """Response from song indexing."""
    song_id: str
    title: str
    fingerprints_indexed: int


class SongInfo(BaseModel):
    """Song information in library."""
    song_id: str
    title: str
    artist: str


class EvaluationResult(BaseModel):
    """Evaluation metrics result."""
    top1_accuracy: float
    mrr: float
    total: int
    correct: int


class TestCase(BaseModel):
    """Single test case for evaluation."""
    audio_path: str
    expected_song_id: str


class DetailedEvaluationResult(BaseModel):
    """Detailed evaluation with per-case results."""
    top1_accuracy: float
    mrr: float
    total: int
    correct: int
    results: List[dict]
