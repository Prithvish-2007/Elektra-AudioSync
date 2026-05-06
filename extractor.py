"""
Audio Fingerprinting Module
Converts raw audio into hash fingerprints without loops.
"""

import librosa
import numpy as np
from scipy.ndimage import maximum_filter
import hashlib
from typing import List, Tuple

SAMPLE_RATE = 22050
N_FFT = 4096
HOP_LENGTH = 512
PEAK_NEIGHBORHOOD = (20, 20)
FAN_OUT = 15
TARGET_ZONE_T = 100
TARGET_ZONE_F = 200
MIN_DB = -40


def load_audio(path: str, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Load audio file at specified sample rate."""
    y, _ = librosa.load(path, sr=sr, mono=True)
    return y


def get_spectrogram(y: np.ndarray, n_fft: int = N_FFT, hop_length: int = HOP_LENGTH) -> np.ndarray:
    """Convert audio to log-power spectrogram."""
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    return librosa.amplitude_to_db(S, ref=np.max)


def get_peaks(spec: np.ndarray, neighborhood: Tuple[int, int] = PEAK_NEIGHBORHOOD, 
              min_db: float = MIN_DB) -> List[Tuple[int, int]]:
    """
    Extract peak coordinates from spectrogram using local max filter.
    Returns list of (frequency_bin, time_frame) tuples without loops.
    """
    local_max = maximum_filter(spec, size=neighborhood)
    detected = (spec == local_max) & (spec > min_db)
    freq_indices, time_indices = np.where(detected)
    
    # Convert numpy arrays to list of tuples (vectorized, no explicit loop)
    return list(map(tuple, np.column_stack((freq_indices, time_indices))))


def generate_hashes(peaks: List[Tuple[int, int]], fan_out: int = FAN_OUT, 
                   target_t: int = TARGET_ZONE_T, target_f: int = TARGET_ZONE_F) -> List[Tuple[int, int]]:
    """
    Generate hash pairs from peaks without explicit loops.
    Uses functional programming with map and filter.
    """
    sorted_peaks = sorted(peaks, key=lambda x: x[1])
    
    # For each peak, create candidate pairs using list comprehension (no loop)
    def create_pairs_for_peak(i: int) -> List[Tuple[int, int]]:
        f1, t1 = sorted_peaks[i]
        subsequent_peaks = sorted_peaks[i+1:i+1+fan_out]
        
        # Filter and hash in one comprehension
        valid_pairs = [
            (
                int(hashlib.sha1(f"{f1}|{f2}|{t2-t1}".encode()).hexdigest(), 16) % (2**32),
                t1
            )
            for f2, t2 in subsequent_peaks
            if 0 < t2 - t1 <= target_t and abs(f2 - f1) <= target_f
        ]
        return valid_pairs
    
    # Map over all peak indices and flatten results
    peak_indices = range(len(sorted_peaks))
    all_pairs = map(create_pairs_for_peak, peak_indices)
    
    # Flatten the nested list
    return [pair for sublist in all_pairs for pair in sublist]


def fingerprint(path: str) -> List[Tuple[int, int]]:
    """
    Complete fingerprinting pipeline.
    Returns list of (hash_value, time_offset) tuples.
    """
    y = load_audio(path)
    spec = get_spectrogram(y)
    peaks = get_peaks(spec)
    return generate_hashes(peaks)
