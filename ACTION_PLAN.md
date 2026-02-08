# Action Plan – Minervini SEPA Scanner Improvements

Use this plan to review and execute improvements in order. Phases are sequential; tasks within a phase can often be done in any order. Mark items **Optional** if you want to skip them. After you review and approve, execute Phase 1 first, then 2, etc.

---

## Pipelines (How to Run Everything)

Two pipelines are available:

| Pipeline | Script | What it does |
|----------|--------|--------------|
| **Full** | `run_full_pipeline.ps1` | Fetches fresh data (01), then generates report (02), runs ChatGPT validation (03), and position suggestions (05). Use when you want completely fresh data and reports. |
| **Latest data** | `run_latest_data_pipeline.ps1` | Uses existing cached data only: generates report (02), ChatGPT validation (03), and position suggestions (05). No fetch. Use when data was already fetched and you only want updated reports. |

**Steps:**

- **Pipeline 1 – Full:** `01_fetch_stock_data.py` → `02_generate_full_report.py` → `03_chatgpt_validation.py` → `05_position_suggestions.py`
- **Pipeline 2 – Latest data:** `02_generate_full_report.py` → `03_chatgpt_validation.py` → `05_position_suggestions.py` (requires `data/cached_stock_data.json` from a previous run of 01)

**How to run:**

```powershell
# Full pipeline (fetch + report + ChatGPT + position suggestions)
.\run_full_pipeline.ps1

# Latest-data pipeline (report + ChatGPT + position suggestions, no fetch)
.\run_latest_data_pipeline.ps1
```

---

## Phase 1: Documentation and Single Source of Truth (Low Risk)

**Goal:** README and project structure reflect how you actually run the project; new users see the right commands.

| # | Task | Details |
|---|------|--------|
| 1.1 | **Update README – pipeline** | Replace all `main.py` examples with the real pipeline. Document both: **Full** (01 → 02 → 03 → 05) and **Latest data** (02 → 03 → 05). Add a "Quick start" that says: run `run_full_pipeline.ps1` for everything including fetch, or `run_latest_data_pipeline.ps1` to use existing cache. |
| 1.2 | **Update README – project structure** | In the "Project structure" section, list the real scripts: `01_fetch_stock_data.py`, `02_generate_full_report.py`, `03_chatgpt_validation.py`, `04_retry_failed_stocks.py`, `05_position_suggestions.py`, plus `bot.py`, `minervini_scanner.py`, `data_provider.py`, `config.py`, etc. Remove or correct any reference to `main.py`. |
| 1.3 | **Align config.example.env** | Change Alpha Vantage wording from "REQUIRED" to "Optional" (or "Optional – for additional coverage") so it matches README and code (yfinance primary). |

**Done when:** README describes the 01–05 workflow and correct file list; example env doesn't claim Alpha Vantage is required.

---

## Phase 2: Centralize Paths and Cache Helpers (Medium Risk, High Value)

**Goal:** One place for cache path, report paths, and load/save cache logic so 01/02/03/04 stay in sync.

| # | Task | Details |
|---|------|--------|
| 2.1 | **Add shared paths (and optional cache helpers)** | In `config.py` (or a new `paths.py`), define: `CACHE_FILE`, `REPORTS_DIR`, `SCAN_RESULTS_LATEST`, and optionally `POSITION_REPORTS_DIR` if you want it there. Keep `position_suggestions_config.py` as-is for now if it already defines `POSITION_REPORTS_DIR`; otherwise import from the shared place. |
| 2.2 | **Add shared cache helpers** | In `config.py` or a new small module (e.g. `cache_utils.py`), add: `load_cached_data()` and `save_cached_data(data)` with a single, clear contract (e.g. return `None` or raise if cache missing; same JSON shape everywhere). |
| 2.3 | **Switch 01 to shared path + helpers** | In `01_fetch_stock_data.py`: remove local `CACHE_FILE` and local `load_cached_data` / `save_cached_data`; import from the shared module and use it. Run 01 once to confirm cache still works. |
| 2.4 | **Switch 02 to shared path + helpers** | In `02_generate_full_report.py`: remove local `CACHE_FILE`, `REPORTS_DIR`, `SCAN_RESULTS_LATEST` and local `load_cached_data`; import from shared module. Run 02 on existing cache to confirm. |
| 2.5 | **Switch 03 to shared path + helpers** | In `03_chatgpt_validation.py`: remove local `REPORTS_DIR`, `SCAN_RESULTS_LATEST` and local `load_cached_data`; import from shared module. Run 03 to confirm. |
| 2.6 | **Switch 04 to shared path + helpers** | In `04_retry_failed_stocks.py`: remove local `CACHE_FILE`, `load_cached_data`, `save_cached_data`; import from shared module. Run 04 (dry run or small retry) to confirm. |

**Done when:** All four scripts use the same `CACHE_FILE`, `load_cached_data`, and `save_cached_data`; no duplicated cache logic.

---

## Phase 3: Fix Warnings and Error Handling (Low–Medium Risk)

**Goal:** No FutureWarnings from pandas; no bare `except:`; failures are visible in logs.

| # | Task | Details |
|---|------|--------|
| 3.1 | **Fix pd.to_datetime in 02** | In `02_generate_full_report.py`, wherever you do `pd.to_datetime(hist_dict["index"])` (and similar for date columns), add `utc=True` if you want UTC, or document that indices are timezone-naive and use a single consistent pattern. Re-run 02 and check that the FutureWarning is gone. |
| 3.2 | **Replace bare except in 02** | In `02_generate_full_report.py`, replace each `except:` with `except Exception as e:` and log `e` (e.g. `logger.warning("...", exc_info=True)` or `logger.debug(...)`). Keep the same behavior (e.g. fallback timestamp or skip). |
| 3.3 | **Replace bare except in 04** | In `04_retry_failed_stocks.py`, replace the bare `except:` (e.g. around `fetched_at` parsing) with `except Exception as e:` and log it. Optionally re-raise if it's unexpected. |

**Done when:** 02 runs without pandas FutureWarning; all former bare `except:` blocks log the exception and use a clear fallback.

---

## Phase 4: Workflow Script and 05 (Low Risk)

**Goal:** One command or script runs the full pipeline; 05 is part of the "official" workflow.

| # | Task | Details |
|---|------|--------|
| 4.1 | **Extend run_full_workflow.ps1** | Document at the top that **01 must be run first** (or run 01 inside the script with a long timeout). After 02 and 03, add a step that runs **05_position_suggestions.py**. On success, print where the position suggestions report was saved. |
| 4.2 | **Optional: all-in-one runner** | (Optional) Add a small script (e.g. `run_pipeline.py` or `run_all.ps1`) that runs 01 → 02 → (03 if desired) → 05 in order, with simple error handling (e.g. exit on first failure, or continue and report which step failed). |

**Done when:** Running "full workflow" clearly includes 01 and 05; you have one place to run the whole pipeline.

---

## Phase 5: 04 Retry Script Robustness (Optional, Medium Value)

**Goal:** 04 doesn't depend on importlib loading 01's internals; shared fetch logic is explicit.

| # | Task | Details |
|---|------|--------|
| 5.1 | **Refactor shared fetch logic** | In `01_fetch_stock_data.py`, ensure the "fetch one ticker" logic lives in a named function (e.g. `fetch_stock_data(ticker, bot)`) that returns the same dict shape you already use. |
| 5.2 | **04 uses explicit import** | In `04_retry_failed_stocks.py`, replace `importlib.util` loading of 01 with a normal import, e.g. `from importlib import import_module` and `fetch_module = import_module("01_fetch_stock_data")`, then call `fetch_module.fetch_stock_data(ticker, bot)`. Or move `fetch_stock_data` to a small shared module (e.g. `fetch_utils.py`) and import it from both 01 and 04. |

**Done when:** 04 runs without importlib on 01's file path and still retries failed tickers correctly.

---

## Phase 6: Minimal Tests (Optional, High Long-Term Value)

**Goal:** Catch regressions in ticker cleaning, actionability ranking, and "report still runs."

| # | Task | Details |
|---|------|--------|
| 6.1 | **Add tests directory and pytest** | Create `tests/` and add `requirements-dev.txt` or extend `requirements.txt` with `pytest>=7.0`. Add a minimal `tests/test_ticker_utils.py` with a few `clean_ticker()` and (if you like) `get_possible_ticker_formats()` cases. |
| 6.2 | **Test actionability sort** | Add `tests/test_summary_report.py` (or similar) that imports `actionability_sort_key` from `02_generate_full_report.py`, builds 1–2 fake scan result dicts with base_depth, volume_contraction, distance_to_buy_pct, rs_rating, and asserts the sort order. |
| 6.3 | **Smoke test 02 (and 05)** | Add a smoke test that loads `data/cached_stock_data.json` (if present), runs the 02 summary generation (or only the part that builds "TOP STOCKS" + "BEST SETUPS") on a small slice (e.g. first 5 stocks), and checks that the report text contains expected headers and no exception. Optionally do the same for 05 with a mock or no API. |

**Done when:** `pytest` runs and at least ticker_utils and actionability (and optionally smoke) tests pass; you can run tests before/after changes.

---

## Phase 7: Logging Idempotency (Optional, Low Priority)

**Goal:** Running 02 after 01 (or 04 invoking 01) doesn't duplicate log handlers.

| # | Task | Details |
|---|------|--------|
| 7.1 | **Make setup_logging idempotent** | In `logger_config.py`, at the start of `setup_logging()`, check if the root or `trading212_bot` logger already has the expected handlers (e.g. one file, one console). If so, skip adding again or clear and re-add once. Document that scripts may be run in the same process. |

**Done when:** Running 01 then 02 (or 04 then 01) doesn't double log lines.

---

## Execution Order (Summary)

1. **Phase 1** – Update README and config.example.env (no code behavior change).
2. **Phase 2** – Centralize paths and cache; update 01, 02, 03, 04 to use them; test each script.
3. **Phase 3** – Fix pandas and `except` in 02 and 04; re-run 02 to confirm no warning.
4. **Phase 4** – Update run_full_workflow.ps1 to include 01 and 05; optionally add run_pipeline script.
5. **Phase 5** – (Optional) Refactor 04 to use explicit import or shared fetch module.
6. **Phase 6** – (Optional) Add pytest and minimal tests.
7. **Phase 7** – (Optional) Make logging setup idempotent.

---

## Quick Checklist (Review Before Executing)

- [ ] I want Phase 1 (docs) – **recommended**
- [ ] I want Phase 2 (centralize cache/paths) – **recommended**
- [ ] I want Phase 3 (warnings + except) – **recommended**
- [ ] I want Phase 4 (workflow + 05) – **recommended**
- [ ] I want Phase 5 (04 refactor) – optional
- [ ] I want Phase 6 (tests) – optional
- [ ] I want Phase 7 (logging) – optional

---

## Notes (Edit as You Go)

Add your own notes, completion dates, or blockers here:

- 
