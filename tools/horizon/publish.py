"""把 Horizon 当天的中文摘要转成 Hugo 的 content/digest/YYYY-MM-DD.md。"""
import re
import sys
from pathlib import Path

src_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
summaries = sorted(src_dir.glob("horizon-????-??-??-zh.md"))
if not summaries:
    print(f"no summary in {src_dir}; skip")
    sys.exit(0)

src = summaries[-1]
date = src.name.removeprefix("horizon-").removesuffix("-zh.md")
text = re.sub(r"\A# .*\n+", "", src.read_text(encoding="utf-8"))  # 去 H1，页面自己渲染标题

out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / f"{date}.md"
out.write_text(
    f"+++\ntitle = 'Horizon 简报 · {date}'\ndate = {date}\n+++\n\n{text}",
    encoding="utf-8",
)
print(f"wrote {out}")
