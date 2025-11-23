# Bad Movie Finder

**Bad Movie Finder** is a simple Python script that scans your media library and identifies video files that may need to be **transcoded or remuxed** (e.g., using HandBrake or ffmpeg) due to known color-playback issues. These issues typically appear on some TVs and media players when certain **HEVC / H.265 + Dolby Vision Profile 8** files are played back, often resulting in:

- purple or green tint  
- distorted skin tones  
- washed-out or blown highlights  
- neon-like or incorrect colors  

The script safely scans files using `ffprobe` and flags those most likely to exhibit these problems, helping you locate videos that may need fixing before watching.

---

## Example Terminal Code

Run the script from any OS using:

```bash
py bmf.py "/path/to/your/media/folder"
```

This will recursively scan all subfolders inside the target directory.

---

## Output

During the scan, each relevant file is printed with a tag such as:

- `PROBLEM-DV-P8-HEVC`
- `DV-P7`
- `HEVC-10bit`

A file named **problem_media.csv** will be created in the working directory.

You can open it in Excel or any spreadsheet application and filter on:

- `is_problematic = TRUE` → High-risk files  
- `dv_profile = 8` → Dolby Vision Profile 8  
- `is_dolby_vision = TRUE` → Any DV-tagged files  

---

## Known TVs With Issues  
*(Informational only — not used by the script)*

Some TVs and devices struggle with Dolby Vision Profile 8 in MKV or WebDL formats. Users have reported issues such as color distortion and purple/green tint when playing these files.

Currently reported:

- **Sony Bravia XBR-65X90CH**  
  Purple/green tint with certain Dolby Vision Profile 8 MKV files.

If your TV or player consistently has issues with DV Profile 8, feel free to open an issue or submit a pull request to have it added to this list.

---

## Requirements

- Python **3.8+**
- `ffprobe` (place it next to `bmf.py` or ensure it’s on your PATH)
- Read access to your media folder

On Windows, place `ffprobe.exe` in the same directory as `bmf.py`.  
On Linux/macOS, install FFmpeg using your package manager.

### FFmpeg Download

This script requires `ffprobe`, which is included with FFmpeg.

Download FFmpeg from the official site:  
 https://ffmpeg.org/download.html

For Windows users, prebuilt static FFmpeg packages (which include `ffprobe.exe`) are available here:  
 https://www.gyan.dev/ffmpeg/builds/

---

## Why These Files Need Fixing

Some TVs and players do not properly interpret Dolby Vision metadata (especially **Profile 8**) when it appears in non-standard or remuxed containers such as MKV. This can lead to:

- purple/green color casts  
- incorrect skin tones  
- severely inaccurate HDR tone-mapping  
- neon-like whites or highlights  

These issues can often be fixed by transcoding or remuxing the file using tools such as:

- **HandBrake**
- **ffmpeg**
- **dovi_tool**
- **MKVToolNix**

Common fixes include:

- stripping Dolby Vision metadata  
- converting to HDR10  
- converting to SDR  
- remuxing from MKV to MP4  
- re-encoding into a more compatible format  

**Bad Movie Finder helps you identify which files are likely to require this treatment.**

---

## Contributing

If you encounter:

- additional devices with consistent issues  
- new problematic Dolby Vision profiles  
- other containers or formats that trigger color problems  

Feel free to open an issue or submit a pull request.

---

## License

MIT License

Copyright (c) 2025 Ben Calo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
