# VerseByVerseTesting — QA Test Plan (Draft)

> Scope: Navigation & Reading, Search, Versions, State, API & Error Handling, Accessibility, Performance/UX, Responsiveness/Cross-browser

## 1) Goals
- Ensure reliable Book → Chapter → Verse navigation and search flows
- Preserve reading location when switching Bible versions
- Protect the user experience under network variability (errors, offline, latency)
- Meet core accessibility and responsive-layout expectations

## 2) Test Suites (Qase structure)
- 00. Smoke
- 10. Navigation & Reading
- 20. Search & Filters
- 30. Versions
- 40. State (Bookmarks/History/Local Storage)
- 50. API & Errors
- 60. Accessibility
- 70. Performance/UX
- 80. Responsiveness & Cross-browser
- 90. Regression

## 3) Entry/Exit Criteria
**Entry**: Feature-complete build or release candidate tag, test env and accounts ready  
**Exit**: No open P0/P1 defects. Remaining lower-severity items documented in release notes.

## 4) Tooling
- Test cases: Qase (CSV import or API)  
- API tests: Postman collection (JSON schema checks & SLA assertions)  
- E2E: Playwright (chromium/firefox/webkit, video/screenshot artifacts)  
- CI: GitHub Actions (matrix, parallel runs, artifact upload)  
- A11y/Perf: Lighthouse, axe

## 5) How to Import to Qase
- Import `verse_by_verse_qase_cases_en.csv` via **Import → CSV** in your Qase project (field mapping: Title→Title, Steps→Steps, Expected→Expected, Priority→Priority, Suite→Suite, Tags→Tags, Type→Type, Layer→Layer, Automation→Automation, Preconditions→Preconditions).
- Adjust custom-field mapping if your workspace uses different names.

## 6) Smoke Checklist (summary)
- App load / modal / navigation / search / version switch / keyboard-only flow / state restore / error banner / mobile layout / duplicate-call avoidance / Lighthouse / external links

## 7) Automation (suggested)
- `smoke.spec`: Load → open modal → reach John 3:16  
- `search.spec`: Reference search 'John 3:16' → focus passage  
- `version.spec`: Switch version while preserving verse & highlight  
- `error.spec`: Mock network failure → verify retry path

## 8) Reporting
- Track defects in Jira (or GitHub Issues) with repro steps, expected vs. actual, screenshots/logs  
- CI artifacts: Playwright videos, screenshots, and HTML report

---

> Note: This is a draft. Tweak cases to match actual routes, storage keys, API endpoints, and share-link format.
