"""
Fingerprint Indexer Module
Manages SQLite database for fingerprint storage and lookup without loops.
"""

import sqlite3
from typing import List, Tuple
import os

DB_PATH = "data/index.db"


def ensure_db_dir():
    """Create data directory if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)


def init_db():
    """Initialize SQLite database with required tables and indices."""
    ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fingerprints (
            hash INTEGER,
            song_id TEXT,
            time_offset INTEGER
        )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints(hash)")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            song_id TEXT PRIMARY KEY,
            title TEXT,
            artist TEXT,
            duration REAL
        )
    """)
    
    conn.commit()
    conn.close()


def index_song(song_id: str, title: str, artist: str, fingerprints: List[Tuple[int, int]]):
    """
    Index a song with its fingerprints.
    Uses executemany to avoid explicit loops.
    """
    conn = sqlite3.connect(DB_PATH)
    
    # Insert song metadata
    conn.execute(
        "INSERT OR REPLACE INTO songs VALUES (?, ?, ?, ?)",
        (song_id, title, artist, 0.0)
    )
    
    # Batch insert all fingerprints without loop (using executemany)
    fingerprint_data = [(h, song_id, t) for h, t in fingerprints]
    conn.executemany(
        "INSERT INTO fingerprints VALUES (?, ?, ?)",
        fingerprint_data
    )
    
    conn.commit()
    conn.close()


def lookup_hash(hash_val: int) -> List[Tuple[str, int]]:
    """
    Look up all songs matching a hash value.
    Returns list of (song_id, time_offset) tuples.
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT song_id, time_offset FROM fingerprints WHERE hash = ?",
        (hash_val,)
    ).fetchall()
    conn.close()
    return rows


def get_all_songs() -> List[Tuple[str, str, str]]:
    """
    Retrieve all indexed songs.
    Returns list of (song_id, title, artist) tuples.
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT song_id, title, artist FROM songs").fetchall()
    conn.close()
    return rows


def delete_song(song_id: str):
    """Delete a song and all its fingerprints from the index."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM songs WHERE song_id = ?", (song_id,))
    conn.execute("DELETE FROM fingerprints WHERE song_id = ?", (song_id,))
    conn.commit()
    conn.close()


def get_song_details(song_id: str) -> Tuple[str, str]:
    """Get title and artist for a song ID."""
    conn = sqlite3.connect(DB_PATH)
    result = conn.execute(
        "SELECT title, artist FROM songs WHERE song_id = ?",
        (song_id,)
    ).fetchone()
    conn.close()
    return result or (None, None)
