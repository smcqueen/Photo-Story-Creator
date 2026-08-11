#!/usr/bin/env python3
"""Photo Story Creator 1.6 release tests (standard library only)."""
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
    require("Photo Story Creator 1.6" in text, "application version was not updated")
    require("Version 1.6 workflow" in text and "Version 1.5 workflow" not in text, "dashboard workflow label was not updated")
    require("version:'1.6'" in text, "new projects do not use the 1.6 project format version")
    require('id="previewPage"' in text and 'id="previewStage"' in text, "preview workspace missing")
    require(all(f'id="{control}"' in text for control in ("previewPlay", "previewRestart", "previewPrevious", "previewNext", "previewFromSelected", "previewFullscreen")), "preview controls missing")
    require("function previewTimeline" in text and "function seekPreview" in text, "preview timing/navigation missing")
    require("requestFullscreen" in text and "previewDraft" in text, "full-screen/draft preview missing")
    require("previewAudioFile" in text and "syncPreviewAudio" in text, "preview soundtrack support missing")
    require('id="fullscreenStory"' in text and "id:'openFullscreen'" in text, "full-screen storyboard missing")
    require("applyFullFilter" in text and 'id="fsSearch"' in text and 'id="fsFilter"' in text, "full-screen search/filter missing")
    require("moveSelectionTo" in text and 'id="fsMoveBefore"' in text and 'id="fsMoveAfter"' in text, "long-distance move controls missing")
    require('id="fsCut"' in text and 'id="fsPaste"' in text, "cut/paste arranging missing")
    require("managerHome.after(managerGrid)" in text, "shared storyboard restoration missing")
    require("e.key==='Escape'" in text, "Escape exit missing")
    require("function jumpToRequested()" in text, "dependable jump handler missing")
    require("stage.scrollTo" in text and "jump-target" in text, "jump scrolling/highlight missing")
    require("card?.classList.contains('filtered-out')" in text, "filtered jump target recovery missing")
    require("Number.isInteger(number)" in text and "fsNumber').onkeydown" in text, "jump validation/Enter activation missing")
    require('id="inspectTitle"' in text and 'id="inspectCaptionPosition"' in text, "slide caption editor missing")
    require("captionFont" in text and "captionSize" in text and "captionShadow" in text, "caption typography controls missing")
    require("captionOverlay" in text and "caption-preview" in text, "caption preview missing")
    require("withCaptionText" in text and "captionText(x)" in text, "title/caption renderer integration missing")
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
    with tempfile.TemporaryDirectory(prefix="psc16-test-") as temp:
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


def caption_render_test() -> None:
    if not shutil.which("ffmpeg"):
        print("SKIP: caption render test (ffmpeg not installed)")
        return
    with tempfile.TemporaryDirectory(prefix="psc16-caption-") as temp:
        work = Path(temp)
        caption = work / "caption.txt"
        caption.write_text("Summer Journey\nThe journey begins", encoding="utf-8")
        output = work / "caption.mp4"
        escaped = str(caption).replace("'", "\\'")
        subprocess.run([
            "ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
            "color=c=navy:s=640x360:r=24:d=1", "-vf",
            f"drawtext=textfile='{escaped}':font=sans-serif:fontcolor=white:fontsize=32:"
            "box=1:boxcolor=black@0.55:boxborderw=12:shadowx=2:shadowy=2:"
            "x=(w-text_w)/2:y=h-text_h-40,format=yuv420p",
            "-t", "1", "-c:v", "libx264", str(output),
        ], check=True)
        require(output.is_file() and output.stat().st_size > 0, "captioned video was not created")
        print("PASS: FFmpeg UTF-8 title/caption render")


def main() -> None:
    static_tests()
    print("PASS: static release checks")
    ffmpeg_regression_test()
    caption_render_test()
    print("All Photo Story Creator 1.6 tests passed.")


if __name__ == "__main__":
    main()
