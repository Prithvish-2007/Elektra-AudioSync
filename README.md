🎵 AudioMatch: Audio Fingerprinting System

AudioMatch is a full-stack, Shazam-inspired audio identification engine. Built with a Python/FastAPI backend and a React + Tailwind CSS frontend, it delivers fast, accurate audio matching utilizing a lightweight SQLite database for rapid hash lookups.
⚙️ Core Algorithm & Backend

The system relies on an exact-match voting algorithm. It processes audio using Short-Time Fourier Transform (STFT) to generate constellation maps and extract local maxima peaks. A major technical highlight is its pure functional programming approach. By utilizing vectorized NumPy operations, map(), and reduce(), the backend completely eliminates explicit loops during fingerprinting and matching. This ensures high efficiency:

    Fingerprinting: ~100–500ms per song

    Matching: ~10–50ms per query

🎨 Interactive Frontend

The frontend offers a highly responsive user interface featuring:

    Audio Inputs: Drag-and-drop file uploads or live 5-second microphone recordings.

    Real-Time Visualization: Interactive waveform rendering powered by WaveSurfer.js.

    Library Management: Complete CRUD operations for indexing and removing songs.

    Evaluation Dashboard: Tools to run batch benchmarking, calculating Top-1 accuracy and Mean Reciprocal Rank (MRR).
