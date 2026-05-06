"""
FastAPI REST API for AudioMatch
Complete backend server with all endpoints.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import uuid
import os
import json
from typing import List

from extractor import fingerprint
from indexer import init_db, index_song, get_all_songs, delete_song, get_song_details
from matcher import match
from evaluator import evaluate, evaluate_with_details
from models import (
    MatchResult, IndexResponse, SongInfo, 
    EvaluationResult, TestCase, DetailedEvaluationResult
)

# Initialize FastAPI app
app = FastAPI(
    title="AudioMatch API",
    version="1.0.0",
    description="Audio fingerprinting and identification system"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Ensure temp directory exists
os.makedirs("/tmp", exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "AudioMatch"}


@app.post("/index", response_model=IndexResponse)
async def index_audio(
    file: UploadFile = File(...),
    title: str = Form(...),
    artist: str = Form(...)
):
    """
    Index a new song by uploading audio file with metadata.
    
    Returns: song_id, title, and number of fingerprints indexed
    """
    try:
        song_id = str(uuid.uuid4())
        
        # Save uploaded file temporarily
        temp_path = f"/tmp/{song_id}_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract fingerprints
        fps = fingerprint(temp_path)
        
        # Index the song
        index_song(song_id, title, artist, fps)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return IndexResponse(
            song_id=song_id,
            title=title,
            fingerprints_indexed=len(fps)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match", response_model=MatchResult)
async def match_audio(file: UploadFile = File(...)):
    """
    Match a query audio clip against the indexed database.
    
    Returns: best match with song_id, confidence score, and voting details
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/query_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract fingerprints from query
        fps = fingerprint(temp_path)
        
        # Perform matching
        result = match(fps)
        
        # Enrich result with song details if match found
        if result.get("song_id"):
            title, artist = get_song_details(result["song_id"])
            result["song_title"] = title
            result["song_artist"] = artist
        
        # Clean up temp file
        os.remove(temp_path)
        
        return MatchResult(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/songs", response_model=List[SongInfo])
async def list_songs():
    """
    Retrieve all indexed songs in the database.
    
    Returns: list of songs with id, title, and artist
    """
    try:
        songs = get_all_songs()
        return [
            SongInfo(song_id=s[0], title=s[1], artist=s[2])
            for s in songs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/songs/{song_id}", response_model=SongInfo)
async def get_song(song_id: str):
    """Get details for a specific song."""
    try:
        title, artist = get_song_details(song_id)
        if not title:
            raise HTTPException(status_code=404, detail="Song not found")
        return SongInfo(song_id=song_id, title=title, artist=artist)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/songs/{song_id}")
async def remove_song(song_id: str):
    """
    Remove a song and all its fingerprints from the index.
    
    Returns: confirmation message
    """
    try:
        delete_song(song_id)
        return {"message": f"Song {song_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate", response_model=EvaluationResult)
async def evaluate_accuracy(test_cases: List[TestCase]):
    """
    Run batch evaluation on test cases to compute accuracy metrics.
    
    Args:
        test_cases: List of test cases with audio_path and expected_song_id
    
    Returns: top1_accuracy, MRR, total cases, and correct matches
    """
    try:
        test_data = [
            {
                "audio_path": case.audio_path,
                "expected_song_id": case.expected_song_id
            }
            for case in test_cases
        ]
        
        result = evaluate(test_data)
        return EvaluationResult(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate/detailed", response_model=DetailedEvaluationResult)
async def evaluate_accuracy_detailed(test_cases: List[TestCase]):
    """
    Run batch evaluation with detailed per-case results.
    
    Returns: same as /evaluate plus detailed results for each test case
    """
    try:
        test_data = [
            {
                "audio_path": case.audio_path,
                "expected_song_id": case.expected_song_id
            }
            for case in test_cases
        ]
        
        result = evaluate_with_details(test_data)
        return DetailedEvaluationResult(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    try:
        songs = get_all_songs()
        return {
            "total_songs": len(songs),
            "songs": [{"id": s[0], "title": s[1], "artist": s[2]} for s in songs]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn main:app --reload --port 8000
