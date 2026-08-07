#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-.}"
OUTPUT_DIR="${2:-$SOURCE_DIR/PSC_Converted}"
mkdir -p "$OUTPUT_DIR"

if command -v heif-convert >/dev/null 2>&1; then
  CONVERTER=heif
elif command -v magick >/dev/null 2>&1; then
  CONVERTER=magick
elif command -v ffmpeg >/dev/null 2>&1; then
  CONVERTER=ffmpeg
else
  echo "No HEIC converter found."
  echo "Linux Mint/Ubuntu: sudo apt install libheif-examples"
  exit 1
fi

count=0
while IFS= read -r -d '' source; do
  name="$(basename "$source")"
  target="$OUTPUT_DIR/$name.jpg"
  if [[ -s "$target" && "$target" -nt "$source" ]]; then
    echo "Reusing: $target"
    continue
  fi
  echo "Converting: $source"
  case "$CONVERTER" in
    heif) heif-convert -q 95 "$source" "$target" >/dev/null ;;
    magick) magick "$source" -auto-orient -quality 95 "$target" ;;
    ffmpeg) ffmpeg -loglevel error -y -i "$source" -frames:v 1 -q:v 2 "$target" ;;
  esac
  count=$((count + 1))
done < <(find "$SOURCE_DIR" -maxdepth 1 -type f \( -iname '*.heic' -o -iname '*.heif' \) -print0)

echo "Complete: $count converted. Originals were not changed."
echo "Import this folder in Photo Story Creator: $OUTPUT_DIR"
