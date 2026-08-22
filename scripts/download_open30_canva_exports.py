"""Download Composio Canva export URLs into open30 asset folder."""
from __future__ import annotations

import json
import shutil
import urllib.request
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
OUT = PROJECT / "assets" / "canva" / "kinetic" / "infographics" / "open30"
REPORT = PROJECT / "renders" / "quality" / "open30_canva_export_report.json"

EXPORTS = [
    ("https://export-download.canva.com/AbXzM/DAHSJzAbXzM/-1/0/0001-4827245464172244010.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQYCGKMUH5AO7UJ26%2F20260812%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260812T224225Z&X-Amz-Expires=56480&X-Amz-Signature=21cbe16090c68f2d6e45e789a0965a5896ed2950885141590e3aeddd7dab08b2&X-Amz-SignedHeaders=host%3Bx-amz-expected-bucket-owner&response-expires=Thu%2C%2013%20Aug%202026%2014%3A23%3A45%20GMT",
     "open30_01_stat.png", "DAHSJzAbXzM"),
    ("https://export-download.canva.com/Y1PC0/DAHSJ2Y1PC0/-1/0/0001-1894276206504438245.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQYCGKMUH5AO7UJ26%2F20260813%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260813T042210Z&X-Amz-Expires=35189&X-Amz-Signature=e9f53652cb3e53d1b327444ced4ae1a00076ba07619e9c5a741712f4d15433e2&X-Amz-SignedHeaders=host%3Bx-amz-expected-bucket-owner&response-expires=Thu%2C%2013%20Aug%202026%2014%3A08%3A39%20GMT",
     "open30_05_stat.png", "DAHSJ2Y1PC0"),
    ("https://export-download.canva.com/xs1ls/DAHSJzxs1ls/-1/0/0001-1776056718326817870.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQYCGKMUH5AO7UJ26%2F20260813%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260813T000459Z&X-Amz-Expires=53306&X-Amz-Signature=a5841480759aa02caad564a3f3bbb82232db133095b128a2ec17fe1960ad49a8&X-Amz-SignedHeaders=host%3Bx-amz-expected-bucket-owner&response-expires=Thu%2C%2013%20Aug%202026%2014%3A53%3A25%20GMT",
     "open30_07_paths.png", "DAHSJzxs1ls"),
    ("https://export-download.canva.com/Y5FQc/DAHSJwY5FQc/-1/0/0001-3838705347476054175.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQYCGKMUH5AO7UJ26%2F20260813%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260813T064346Z&X-Amz-Expires=29255&X-Amz-Signature=0dcfbb25b7ad49f22fb0459144c1e17d266f8dc0c1991f33c9aaa1d2996b3aa0&X-Amz-SignedHeaders=host%3Bx-amz-expected-bucket-owner&response-expires=Thu%2C%2013%20Aug%202026%2014%3A51%3A21%20GMT",
     "open30_09_title.png", "DAHSJwY5FQc"),
]

UA = {"User-Agent": "AfricaS1Open30/1.0"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log = []
    for url, fname, design_id in EXPORTS:
        dest = OUT / fname
        bak = OUT / f"{fname}.matplotlib.bak"
        if dest.is_file() and not bak.is_file():
            shutil.copy2(dest, bak)
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as out:
            shutil.copyfileobj(resp, out)
        log.append({"design": design_id, "file": str(dest), "bytes": dest.stat().st_size})
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print("CANVA_SAVED", len(log))


if __name__ == "__main__":
    main()
