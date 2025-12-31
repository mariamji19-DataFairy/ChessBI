# Technology Stack

## TL;DR

- **DuckDB**: Embedded OLAP database (zero setup, git-committable, fast analytics)
- **dbt**: SQL transformations with built-in testing (industry standard for analytics)
- **Evidence**: Code-based dashboards (Markdown + SQL, version controlled)
- **Python**: API ingestion with retry/caching, data validation scripts
- **GitHub Actions**: Free CI/CD for automated testing

**Why valuable**: Demonstrates modern analytics patterns, zero cloud cost, skills transfer to Snowflake/BigQuery production stacks.

---

## Project Goals

ChessBI is designed as a **production-style analytics project** that demonstrates modern analytics engineering practices. The platform must be:

1. **Reproducible**: Anyone can clone, setup, and run locally in minutes
2. **Local-first**: No cloud dependencies or API keys required for core functionality
3. **Cost-effective**: Zero operational costs for development and demonstration
4. **CI-friendly**: Automated testing with fast feedback cycles
5. **Modern**: Uses current best practices in analytics engineering (2024-2025)

## Selection Criteria

Every tool in the stack was chosen based on:

- **Zero infrastructure overhead**: No servers, no cloud accounts, no credit cards
- **Fast iteration cycles**: Quick feedback during development
- **Industry relevance**: Skills transferable to production data teams
- **Git-compatible**: Full version control of code, config, and schema
- **Testing capability**: Supports automated quality checks in CI

## Technology Decisions

### Python (Ingestion + Scripts)

**Why:**
- Universal language for data engineering
- Rich ecosystem for API clients, CSV processing, data validation
- Native support in GitHub Actions
- Easy dependency management with `requirements.txt`

**Usage:**
- Chess.com/Lichess API ingestion with retry logic and ETag caching
- Dataset preparation scripts (sampling, validation)
- DuckDB loader with type inference

**Alternatives Considered:**
- **Node.js**: Better for web APIs but weaker data ecosystem
- **Go**: Faster but overkill for I/O-bound ingestion tasks
- **SQL-only**: Insufficient for API calls and complex logic

### DuckDB (Warehouse)

**Why:**
- **Embedded**: Single file database, no server process needed
- **Fast**: OLAP-optimized with columnar storage and vectorized execution
- **Portable**: Database file commits to git (under size limits)
- **SQL-compatible**: Standard SQL with PostgreSQL extensions
- **dbt support**: First-class integration via `dbt-duckdb`

**Usage:**
- Local warehouse stored in `warehouse/chessbi.duckdb`
- Sample dataset (2000 rows) committed for CI testing
- Full dataset (20k+ rows) used locally, gitignored

**Alternatives Considered:**
- **PostgreSQL**: Requires server installation, harder local setup
- **SQLite**: Weaker analytics capabilities (no OLAP optimizations)
- **BigQuery/Snowflake**: Cloud cost and credentials required
- **Parquet files**: No SQL engine, requires Spark/DuckDB anyway

**Tradeoffs:**
- ✅ Zero setup, instant queries, perfect for < 100M rows
- ✅ Free forever, no usage limits
- ❌ Single-writer limitation (fine for batch analytics)
- ❌ Not web-scale (not the goal for this project)

### dbt (Modeling + Tests)

**Why:**
- **Industry standard**: Used by majority of modern data teams
- **Version control**: All transformations in SQL files tracked by git
- **Testing framework**: Built-in data quality checks (uniqueness, nulls, referential integrity)
- **Documentation**: Auto-generated data dictionary from YAML
- **Modularity**: Reusable SQL with Jinja templating and macros

**Usage:**
- Staging layer: `stg_games` with data cleaning and deduplication
- Marts layer: `fact_games`, `dim_player`, `dim_opening`, `dim_time_control`
- 13 data tests ensuring quality (unique IDs, valid enums, not null)

**Alternatives Considered:**
- **Raw SQL scripts**: No dependency management, testing, or documentation
- **Python (pandas)**: Harder to test, review, and maintain transformations
- **Dataform**: Google-specific, less adoption than dbt
- **SQLMesh**: Newer tool, smaller community

**Tradeoffs:**
- ✅ Declarative SQL, easy code review
- ✅ Built-in lineage and impact analysis
- ✅ Runs anywhere (dev, CI, prod)
- ❌ Learning curve for Jinja templating
- ❌ YAML verbosity for tests/docs

### Evidence (Dashboards)

**Why:**
- **Code-based**: Dashboards defined in Markdown + SQL (version controlled)
- **No BI server**: Static site generation, host anywhere (GitHub Pages, Netlify)
- **Fast development**: Live reload during development
- **SQL-native**: Write queries directly, no drag-and-drop limitations
- **Modern UX**: Responsive, interactive charts without JavaScript

**Usage (Planned):**
- Player performance dashboard (win/loss/draw rates by opening, time control)
- Opening analysis (ECO code performance)
- Rating progression over time

**Alternatives Considered:**
- **Metabase/Superset**: Require servers, databases, manual deployment
- **Streamlit**: Python-based but requires runtime server
- **PowerBI/Tableau**: Expensive licenses, not git-friendly
- **Jupyter notebooks**: Not production-quality for end users
- **Custom React app**: Overkill, requires frontend engineering

**Tradeoffs:**
- ✅ Version control for dashboards
- ✅ Zero hosting cost (static files)
- ✅ Fast, lightweight, modern
- ❌ Less mature than Metabase/Superset
- ❌ Smaller community and plugin ecosystem

### GitHub Actions (CI)

**Why:**
- **Built-in**: Free for public repos, no external CI service
- **Fast**: Runs in parallel, modern caching
- **Standard**: YAML-based config, used by millions of projects
- **Matrix builds**: Test multiple Python versions easily

**Usage:**
- Install dependencies from `requirements.txt`
- Load sample dataset (2000 rows) into DuckDB
- Run dbt models and tests
- Verify all data quality checks pass

**Alternatives Considered:**
- **GitLab CI**: Requires GitLab hosting
- **CircleCI/Travis**: External services, configuration complexity
- **Local testing only**: No automated verification on PRs

**Tradeoffs:**
- ✅ Zero configuration for GitHub repos
- ✅ Free for open source
- ✅ Fast feedback on pull requests
- ❌ Vendor lock-in to GitHub
- ❌ Limited to 2000 minutes/month on free tier (sufficient for this project)

## Why This Stack Demonstrates Professional Quality

### Demonstrates Modern Analytics Engineering

This stack mirrors what you'd find at data-driven companies in 2024-2025:

1. **dbt adoption**: Core skill for analytics engineers at Airbnb, GitLab, Shopify, etc.
2. **Local-first development**: Best practice for fast iteration (pre-cloud deployment)
3. **Infrastructure as Code**: Everything in git, reproducible deployments
4. **Automated testing**: Data quality checks in CI prevent regressions

### Transferable Skills

Every tool has direct production equivalents:

- **DuckDB** → Snowflake/BigQuery/Redshift (same SQL patterns)
- **dbt** → dbt (literally the same tool in production)
- **Evidence** → Looker/Mode/Hex (SQL-based BI)
- **GitHub Actions** → Airflow/Dagster (orchestration patterns)

### Conversation Starters for Interviews

- "How did you handle data quality?" → dbt tests with 18/18 passing checks
- "How did you optimize for cost?" → DuckDB eliminates warehouse spend
- "How did you ensure reproducibility?" → Full git history, sample dataset in repo
- "How did you handle CI/CD?" → Automated dbt builds on every commit

### Complexity Appropriate for Solo Project

- No Kubernetes, no microservices, no over-engineering
- Each tool solves a real problem (not resume-driven development)
- Can explain every technical decision with clear rationale
- Avoids "enterprise complexity" (Kafka, Airflow, Spark) where unnecessary

### Easy to Demonstrate

- Clone repo, run 3 commands, see results
- No API keys, no cloud setup, no waiting
- Works on any laptop (Windows, Mac, Linux)
- Independent reviewers can validate quality

## Summary

This stack optimizes for **learning, demonstration, and iteration speed** without sacrificing **production relevance**. It's the ideal balance for a technical project that shows:

1. Understanding of modern data tooling
2. Ability to make pragmatic technical decisions
3. Focus on code quality and testing
4. Production-ready patterns at appropriate scale

**Key principle**: Use the simplest tool that solves the problem, with a clear upgrade path to production equivalents.
