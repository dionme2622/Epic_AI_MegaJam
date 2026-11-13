"""Generate the four English boss-prologue lines as Unreal-ready WAV files.

Run with Unreal 5.8's bundled Python after installing edge-tts into
MegaJam/Saved/PythonPackages, for example::

    python -m pip install --target MegaJam/Saved/PythonPackages edge-tts==7.3.1
    python MegaJam/SourceAssets/BossPrologue/generate_voice.py

Requires an internet connection and ffmpeg.
"""

import asyncio
import json
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "Saved" / "PythonPackages"))

import edge_tts  # noqa: E402


OUTPUT = Path(__file__).resolve().parent / "Voice"
FFMPEG = shutil.which("ffmpeg") or Path(r"D:\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe")

LINES = [
    ("01_Hero_Challenge", "Prepare yourself, dragon!", "en-US-GuyNeural", "+6%", "+0Hz"),
    ("02_Dragon_Threat", "Ha ha ha! I'll roast you alive!", "en-US-ChristopherNeural", "-8%", "-18Hz"),
    ("03_Dragon_MissingLegs", "...Where did my legs go?", "en-US-ChristopherNeural", "-10%", "-18Hz"),
    ("04_Dragon_Protest", "You took my legs because they were off camera?", "en-US-ChristopherNeural", "-8%", "-18Hz"),
]


async def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for name, line, voice, rate, pitch in LINES:
            mp3 = Path(temp_dir) / f"{name}.mp3"
            wav = OUTPUT / f"{name}.wav"
            await edge_tts.Communicate(line, voice, rate=rate, pitch=pitch).save(str(mp3))
            subprocess.run(
                [str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error", "-i", str(mp3),
                 "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)],
                check=True,
            )
            with wave.open(str(wav), "rb") as audio:
                duration = audio.getnframes() / audio.getframerate()
            manifest.append({"name": name, "text": line, "voice": voice, "duration_seconds": round(duration, 3)})
            print(f"{name}: {duration:.3f}s -> {wav}")
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
