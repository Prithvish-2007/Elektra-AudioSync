"""
Core Matching Engine Module
Implements exact-match voting algorithm without explicit loops.
Uses functional programming with map and reduce.
"""

from typing import List, Tuple, Dict
from collections import defaultdict
from functools import reduce
from indexer import lookup_hash


def match(query_fingerprints: List[Tuple[int, int]]) -> Dict:
    """
    Core exact-match engine using functional voting.
    
    Args:
        query_fingerprints: List of (hash_value, time_offset) tuples
    
    Returns:
        dict with song_id, confidence, vote_count, total_fingerprints
    """
    
    if not query_fingerprints:
        return {
            "song_id": None,
            "confidence": 0.0,
            "vote_count": 0,
            "total_fingerprints": 0,
            "message": "No query fingerprints provided"
        }
    
    # Map: For each query fingerprint, get all matching candidates
    def get_candidates_for_hash(hash_and_time: Tuple[int, int]) -> List[Tuple[str, int, int]]:
        hash_val, q_time = hash_and_time
        candidates = lookup_hash(hash_val)
        # Return tuples of (song_id, db_time - q_time, 1) for voting
        return [(song_id, db_time - q_time, 1) for song_id, db_time in candidates]
    
    # Get all candidates for all hashes
    all_candidates = map(get_candidates_for_hash, query_fingerprints)
    flattened_candidates = [c for sublist in all_candidates for c in sublist]
    
    if not flattened_candidates:
        return {
            "song_id": None,
            "confidence": 0.0,
            "vote_count": 0,
            "total_fingerprints": len(query_fingerprints),
            "message": "No match found"
        }
    
    # Reduce: Aggregate votes by (song_id, delta_t)
    def aggregate_votes(vote_dict: Dict, candidate: Tuple[str, int, int]) -> Dict:
        song_id, delta_t, vote = candidate
        key = (song_id, delta_t)
        vote_dict[key] = vote_dict.get(key, 0) + vote
        return vote_dict
    
    vote_counter = reduce(aggregate_votes, flattened_candidates, {})
    
    # Find the key with maximum votes
    best_key = max(vote_counter.items(), key=lambda x: x[1])
    (best_song_id, best_delta_t), max_votes = best_key
    
    total_fp = len(query_fingerprints)
    confidence = min(max_votes / max(total_fp, 1), 1.0)
    
    return {
        "song_id": best_song_id,
        "delta_t": int(best_delta_t),
        "vote_count": int(max_votes),
        "total_fingerprints": total_fp,
        "confidence": round(confidence, 4)
    }
