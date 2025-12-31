# ChessBI Runbook

## TL;DR - Quick Start

```powershell
# 1. Setup
git clone https://github.com/mariamji19-DataFairy/ChessBI.git && cd ChessBI
python -m venv .venv && .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Prepare sample dataset
python scripts/prepare_dataset.py --input data/raw/archive/games.csv --out data/sample/games_sample.csv --rows 2000

# 3. Load into DuckDB
python warehouse/load_duckdb.py --db warehouse/chessbi.duckdb --source sample

# 4. Build dbt models
cd dbt && dbt build && cd ..
```

**Result**: All 18 dbt tests passing, analytics layer ready for querying.

---

## Full Runbook

This runbook provides step-by-step commands for common operations. All commands assume you're in the project root directory with the virtual environment activated.

## Prerequisites

```powershell
# Clone repository
git clone https://github.com/mariamji19-DataFairy/ChessBI.git
cd ChessBI

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pandas, duckdb, requests; print('✓ All dependencies installed')"
```

**Expected output:**
```
✓ All dependencies installed
```

## Step 1: Prepare Sample Dataset

**Purpose:** Create a small committed dataset (2000 rows) for CI testing and quick iteration.

```powershell
# Generate sample from full dataset
python scripts/prepare_dataset.py `
  --input data/raw/archive/games.csv `
  --out data/sample/games_sample.csv `
  --rows 2000
```

**Expected output:**
```
Dataset prepared successfully!
  Input:  data/raw/archive/games.csv (20058 rows)
  Output: data/sample/games_sample.csv (2000 rows)
  Columns: 11
```

**Common errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError: data/raw/archive/games.csv` | Full dataset not present | Download dataset or use existing sample |
| `Missing required column: game_id` | CSV schema mismatch | Verify CSV has required columns (see script) |
| `ValueError: rows must be positive` | Invalid `--rows` argument | Use positive integer (e.g., 2000) |

**Validation:**
```powershell
# Check output file exists and has correct row count
python -c "import pandas as pd; df = pd.read_csv('data/sample/games_sample.csv'); print(f'Rows: {len(df)}'); print(f'Columns: {list(df.columns)}')"
```

## Step 2: Load Data into DuckDB

**Purpose:** Import CSV data into DuckDB warehouse for querying and transformation.

```powershell
# Load from sample dataset (for CI or quick testing)
python warehouse/load_duckdb.py `
  --db warehouse/chessbi.duckdb `
  --source sample

# Load from full dataset (for local development)
python warehouse/load_duckdb.py `
  --db warehouse/chessbi.duckdb `
  --source raw
```

**Expected output:**
```
Source mode: sample
Input CSV: data/sample/games_sample.csv
Creating database at: warehouse/chessbi.duckdb
Database loaded successfully.
  Rows in raw_games: 2000
```

**What this creates:**
- `raw_games` table: Exact copy of CSV with inferred types
- `raw_games_clean` view: Standardized column names and types (timestamp conversion)

**Common errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError: data/sample/games_sample.csv` | Sample dataset missing | Run `prepare_dataset.py` first |
| `ParserError: Error tokenizing data` | Malformed CSV | Check CSV for formatting issues |
| `TypeError: epoch_ms() requires BIGINT` | Wrong created_at type | Verify CSV has numeric timestamps |

**Validation:**
```powershell
# Query database to verify data loaded
python -c "import duckdb; con = duckdb.connect('warehouse/chessbi.duckdb'); print(con.sql('SELECT COUNT(*) as total, winner, COUNT(*)/SUM(COUNT(*)) OVER() as pct FROM raw_games_clean GROUP BY winner').fetchall())"
```

**Expected output (for 2000-row sample):**
```
[(958, 'black', 0.479), (940, 'white', 0.47), (102, 'draw', 0.051)]
```

## Step 3: Test dbt Connection

**Purpose:** Verify dbt can connect to DuckDB before building models.

```powershell
# Change to dbt directory
cd dbt

# Test connection
dbt debug

# Return to project root
cd ..
```

**Expected output:**
```
10:26:50  Running with dbt=1.8.8
10:26:50  Registered adapter: duckdb=1.8.3
...
10:26:50  Connection test: [OK connection ok]
10:26:50  All checks passed!
```

**Common errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `Runtime Error: Could not find profile named 'chessbi'` | Wrong directory or missing profiles.yml | Ensure `profiles.yml` exists in `dbt/` |
| `Database Error: no such table: raw_games_clean` | DuckDB not loaded | Run `load_duckdb.py` first |
| `OperationalError: no such file: ../warehouse/chessbi.duckdb` | Database path incorrect | Check path in `profiles.yml` |

## Step 4: Build dbt Models

**Purpose:** Run SQL transformations to create staging tables and marts.

```powershell
# Change to dbt directory
cd dbt

# Build all models and run tests
dbt build

# Return to project root
cd ..
```

**Expected output:**
```
10:50:43  Running with dbt=1.8.8
10:50:43  Found 5 models, 13 data tests, 1 source, 416 macros
10:50:43  
10:50:43  Concurrency: 4 threads (target='dev')
...
10:50:43  Completed successfully
10:50:43  Done. PASS=18 WARN=0 ERROR=0 SKIP=0 TOTAL=18
```

**What this creates:**

| Object | Type | Description |
|--------|------|-------------|
| `stg_games` | View | Cleaned games with deduplication |
| `fact_games` | Table | One row per game (fact table) |
| `dim_player` | Table | Unique players dimension |
| `dim_opening` | Table | Chess openings with surrogate key |
| `dim_time_control` | Table | Time control categories |

**Data tests run:**
- 3 tests on `stg_games` (unique game_id, not null, valid result_label)
- 2 tests on `fact_games` (unique game_id, not null)
- 2 tests on `dim_player` (unique player_id, not null)
- 3 tests on `dim_opening` (unique opening_key, not null ECO, not null key)
- 3 tests on `dim_time_control` (unique time_control_raw, not null, valid category)

**Common errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `Compilation Error: Model 'stg_games' depends on source 'raw.raw_games' which was not found` | Source not defined | Check `models/sources.yml` |
| `FAIL 3 unique_stg_games_game_id` | Duplicate game IDs in source | Check deduplication logic in `stg_games.sql` |
| `Database Error: Catalog Error: Table with name "raw_games_clean" does not exist!` | Database not loaded | Run `load_duckdb.py` first |

**Incremental commands:**
```powershell
# Run only models (skip tests)
dbt run

# Run only tests
dbt test

# Run specific model and dependencies
dbt build --select stg_games+

# Run specific model and downstream
dbt build --select +fact_games
```

**Validation:**
```powershell
# Query built models to verify
python -c "import duckdb; con = duckdb.connect('warehouse/chessbi.duckdb'); print('Fact table rows:', con.sql('SELECT COUNT(*) FROM main.fact_games').fetchone()[0]); print('Unique players:', con.sql('SELECT COUNT(*) FROM main.dim_player').fetchone()[0]); print('Unique openings:', con.sql('SELECT COUNT(*) FROM main.dim_opening').fetchone()[0])"
```

**Expected output (for 2000-row sample):**
```
Fact table rows: 1997
Unique players: 1129
Unique openings: 117
```

## Step 5: Evidence Dashboard (Placeholder)

**Purpose:** Generate interactive dashboards from dbt models.

**Setup (once):**
```powershell
# Install Evidence CLI (requires Node.js)
npm install -g @evidence-dev/cli

# Initialize Evidence project
cd dashboard
evidence init
```

**Development:**
```powershell
# Start development server
cd dashboard
evidence dev
```

**Build for production:**
```powershell
# Generate static site
cd dashboard
evidence build

# Output: dashboard/build/ contains static HTML/CSS/JS
```

**Expected output:**
```
🔍 Evidence development server running
📊 Dashboards available at http://localhost:3000
```

**Note:** Evidence integration is planned but not yet implemented. This section will be updated once dashboard development begins.

## Troubleshooting

### Virtual Environment Issues

**Problem:** Commands fail with `ModuleNotFoundError`

**Solution:**
```powershell
# Verify virtual environment is activated
python -c "import sys; print(sys.prefix)"
# Should print path ending in .venv

# If not activated:
.venv\Scripts\activate

# Reinstall dependencies if needed
pip install -r requirements.txt
```

### DuckDB Database Locked

**Problem:** `duckdb.IOException: Could not set lock on file`

**Solution:**
```powershell
# Close all connections to the database
# Check for Python processes holding locks
tasklist | findstr python

# Kill specific process if needed
taskkill /F /PID <process_id>

# Or simply restart the terminal
```

### dbt Compilation Errors

**Problem:** `Jinja template error` or `Compilation Error`

**Solution:**
```powershell
# Clean compiled artifacts
cd dbt
Remove-Item -Recurse -Force target/

# Try compile only (faster than build)
dbt compile

# Check specific model
dbt compile --select stg_games
```

### Git Line Ending Warnings

**Problem:** `warning: CRLF will be replaced by LF`

**Solution:**
```powershell
# Configure git to auto-convert (one-time)
git config --global core.autocrlf true

# Or ignore warnings (they're harmless)
```

## CI/CD Integration

**GitHub Actions workflow** (`.github/workflows/ci.yml`):

```yaml
- name: Load sample data
  run: python warehouse/load_duckdb.py --db warehouse/chessbi.duckdb --source sample

- name: Run dbt tests
  run: |
    cd dbt
    dbt debug
    dbt build
```

**Key points:**
- CI uses `--source sample` (2000 rows) for fast testing
- Full dataset (`--source raw`) is for local development only
- All dbt tests must pass before merge

## Quick Reference

```powershell
# Full workflow from scratch
python scripts/prepare_dataset.py --input data/raw/archive/games.csv --out data/sample/games_sample.csv --rows 2000
python warehouse/load_duckdb.py --db warehouse/chessbi.duckdb --source sample
cd dbt; dbt build; cd ..

# Reset everything
Remove-Item warehouse/chessbi.duckdb
Remove-Item -Recurse -Force dbt/target/

# Check data quality
python -c "import duckdb; con = duckdb.connect('warehouse/chessbi.duckdb'); print(con.sql('SELECT * FROM main.fact_games LIMIT 5').df())"
```
