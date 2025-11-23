#!/usr/bin/env python3
"""
Bad Movie Finder

Scan a media library for video files that are likely to show bad colors
(purple/green tint, neon skin tones, etc.) on some TVs and players.

Current focus:
- HEVC (H.265) video streams
- With Dolby Vision side-data present
- Specifically Dolby Vision Profile 8, which is a common troublemaker in
  MKV / web 4K files on many devices.

Detection is based ONLY on file metadata. The script does not make any
assumptions about your TV — users decide whether the results are relevant
for their setup.

Known TVs with issues (user-reported):
- Sony Bravia XBR-65X90CH
  Symptoms: Purple/green tint with DV Profile 8 in some MKV/WebDL formats.

(Users can add their TVs to this comment list in pull requests.)

Example terminal code:

  py bmf.py "/path/to/your/media/folder"

Output:
- Prints a summary line per relevant file
- Writes problem_media.csv with details for filtering in a spreadsheet

Requirements:
- Python 3.8+
- ffprobe (from FFmpeg) in the same folder as this script (or on PATH)
"""

import os
import sys
import csv
import json
import subprocess
from pathlib import Path

# ------------ config ------------

MEDIA_EXTENSIONS = {".mkv", ".mp4", ".mov", ".avi", ".m4v", ".ts", ".webm"}
CSV_OUTPUT = "problem_media.csv"


# ---------------- ffprobe discovery ----------------

SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_FFPROBE = None
for name in ("ffprobe.exe", "ffprobe"):
    candidate = SCRIPT_DIR / name
    if candidate.exists():
        LOCAL_FFPROBE = str(candidate)
        break

if LOCAL_FFPROBE is None:
    print("[Bad Movie Finder] ERROR: ffprobe not found in script directory.")
    print("Place ffprobe.exe (Windows) or ffprobe (Linux/macOS) next to this script,")
    print("or ensure ffprobe is on your PATH, then run again.")
    sys.exit(1)


# ---------------- helpers ----------------

def run_ffprobe(file_path: Path) -> dict | None:
    """Run ffprobe and return parsed JSON, or None on error."""
    cmd = [
        LOCAL_FFPROBE,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_streams",
        "-show_format",
        "-print_format", "json",
        str(file_path),
    ]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() or e.stdout.strip()
        print(f"[WARN] ffprobe failed: {file_path} -> {msg}")
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"[WARN] Could not parse ffprobe JSON: {file_path}")
        return None


def detect_bit_depth(stream: dict) -> int | None:
    """Infer bit depth from common fields and pixel format."""
    for key in ("bits_per_raw_sample", "bits_per_sample"):
        if key in stream:
            try:
                return int(stream[key])
            except (ValueError, TypeError):
                pass

    pix_fmt = (stream.get("pix_fmt") or "").lower()
    if any(tag in pix_fmt for tag in ("p10", "10le", "10be")):
        return 10
    if any(tag in pix_fmt for tag in ("p12", "12le", "12be")):
        return 12
    return None


def parse_dovi_info(stream: dict) -> dict:
    """
    Extract Dolby Vision (DOVI) info from side_data_list, if present.

    Returns a dict with:
      - is_dolby_vision: bool
      - dv_profile: int | None
      - el_present_flag: int | None
      - bl_present_flag: int | None
      - dv_bl_signal_compatibility_id: int | None
    """
    info = {
        "is_dolby_vision": False,
        "dv_profile": None,
        "el_present_flag": None,
        "bl_present_flag": None,
        "dv_bl_signal_compatibility_id": None,
    }

    side_list = stream.get("side_data_list") or []
    for side in side_list:
        side_type = (side.get("side_data_type") or "").lower()
        if "dovi" in side_type or "dolby vision" in side_type:
            info["is_dolby_vision"] = True
            for key in (
                "dv_profile",
                "el_present_flag",
                "bl_present_flag",
                "dv_bl_signal_compatibility_id",
            ):
                val = side.get(key)
                if isinstance(val, str):
                    try:
                        info[key] = int(val)
                    except ValueError:
                        info[key] = None
                else:
                    info[key] = val
            break

    return info


def analyze_file(file_path: Path) -> dict | None:
    """Return a dict of video/DV info for one file, or None if irrelevant."""
    data = run_ffprobe(file_path)
    if not data:
        return None

    streams = data.get("streams") or []
    if not streams:
        return None

    v = streams[0]  # first video stream
    codec = (v.get("codec_name") or "unknown").lower()
    pix_fmt = v.get("pix_fmt", "unknown")
    color_primaries = v.get("color_primaries", "")
    color_transfer = v.get("color_transfer", "")
    color_space = v.get("color_space", "")

    bit_depth = detect_bit_depth(v)
    is_10bit_or_more = bit_depth is not None and bit_depth >= 10
    is_hevc = codec in ("hevc", "h265")

    dovi = parse_dovi_info(v)
    is_dolby_vision = dovi["is_dolby_vision"]
    dv_profile = dovi["dv_profile"]
    el_present_flag = dovi["el_present_flag"]
    bl_present_flag = dovi["bl_present_flag"]
    dv_bl_signal_compat = dovi["dv_bl_signal_compatibility_id"]

    # Core Bad Movie Finder heuristic (TV-independent):
    # - HEVC + Dolby Vision + Profile 8 is considered "high risk"
    #   for color issues across many devices.
    is_problematic = bool(is_hevc and is_dolby_vision and dv_profile == 8)

    # Log anything that might be relevant to HDR/DV/HEVC troubleshooting.
    if not (is_hevc or is_10bit_or_more or is_dolby_vision):
        return None

    return {
        "path": str(file_path),
        "codec": codec,
        "pix_fmt": pix_fmt,
        "bit_depth": bit_depth if bit_depth is not None else "unknown",
        "color_primaries": color_primaries,
        "color_transfer": color_transfer,
        "color_space": color_space,
        "is_hevc": is_hevc,
        "is_10bit_or_more": is_10bit_or_more,
        "is_dolby_vision": is_dolby_vision,
        "dv_profile": dv_profile,
        "el_present_flag": el_present_flag,
        "bl_present_flag": bl_present_flag,
        "dv_bl_signal_compatibility_id": dv_bl_signal_compat,
        "is_problematic": is_problematic,
    }


# ---------------- main ----------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Bad Movie Finder")
        print("Usage: py bad_movie_finder.py <media_folder>")
        sys.exit(1)

    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.exists():
        print(f"[Bad Movie Finder] ERROR: Folder not found: {root}")
        sys.exit(1)

    print(f"[Bad Movie Finder] Scanning: {root}\n")

    results: list[dict] = []

    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            ext = Path(fn).suffix.lower()
            if ext not in MEDIA_EXTENSIONS:
                continue

            fp = Path(dirpath) / fn
            info = analyze_file(fp)
            if not info:
                continue

            results.append(info)

            if info["is_problematic"]:
                tag = "PROBLEM-DV-P{}-HEVC".format(info["dv_profile"] or "?")
            elif info["is_dolby_vision"]:
                tag = "DV-P{}".format(info["dv_profile"] or "?")
            elif info["is_hevc"] and info["is_10bit_or_more"]:
                tag = "HEVC-10bit"
            else:
                tag = "OTHER"

            print(
                f"[{tag}] {fp} "
                f"(codec={info['codec']}, "
                f"bit_depth={info['bit_depth']}, "
                f"is_dolby_vision={info['is_dolby_vision']}, "
                f"dv_profile={info['dv_profile']})"
            )

    if not results:
        print("\n[Bad Movie Finder] Done. No HEVC, 10-bit+, or DV-tagged files detected.")
        return

    fieldnames = [
        "path",
        "codec",
        "pix_fmt",
        "bit_depth",
        "color_primaries",
        "color_transfer",
        "color_space",
        "is_hevc",
        "is_10bit_or_more",
        "is_dolby_vision",
        "dv_profile",
        "el_present_flag",
        "bl_present_flag",
        "dv_bl_signal_compatibility_id",
        "is_problematic",
    ]
    with open(CSV_OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[Bad Movie Finder] Done. Found {len(results)} HEVC/10-bit/DV-related files.")
    print(f"[Bad Movie Finder] Details written to: {CSV_OUTPUT}")
    print("[Bad Movie Finder] Filter is_problematic = TRUE to see high-risk titles.")


if __name__ == "__main__":
    main()

