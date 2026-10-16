#!/usr/bin/env python3
"""Create a portable episode plan; optionally copy an explicitly supplied engine."""
import argparse
import datetime
import re
import shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--title", required=True)
    ap.add_argument("--output", type=Path, default=Path("episodes"))
    ap.add_argument("--base-dir", type=Path)
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", a.slug):
        ap.error("slug must contain lowercase letters, digits and hyphens only")
    if a.base_dir and not a.base_dir.is_dir():
        ap.error("--base-dir must be an existing directory")
    date = datetime.date.today().isoformat()
    ep = a.output.resolve() / f"{date}-vibe-{a.slug}"
    if ep.exists():
        ap.error(f"Refusing to overwrite: {ep}")
    if a.base_dir and (ep == a.base_dir.resolve() or a.base_dir.resolve() in ep.parents):
        ap.error("Output must not be inside the source engine")
    ep.mkdir(parents=True)
    film = ep / "film"
    if a.base_dir:
        shutil.copytree(a.base_dir, film, ignore=shutil.ignore_patterns(".git", "node_modules", "exports", "qa", ".env", ".env.*", "*.pem", "*.key", ".DS_Store"))
    else:
        film.mkdir()
    (film / "exports").mkdir(exist_ok=True)
    values = {"标题": a.title, "日期": date, "名字": a.slug, "base": "用户提供工程" if a.base_dir else "待制作", "源文件": "自己的工程源文件"}
    for src, dst in [("PLAN.md", ep / "PLAN.md"), ("README-film.md", film / "README.md")]:
        text = (SKILL / "templates" / src).read_text()
        for key, value in values.items():
            text = text.replace("{" + key + "}", value)
        dst.write_text(text)
    print(f"Created {ep}; edit PLAN.md, then implement the film. No engine is bundled.")
if __name__ == "__main__":
    main()
