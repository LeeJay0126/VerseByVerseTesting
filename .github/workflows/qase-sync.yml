name: Sync Qase test cases to repo (8am Vancouver)

on:
  workflow_dispatch:
  schedule:
    - cron: "0 * * * *"

concurrency:
  group: qase-sync
  cancel-in-progress: false

jobs:
  export:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    env:
      QASE_PROJECT_CODE: VERSEBYVER
      QASE_API_TOKEN: ${{ secrets.QASE_API_TOKEN }}
    steps:
      - id: now
        name: Determine local time
        shell: bash
        run: |
          HOUR=$(TZ=America/Vancouver date +%H)
          DATE=$(TZ=America/Vancouver date -Is)
          echo "hour=$HOUR" >> "$GITHUB_OUTPUT"
          echo "date=$DATE" >> "$GITHUB_OUTPUT"
          echo "Local time is $DATE"

      - name: Checkout
        if: steps.now.outputs.hour == '08'
        uses: actions/checkout@v4

      - name: Set up Python
        if: steps.now.outputs.hour == '08'
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        if: steps.now.outputs.hour == '08'
        shell: bash
        run: pip install requests

      - name: Sanitize token
        if: steps.now.outputs.hour == '08'
        shell: bash
        run: |
          printf "%s" "$QASE_API_TOKEN" | tr -d '\r\n' > token.txt
          echo "TOKEN_LEN=$(wc -c < token.txt) chars"

      - name: Preflight (token + project on US API)
        if: steps.now.outputs.hour == '08'
        id: probe
        shell: bash
        run: |
          test -s token.txt || { echo "::error::Missing or empty QASE_API_TOKEN"; exit 2; }
          [ -n "$QASE_PROJECT_CODE" ] || { echo "::error::Missing QASE_PROJECT_CODE"; exit 2; }
          TOKEN=$(cat token.txt)
          BASE="https://api.qase.io/v1"
          URL="$BASE/case/${QASE_PROJECT_CODE}?limit=1&offset=0"
          echo "Probing $URL"
          HTTP=$(curl -sS -o resp.json -w "%{http_code}" -H "X-Token: ${TOKEN}" "$URL")
          echo "HTTP=$HTTP"
          if [ "$HTTP" -eq 401 ] || [ "$HTTP" -eq 403 ]; then
            echo "::error::Unauthorized. The token user likely has no access to project '$QASE_PROJECT_CODE', or the project code is incorrect."
            echo "Tip: create a new token from a user who can open the project in Qase, then update the GitHub secret."
            cat resp.json || true
            exit 3
          fi
          [ "$HTTP" -eq 200 ] || { echo "::error::Qase API returned HTTP $HTTP"; cat resp.json; exit 3; }
          echo "base=$BASE" >> "$GITHUB_OUTPUT"

      - name: Export from Qase
        if: steps.now.outputs.hour == '08'
        shell: bash
        env:
          QASE_API_BASE: ${{ steps.probe.outputs.base }}
        run: |
          export QASE_API_BASE="${QASE_API_BASE:-https://api.qase.io/v1}"
          export QASE_API_TOKEN="$(cat token.txt)"
          python scripts/qase_export.py

      - name: Show export tree
        if: steps.now.outputs.hour == '08'
        shell: bash
        run: |
          echo "--- qase_export ---"
          find qase_export -maxdepth 2 -type f -print | sort || true
          echo "--- git status ---"
          git status --porcelain

      - name: Commit changes
        if: steps.now.outputs.hour == '08'
        shell: bash
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add qase_export
          git commit -m "chore(qase): daily sync at 08:00 America/Vancouver" || echo "No changes"
          git push
