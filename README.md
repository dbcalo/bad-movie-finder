# Bad Movie Finder

**Bad Movie Finder** is a simple Python script that scans a media library for video files that may display **incorrect colors** (purple/green tint or distorted tones) on some TVs and media players. These issues most commonly appear with:

- **HEVC / H.265** video  
- Containing **Dolby Vision** metadata  
- Especially **Dolby Vision Profile 8** inside MKV or WebDL releases  

The script performs a safe, **read-only** scan of each file using `ffprobe` and outputs a list of potentially problematic titles.

---

## Example Terminal Code

Run the script from any OS using:

```bash
py bmv.py "/path/to/your/media/folder"
```

This will recursively scan all subfolders.

---

## Output

During the scan, each relevant file is printed with a tag such as:

- `PROBLEM-DV-P8-HEVC`
- `DV-P7`
- `HEVC-10bit`

A file called **problem_media.csv** will be created in the working directory.

You can open it in Excel or any spreadsheet app and filter on:

- `is_problematic = TRUE` → High-risk files  
- `dv_profile = 8` → Dolby Vision Profile 8  
- `is_dolby_vision = TRUE` → Any DV-tagged files  

---

## Known TVs With Issues  
*(Informational only — not used by the script)*

- **Sony Bravia XBR-65X90CH**  
  User-reported purple/green tint with Dolby Vision Profile 8 in MKV files.

---

## Requirements

- Python **3.8+**
- `ffprobe` (place it next to `bmv.py` or ensure it’s on your PATH)
- Read access to your media folder

On Windows, place `ffprobe.exe` in the same directory as `bmv.py`.  
On Linux/macOS, install FFmpeg using your package manager.

---

## Why This Script Exists

Some TVs and players mishandle **Dolby Vision Profile 8** when it is remuxed into MKV or other non-standard containers. This can lead to:

- Green or purple color casts  
- Washed-out or blown highlights  
- Incorrect skin tones  
- Other color-mapping issues  

This tool helps users quickly identify files that are likely to cause those problems.

---

## Contributing

If you encounter:

- Additional devices with consistent issues  
- Other problematic patterns (profiles, containers, flags)  

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
