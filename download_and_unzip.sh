#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./download_and_unzip.sh <url> [output_dir]
# Example:
#   ./download_and_unzip.sh "https://example.com/archive.zip" ./downloaded

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <url> [output_dir]"
  exit 1
fi

URL="$1"
OUTPUT_DIR="${2:-./unzipped}"
TMP_ARCHIVE="$(mktemp /tmp/download.XXXXXX)"
URL_PATH="${URL%%\?*}"
URL_PATH_LOWER="$(printf '%s' "$URL_PATH" | tr '[:upper:]' '[:lower:]')"

cleanup() {
  rm -f "$TMP_ARCHIVE"
}
trap cleanup EXIT

mkdir -p "$OUTPUT_DIR"

echo "Downloading: $URL"
curl -fL "$URL" -o "$TMP_ARCHIVE"

echo "Extracting to: $OUTPUT_DIR"
if [[ "$URL_PATH_LOWER" == *.zip ]]; then
  unzip -o "$TMP_ARCHIVE" -d "$OUTPUT_DIR"
elif [[ "$URL_PATH_LOWER" == *.tar.gz ]] || [[ "$URL_PATH_LOWER" == *.tgz ]]; then
  tar -xzf "$TMP_ARCHIVE" -C "$OUTPUT_DIR"
elif [[ "$URL_PATH_LOWER" == *.tar.bz2 ]] || [[ "$URL_PATH_LOWER" == *.tbz2 ]]; then
  tar -xjf "$TMP_ARCHIVE" -C "$OUTPUT_DIR"
else
  echo "Unsupported archive format in URL: $URL"
  echo "Supported formats: .zip, .tar.gz, .tgz, .tar.bz2, .tbz2"
  exit 1
fi

echo "Done."
