#!/usr/bin/env python3
import os, pathlib, requests, math, re, json

PROJECT = os.environ.get("QASE_PROJECT_CODE", "VERSEBYVER")
TOKEN   = os.environ["QASE_API_TOKEN"]  # set in GH Actions secret
ROOT    = pathlib.Path("qase_export")
OUT_MD  = ROOT / "cases"
OUT_JSON= ROOT / "raw"

OUT_MD.mkdir(parents=True, exist_ok=True)
OUT_JSON.mkdir(parents=True, exist_ok=True)

BASE = "https://api.qase.io/v1"
HEAD = {"X-Token": TOKEN, "Accept": "application/json"}  # Qase API auth

def slug(s):
    s = re.sub(r"[^A-Za-z0-9._ -]+", "", s).strip().replace(" ", "-")
    return s[:80] or "suite"

def paginate(url, params=None):
    params = dict(params or {})
    limit, offset = 100, 0
    while True:
        p = {**params, "limit": limit, "offset": offset}
        r = requests.get(url, headers=HEAD, params=p, timeout=30)
        r.raise_for_status()
        data = r.json()
        yield from data.get("result", {}).get("entities", [])
        total = data.get("result", {}).get("total", 0)
        offset += limit
        if offset >= total:
            break

# 1) Get all suites
suites = list(paginate(f"{BASE}/suite/{PROJECT}"))

# Index for suite id → name
suite_name = {s["id"]: s.get("title", f"Suite-{s['id']}") for s in suites}

# 2) Fetch all cases (paginated)
cases = list(paginate(f"{BASE}/case/{PROJECT}"))

# 3) Save raw JSON (optional for diffs)
(OUT_JSON / "suites.json").write_text(json.dumps(suites, indent=2), encoding="utf-8")
(OUT_JSON / "cases.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")

# 4) Group by suite and render Markdown
by_suite = {}
for c in cases:
    sid = c.get("suite_id") or 0
    by_suite.setdefault(sid, []).append(c)

index_lines = ["# Qase Export — Test Cases\n", "", "## Suites"]

for sid, items in sorted(by_suite.items(), key=lambda kv: suite_name.get(kv[0], "")):
    sname = suite_name.get(sid, "No Suite")
    sslug = slug(sname)
    md_path = OUT_MD / f"{sslug}.md"
    index_lines.append(f"- [{sname}](cases/{md_path.name}) ({len(items)})")
    lines = [f"# {sname}", "", f"_Suite ID: {sid}_", "", "| ID | Title | Priority | Status |",
             "|---:|-------|---------|--------|"]
    for c in sorted(items, key=lambda x: x.get("id", 0)):
        cid = c["id"]
        title = c.get("title","").replace("\n"," ")
        prio  = c.get("priority","")
        status= c.get("status","")
        lines.append(f"| C{cid} | {title} | {prio} | {status} |")
    lines += ["", "## Details"]
    for c in sorted(items, key=lambda x: x.get("id", 0)):
        cid = c["id"]
        title = c.get("title","")
        pre   = (c.get("preconditions") or "").strip()
        steps = (c.get("steps") or "").strip()
        exp   = (c.get("expected_result") or "").strip()
        tags  = ", ".join(c.get("tags", []) or [])
        lines += [
            f"### C{cid}: {title}",
            "",
            f"- **Priority:** {c.get('priority','')}",
            f"- **Severity:** {c.get('severity','')}",
            f"- **Status:** {c.get('status','')}",
            f"- **Type:** {c.get('type','')}",
            f"- **Behavior:** {c.get('behavior','')}",
            f"- **Layer:** {c.get('layer','')}",
            f"- **Tags:** {tags or '—'}",
            "",
            "**Preconditions**",
            "",
            pre or "—",
            "",
            "**Steps**",
            "",
            "```\n" + (steps or "—") + "\n```",
            "",
            "**Expected result**",
            "",
            exp or "—",
            ""
        ]
    md_path.write_text("\n".join(lines), encoding="utf-8")

# 5) Write top-level index
(ROOT / "README.md").write_text("\n".join(index_lines)+ "\n", encoding="utf-8")

print(f"Exported {len(suites)} suites and {len(cases)} cases to {ROOT}/")
