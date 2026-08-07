#!/usr/bin/env python3
"""Photo Story Creator 1.4.6 release tests (standard library only)."""
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
    require("Photo Story Creator 1.4.6" in text, "application version was not updated")
    require('id="photoInput"' in text and 'multiple hidden' in text, "individual multi-photo import missing")
    require('id="storyDrop"' in text and "dataTransfer.files" in text, "drag-and-drop import missing")
    require('id="folderInput" type="file" webkitdirectory multiple hidden' in text, "compatible directory picker missing")
    require('id="relinkInput" type="file" webkitdirectory multiple hidden' in text, "relink directory picker missing")
    require("function makeThumbnail(file)" in text and "x.url||x.thumbnail" in text, "saved thumbnail fallback missing")
    require("async function relinkImages(files)" in text, "image relinking workflow missing")
    require("showDirectoryPicker" not in text, "incompatible Linux directory picker remains")
    require("application/x-photo-story-reorder" in text and "e.stopPropagation()" in text, "internal reorder isolation missing")
    require("if(dragIds.length||" in text, "outer import drop guard missing")
    require('id="setSelectedDuration"' in text and "batchDuration" in text, "batch timing editor missing")
    require('id="audioInput"' in text and 'id="audioSummary"' in text, "audio redesign missing")
    require("zenity --file-selection" in text and "Full path to audio file:" in text, "Linux audio resolver missing")
    require("System.Windows.Forms.OpenFileDialog" in text and "$AudioSource" in text, "Windows audio resolver missing")
    require("Audio file not found:" in text, "audio path validation missing")
    require("if tr=='cut': td=frame; tr='fade'" in text, "Linux frame-safe Cut fix missing")
    require("frame=1.0/${state.fps}" in text, "Linux frame duration calculation missing")
    require("if($tr-eq'cut'){$td=1.0/${state.fps};$tr='fade'}" in text, "Windows frame-safe Cut fix missing")
    require("td=.04" not in text and "$td=.04" not in text, "unsafe 0.04-second Cut remains")
    require("heic|heif" in text and "heicPending" in text, "HEIC import handling missing")
    require("img/'PSC_Converted'/x.get('name','')" in text, "Linux converted-HEIC resolver missing")
    require("Join-Path $ImageDir \"PSC_Converted\"" in text, "Windows converted-HEIC resolver missing")
    require("if clip.exists()" not in text and "Get-Item $clip" not in text, "stale clip reuse can override storyboard order")
    require("const conversions=new Map" in text and "const originals=new Map" in text, "two-pass HEIC pairing missing")
    require("converted&&state.images.some(x=>identity(x)===source)" in text, "converted HEIC duplicate guard missing")
    require("matches.find(x=>x.heicPending)||matches[0]" in text and "deduped=true" in text, "existing HEIC duplicate repair missing")
    require("if(rel&&(added.length||replaced.length))state.imageFolder" in text, "image folder update rule missing")
    require((ROOT / "tools" / "convert_heic_linux.sh").is_file(), "Linux HEIC converter missing")
    require((ROOT / "tools" / "convert_heic_windows.ps1").is_file(), "Windows HEIC converter missing")
    linux_converter = (ROOT / "tools" / "convert_heic_linux.sh").read_text(encoding="utf-8")
    windows_converter = (ROOT / "tools" / "convert_heic_windows.ps1").read_text(encoding="utf-8")
    require("PSC_Converted" in linux_converter and "heif-convert" in linux_converter, "Linux converter incomplete")
    require("PSC_Converted" in windows_converter and "magick" in windows_converter, "Windows converter incomplete")


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
    with tempfile.TemporaryDirectory(prefix="psc14-test-") as temp:
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
    print("All Photo Story Creator 1.4.6 tests passed.")


if __name__ == "__main__":
    main()
