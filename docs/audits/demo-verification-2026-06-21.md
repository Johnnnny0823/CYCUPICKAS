# Demo Verification Audit - 2026-06-21

## Scope
本次只驗證本機 FAKE HTML Demo：`http://localhost:8765/demo/fake_selection_system.html`。
真實 itouch 頁面注入已停用，不列入展示流程。

## Automated Checks
- `node --check extension/content.js`: passed
- `node --check demo/fake_selection_system.js`: passed
- `python -m json.tool extension/manifest.json`: passed
- `python -m unittest discover -s tests`: passed, 4 tests
- `python tools/validate_course_summaries.py extension/data/course_summaries_itouch.json`: passed with grading warnings
- `python tools/verify_demo_contract.py`: passed

## Demo Contract Evidence
- Full course seed rows: 58
- Summary matches: 58 / 58
- Grade filter coverage:
  - 大一: 15
  - 大二: 16
  - 大三: 20
  - 大四: 7
- Extension manifest matches only:
  - `http://localhost:*/*`
  - `http://127.0.0.1:*/*`
  - `file:///*`

## Verified Behaviors By Static And Contract Checks
1. Demo page loads full `course_seed_itouch.json` data.
2. Course rows expose `data-course-code` for extension matching.
3. Extension merges `course_summaries.json` and `course_summaries_itouch.json`.
4. AI summary button and collapsible card code are present.
5. Compare flow uses a small launcher and modal, not a permanent bottom panel.
6. AI filters include `沒報告`, `沒考試`, `沒作業`, and `課綱已解析`.
7. Manifest no longer injects into itouch or CYCU real pages.
8. Documents now point to port `8765`; fallback port is `8766`.

## Screenshot Audit Limit
Product Design screenshot audit could not be completed in this environment:
- Browser tool was unavailable.
- Node REPL failed before Playwright could run.
- Local shell reported Playwright missing.
- Chrome/Edge CLI was not found in PATH.

Manual browser smoke test still recommended after loading the extension in Chrome.

## Computer Use Retry - 2026-06-21
User requested retry with `@電腦` / Computer Use. The plugin skill was loaded and the official bootstrap path was attempted again, including `js_reset`. The Node REPL entry point still failed with:

```text
Mcp error: -32602: js: codex/sandbox-state-meta: missing field `sandboxPolicy`
```

No Windows browser interaction was performed through Computer Use.
