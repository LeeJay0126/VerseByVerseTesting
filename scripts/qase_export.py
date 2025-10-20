#!/usr/bin/env python3
import os, sys, pathlib, requests, re, json

PROJECT = os.environ.get("QASE_PROJECT_CODE", "VERSEBYVER")
TOKEN   = os.environ.get("QASE_API_TOKEN")
if not TOKEN:
    print("ERROR: QASE_API_TOKEN is not set", file=sys.stderr)
    sys.exit(2)

ROOT    = pathlib.Path("qase_export")
OUT_MD  = ROOT / "cases"
OUT_JSON= ROOT / "raw"
OUT_MD.mkdir(parents=True, exist_ok=True)
OUT_JSON.mkdir(parents=True, exist_ok=True)

BASE = "https://api.qase.io/v1"
HEAD = {"X-Token": TOKEN, "Accept": "application/json"}  # Qase API auth

def slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9._ -]+", "", s or "").strip().replace(" ", "-")
    return s[:80] or "suite"

def get_json(url: str, **params):
    try:
        r = requests.get(url, headers=HEAD, params=params, timeout=30)
        if r.status_code != 200:
            print(f"ERROR: GET {url} -> HTTP {r.status_code}\n{r.text}", file=sys.stderr)
            sys.exit(3)
        return r.json()
    except requests.RequestException as e:
        print(f"ERROR: Request failed: {e}", file=sys.stderr)
        sys.exit(4)

def paginate(url: str):
    limit, offset = 100, 0
    while True:
        data = get_json(url, limit=limit, offset=offset)
        result = data.get("result") or {}
        # Qase typically uses "entities"; handle "items" just in case
        entities = result.get("entities") or result.get("items") or []
        total = int(result.get("total") or len(entities) or 0)
        for e in entities:
            yield e
        offset += limit
        if offset >= total:
            break

def norm_tags(raw):
    if not raw: return []
    if isinstance(raw, list):
        out = []
        for t in raw:
            if isinstance(t, str):
                out.append(t)
            elif isinstance(t, dict):
                out.append(t.get("title") or t.get("name") or t.get("value") or "")
        return [x for x in out if x]
    return [str(raw)]

# 1) Get all suites
suites = list(paginate(f"{BASE}/suite/{PROJECT}"))
suite_name = {s.get("id"): (s.get("title") or f"Suite-{s.get('id')}") for s in suites if s.get("id") is not None}

# 2) Fetch all cases (paginated)
cases = list(paginate(f"{BASE}/case/{PROJECT}"))

# 3) Save raw JSON
(OUT_JSON / "suites.json").write_text(json.dumps(suites, indent=2), encoding="utf-8")
(OUT_JSON / "cases.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")

# 4) Group by suite and render Markdown
by_suite = {}
for c in cases:
    sid = c.get("suite_id") or 0
    by_suite.setdefault(sid, []).append(c)

index_lines = ["# Qase Export — Test Cases", "", "## Suites"]

for sid, items in sorted(by_suite.items(), key=lambda kv: suite_name.get(kv[0], f"Suite-{kv[0]}")):
    sname = suite_name.get(sid, "No Suite")
    sslug = slug(sname)
    md_path = OUT_MD / f"{sslug}.md"
    index_lines.append(f"- [{sname}](cases/{md_path.name}) ({len(items)})")

    lines = [
        f"# {sname}",
        "",
        f"_Suite ID: {sid}_",
        "",
        "| ID | Title | Priority | Status |",
        "|---:|-------|---------|--------|"
    ]

    for c in sorted(items, key=lambda x: x.get("id", 0)):
        cid = c.get("id", 0)
        title = (c.get("title") or "").replace("\n"," ")
        prio  = c.get("priority") or ""
        status= c.get("status") or ""
        lines.append(f"| C{cid} | {title} | {prio} | {status} |")

    lines += ["", "## Details"]

    for c in sorted(items, key=lambda x: x.get("id", 0)):
        cid   = c.get("id", 0)
        title = c.get("title") or ""
        pre   = (c.get("preconditions") or "").strip()
        steps = (c.get("steps") or "").strip()
        exp   = (c.get("expected_result") or "").strip()
        tags  = ", ".join(norm_tags(c.get("tags"))) or "—"

        lines += [
            f"### C{cid}: {title}",
            "",
            f"- **Priority:** {c.get('priority','')}",
            f"- **Severity:** {c.get('severity','')}",
            f"- **Status:** {c.get('status','')}",
            f"- **Type:** {c.get('type','')}",
            f"- **Behavior:** {c.get('behavior','')}",
            f"- **Layer:** {c.get('layer','')}",
            f"- **Tags:** {tags}",
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

(ROOT / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

print(f"OK: Exported {len(suites)} suites and {len(cases)} cases to {ROOT}/")
