#!/usr/bin/env python3
"""Pull frames from a finished video into one contact sheet (ffmpeg only).

Default times: the hook (0.3, 1, 2, 3.5, 5, 8 s) plus evenly spaced frames across the film.
Prints which tile shows which second.
"""
import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("-o", "--out", required=True, help="输出 jpg")
    ap.add_argument("--at", help="逗号分隔的秒数，例如 0.5,2,5,30")
    ap.add_argument("--n", type=int, default=24, help="默认取帧总数")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--width", type=int, default=480)
    a = ap.parse_args()

    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", a.video],
                                  capture_output=True, text=True, check=True).stdout)
    dur = float(j["format"]["duration"])
    if a.at:
        times = [float(x) for x in a.at.split(",") if x.strip()]
    else:
        hook = [t for t in (0.3, 1.0, 2.0, 3.5, 5.0, 8.0) if t < dur]
        rest = max(0, a.n - len(hook))
        times = hook + [10 + (dur - 11) * i / max(1, rest - 1) for i in range(rest)] if dur > 12 else hook
    times = sorted({round(min(max(t, 0.0), dur - 0.05), 2) for t in times})

    tmp = Path(tempfile.mkdtemp(prefix="vibe-sheet-"))
    for i, t in enumerate(times):
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t}", "-i", a.video, "-frames:v", "1",
                        "-vf", f"scale={a.width}:-2", str(tmp / f"f_{i:03d}.jpg")], check=True)
    rows = math.ceil(len(times) / a.cols)
    h = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=height", "-of", "json", str(tmp / "f_000.jpg")],
                                  capture_output=True, text=True, check=True).stdout)["streams"][0]["height"]
    for k in range(len(times), rows * a.cols):  # fill the last row with black tiles
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={a.width}x{h}",
                        "-frames:v", "1", str(tmp / f"f_{k:03d}.jpg")], check=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(tmp / "f_%03d.jpg"), "-vf", f"tile={a.cols}x{rows}",
                    "-frames:v", "1", "-q:v", "3", a.out], check=True)
    for i, t in enumerate(times):
        print(f"格 {i + 1:>2}（第 {i // a.cols + 1} 行）：{t:g} 秒")
    print("→", a.out)


if __name__ == "__main__":
    sys.exit(main())
