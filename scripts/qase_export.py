#!/usr/bin/env python3
import os, sys, pathlib, requests, re, json

PROJECT = os.environ.get("QASE_PROJECT_CODE", "VERSEBYVER")
TOKEN   = os.environ.get("QASE_API_TOKEN", "")
BASE    = os.environ.get("QASE_API_BASE", "https://api.qase.io/v1")

print(f"[debug] PROJECT={PROJECT}")
print(f"[debug] QASE_API_BASE={BASE}")
print(f"[debug] QASE_API_TOKEN length={len(TOKEN)}")

if not TOKEN:
    print("ERROR: QASE_API_TOKEN is not set", file=sys.stderr)
    sys.exit(2)

ROOT    = pathlib.Path("qase_export")
OUT_MD  = ROOT / "cases"
OUT_JSON= ROOT / "raw"
OUT_MD.mkdir(parents=True, exist_ok=True)
OUT_JSON.mkdir(parents=True, exist_ok=True)

# IMPORTANT: Qase expects header name 'Token' for auth
HEAD = {"Token": TOKEN, "Accept": "application/json"}

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

def render_steps(steps_field):
    """
    Qase returns either:
      - string
      - list of step objects: { 'action': str, 'expected_result': str, 'data': str, ... }
    Return a markdown block (string).
    """
    if not steps_field:
        return "—"
    # If it's already a string
    if isinstance(steps_field, str):
        return steps_field.strip() or "—"
    # If it's a list of steps
    if isinstance(steps_field, list):
        lines = []
        for i, s in enumerate(steps_field, 1):
            if not isinstance(s, dict):
                # fallback plain text
                lines.append(f"{i}. {str(s)}")
                continue
            action = (s.get("action") or "").strip()
            expected = (s.get("expected_result") or "").strip()
            data = (s.get("data") or "").strip()
            # Step title line
            title = action or "(no action provided)"
            lines.append(f"{i}. {title}")
            # Optional details indented
            if expected:
                lines.append(f"   - Expected: {expected}")
            if data:
                lines.append(f"   - Data: {data}")
        return "\n".join(lines) if lines else "—"
    # Any other unexpected type
    return str(steps_field)

# 1) Get all suites
suites = list(paginate(f"{BASE}/suite/{PROJECT}"))
suite_name = {s.get("id"): (s.get("title") or f"Suite-{s.get('id')}") for s in suites if s.get("id") is not None}

# 2) Fetch all cases
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
        title = (c.get("title") or "").replace("\n", " ")
        prio  = c.get("priority") or ""
        status= c.get("status") or ""
        lines.append(f"| C{cid} | {title} | {prio} | {status} |")

    lines += ["", "## Details"]

    for c in sorted(items, key=lambda x: x.get("id", 0)):
        cid   = c.get("id", 0)
        title = c.get("title") or ""
        pre   = (c.get("preconditions") or "").strip() if isinstance(c.get("preconditions"), str) else ""
        steps_md = render_steps(c.get("steps"))
        exp   = c.get("expected_result")
        if isinstance(exp, list):
            # sometimes expected results are split per step; flatten
