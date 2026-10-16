#!/usr/bin/env python3
"""Render a Vibe 知识大赏 film and export the two deliverables.

Steps: build (build.mjs / net.mjs) → subset fonts → lint → temp score + master to -14 LUFS →
render 60fps → <name>-上传版-无配乐.mp4 (CRF 20, no audio) → <name>-预览版-临时配乐.mp4 (AAC 320k) →
verify durations, tracks and loudness → delete the raw render.
Takes ~15-20 min for a 2-minute film: run it in the background.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HF = ["npx", "--yes", "hyperframes@0.8.138"]
LOUD = re.compile(r"\{[^{}]*\"input_i\"[^{}]*\}")


def run(cmd, cwd):
    print("→", " ".join(map(str, cmd)), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def probe(f: Path):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", str(f)],
                                  capture_output=True, text=True, check=True).stdout)
    return float(j["format"]["duration"]), [s["codec_type"] for s in j.get("streams", [])]


def measure(f: Path, af: str = "loudnorm=print_format=json"):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", af, "-f", "null", "-"], capture_output=True, text=True)
    return json.loads(LOUD.search(r.stderr).group(0))


def master(src: Path, out: Path, dur: float):
    base = f"afade=t=in:d=0.05,afade=t=out:st={max(0.0, dur - 1.8):.2f}:d=1.8"
    m = measure(src, base + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json")
    f = base + (f",loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
                f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-af", f, "-ar", "48000", str(out)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("film", help="工程目录（含 index.html）")
    ap.add_argument("--name", required=True, help="成片文件名前缀，通常是中文标题")
    ap.add_argument("--archive-old", metavar="TAG", help="已有成片改名为 <name>-TAG-… 后再出新版，例如 v1")
    ap.add_argument("--overwrite", action="store_true", help="直接覆盖已有成片")
    ap.add_argument("--skip-render", action="store_true", help="exports/_raw.mp4 已存在时跳过渲染")
    ap.add_argument("--no-score", action="store_true", help="不重新生成临时配乐，沿用已有 preview-mix.wav")
    ap.add_argument("--keep-raw", action="store_true")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    film = Path(a.film).resolve()
    ex = film / "exports"; ex.mkdir(exist_ok=True)
    up, pv, raw = ex / f"{a.name}-上传版-无配乐.mp4", ex / f"{a.name}-预览版-临时配乐.mp4", ex / "_raw.mp4"
    if (up.exists() or pv.exists()) and not (a.archive_old or a.overwrite):
        sys.exit("成片已存在：加 --archive-old v1 保留旧版，或加 --overwrite 覆盖。")

    # 1. build + fonts
    if (film / "scripts/build.mjs").exists():
        run(["node", "scripts/build.mjs"], film)
    elif (film / "scripts/net.mjs").exists():
        run(["node", "scripts/net.mjs"], film)
    if (film / "scripts/fonts.py").exists():
        run([sys.executable, "scripts/fonts.py"], film)
    html = (film / "index.html").read_text("utf-8")
    m = re.search(r'data-composition-id="main"[^>]*?data-duration="([\d.]+)"', html) or re.search(r'data-duration="([\d.]+)"', html)
    dur = float(m.group(1))
    print(f"片长 {dur:g} 秒", flush=True)

    # 2. lint
    r = subprocess.run(HF + ["lint"], cwd=film, capture_output=True, text=True)
    print((r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "lint: no output")
    errs = re.search(r"(\d+) error", r.stdout + r.stderr)
    if r.returncode or (errs and int(errs.group(1))):
        sys.exit("lint 有错误，先修好再渲染。\n" + (r.stdout + r.stderr)[-3000:])

    # 3. temp score
    mix = film / "assets/audio/preview-mix.wav"
    if not a.no_score and (film / "scripts/compose-score.py").exists():
        run([sys.executable, "scripts/compose-score.py"], film)
        run(["./scripts/render-score", "assets/audio/score.json", "assets/audio/score.wav", f"{dur:g}"], film)
        master(film / "assets/audio/score.wav", mix, dur)

    # 4. archive old exports
    if a.archive_old:
        for f in (up, pv):
            if f.exists():
                f.rename(ex / f.name.replace(f"{a.name}-", f"{a.name}-{a.archive_old}-", 1))

    # 5. render + encode
    if not (a.skip_render and raw.exists()):
        run(HF + ["render", "--fps", str(a.fps), "--workers", str(a.workers), "--quality", "delivery", "--output", "exports/_raw.mp4"], film)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw), "-c:v", "libx264", "-preset", "slow", "-crf", "20",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(up)], film)
    if mix.exists():
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(up), "-i", str(mix), "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-af", "apad", "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", str(pv)], film)

    # 6. verify
    report, ok = {}, True
    d, s = probe(up); report["upload"] = {"file": str(up), "seconds": round(d, 2), "audio": "audio" in s, "MB": round(up.stat().st_size / 1e6)}
    ok &= abs(d - dur) < 0.15 and "audio" not in s
    if pv.exists():
        d, s = probe(pv); ln = measure(pv)
        report["preview"] = {"file": str(pv), "seconds": round(d, 2), "audio": "audio" in s, "LUFS": float(ln["input_i"]), "dBTP": float(ln["input_tp"])}
        ok &= abs(d - dur) < 0.15 and "audio" in s
    if ok and not a.keep_raw and raw.exists():
        raw.unlink()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not ok:
        sys.exit("检查没通过：时长或音轨不对，原始渲染已保留在 exports/_raw.mp4。")
    print("完成。接着用 frame_sheet.py 从上传版抽帧检查。")


if __name__ == "__main__":
    main()
