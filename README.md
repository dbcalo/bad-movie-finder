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
