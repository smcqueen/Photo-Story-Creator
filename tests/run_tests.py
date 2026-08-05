#!/usr/bin/env python3
"""Photo Story Creator 1.3 release tests (standard library only)."""
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def static_tests() -> None:
    text = INDEX.read_text(encoding="utf-8")
    require("Photo Story Creator 1.3" in text, "application version was not updated")
    require("if tr=='cut': td=frame; tr='fade'" in text, "Linux frame-safe Cut fix missing")
    require("frame=1.0/${state.fps}" in text, "Linux frame duration calculation missing")
    require("if($tr-eq'cut'){$td=1.0/${state.fps};$tr='fade'}" in text, "Windows frame-safe Cut fix missing")
    require("td=.04" not in text and "$td=.04" not in text, "unsafe 0.04-second Cut remains")


def duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def ffmpeg_regression_test() -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("SKIP: FFmpeg integration test (ffmpeg/ffprobe not installed)")
        return
    fps = 24
    frame = 1.0 / fps
    durations = [5.0] * 6
    transitions = [("fade", frame), ("slideright", 2.0), ("fade", 2.0), ("fade", 2.0), ("fade", 2.0)]
    with tempfile.TemporaryDirectory(prefix="psc13-test-") as temp:
        work = Path(temp)
        clips = []
        for index in range(6):
            clip = work / f"{index}.mp4"
            subprocess.run([
                "ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                f"color=c=black:s=320x180:r={fps}:d=5", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip)
            ], check=True)
            clips.append(clip)
        parts = []
        elapsed = durations[0]
        previous = "[0:v]"
        for index, (transition, td) in enumerate(transitions, start=1):
            offset = max(0.0, elapsed - td)
            output = f"[v{index}]"
            parts.append(f"{previous}[{index}:v]xfade=transition={transition}:duration={td}:offset={offset}{output}")
            previous = output
            elapsed += durations[index] - td
        output = work / "mixed-transitions.mp4"
        command = ["ffmpeg", "-loglevel", "error", "-y"]
        for clip in clips:
            command += ["-i", str(clip)]
        command += ["-filter_complex", ";".join(parts), "-map", previous, "-r", str(fps), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(output)]
        subprocess.run(command, check=True)
        actual = duration(output)
        require(abs(actual - elapsed) <= frame * 1.5, f"mixed transition duration {actual:.6f}s; expected {elapsed:.6f}s")
        require(actual > 20.0, "regression: output collapsed to first-clip duration")
        print(f"PASS: FFmpeg mixed-transition duration {actual:.6f}s")


def main() -> None:
    static_tests()
    print("PASS: static release checks")
    ffmpeg_regression_test()
    print("All Photo Story Creator 1.3 tests passed.")


if __name__ == "__main__":
    main()
