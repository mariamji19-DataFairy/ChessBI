# ADR 0001: Technology Stack Selection

## Status

**Accepted** – December 2025

## Context

ChessBI requires a modern analytics stack that balances:

1. **Project objectives**: Demonstrate analytics engineering skills relevant to industry (dbt, SQL, data quality)
2. **Practical constraints**: Zero cloud costs, fast local iteration, reproducible setup
3. **Technical requirements**: Handle 20k+ rows locally, scale to millions in theory
4. **CI/CD needs**: Automated testing with sample data, fast feedback cycles

### Requirements Analysis

**Must Have:**
- SQL-based transformation layer (industry standard for analytics)
- Version control for all code, config, and schema
- Automated data quality testing
- Local-first development (no cloud dependencies)
- Dashboard/BI capability (static or server-based)

**Should Have:**
- Fast query performance on analytical workloads
- Minimal setup complexity (< 5 minutes from clone to running)
- Free/open-source tools with active communities
- Skills transferable to production environments

**Could Have:**
- Real-time streaming (not needed for batch chess analytics)
- Multi-user collaboration features (solo project)
- Advanced ML/AI capabilities (future phase)

### Alternatives Considered

#### Warehouse Options

1. **PostgreSQL**
   - ✅ Production-grade, widely used
   - ✅ Excellent dbt support
   - ❌ Requires server installation and management
   - ❌ OLTP-optimized, slower for analytics than OLAP databases
   - **Verdict**: Overkill for local development, adds setup friction

2. **SQLite**
   - ✅ Zero setup, single file
   - ✅ Embedded like DuckDB
   - ❌ Limited analytical capabilities (no window functions before 3.25)
   - ❌ Weak dbt support (community plugin only)
   - **Verdict**: Too limited for modern analytics workloads

3. **BigQuery / Snowflake / Redshift**
   - ✅ Production-grade cloud warehouses
   - ✅ Excellent dbt support
   - ❌ Requires cloud accounts and credentials
   - ❌ Incurs costs (even with free tiers)
   - ❌ Cannot commit database to git
   - **Verdict**: Not local-first, inappropriate for demonstration projects

4. **DuckDB** ✓ Selected
   - ✅ OLAP-optimized (columnar, vectorized execution)
   - ✅ Embedded, zero setup
   - ✅ Excellent dbt support (`dbt-duckdb`)
   - ✅ PostgreSQL-compatible SQL
   - ✅ Database file can be committed (under git size limits)
   - ❌ Single-writer limitation (not relevant for batch analytics)
   - **Verdict**: Optimal for local analytics with production-grade SQL

#### Transformation Options

1. **Raw SQL scripts**
   - ✅ Simple, direct
   - ❌ No dependency management
   - ❌ No testing framework
   - ❌ Hard to maintain and review
   - **Verdict**: Not suitable for multi-model projects

2. **Python (pandas/Polars)**
   - ✅ Flexible, powerful
   - ❌ Harder to review transformations than SQL
   - ❌ No built-in testing or lineage
   - ❌ Less transferable to analytics engineering roles
   - **Verdict**: Better for ML pipelines than BI transformations

3. **dbt** ✓ Selected
   - ✅ Industry standard for analytics engineering
   - ✅ SQL-based with Jinja templating
   - ✅ Built-in testing framework (uniqueness, nulls, referential integrity)
   - ✅ Auto-generated documentation and lineage
   - ✅ Version control friendly
   - ❌ Learning curve for Jinja and YAML config
   - **Verdict**: Aligns with industry best practices, highly transferable skill

#### Dashboard Options

1. **Metabase / Superset**
   - ✅ Feature-rich, mature
   - ❌ Requires server deployment
   - ❌ Configuration not fully version-controlled
   - ❌ Overkill for demonstration projects
   - **Verdict**: Too heavy for local-first approach

2. **PowerBI / Tableau**
   - ✅ Industry-leading BI tools
   - ❌ Expensive licenses
   - ❌ Not git-friendly (binary files)
   - ❌ Requires manual deployment
   - **Verdict**: Not suitable for open-source projects

3. **Jupyter Notebooks**
   - ✅ Easy to iterate
   - ❌ Not production-quality for end-user dashboards
   - ❌ Requires runtime server
   - **Verdict**: Good for analysis, not for BI delivery

4. **Evidence** ✓ Selected
   - ✅ Code-based (Markdown + SQL), version controlled
   - ✅ Static site generation (host on GitHub Pages)
   - ✅ Fast development with live reload
   - ✅ Modern, responsive UX
   - ❌ Newer tool, smaller community
   - ❌ Less mature than Metabase
   - **Verdict**: Best balance of simplicity and modern BI capabilities

#### CI/CD Options

1. **GitHub Actions** ✓ Selected
   - ✅ Built-in for GitHub repos
   - ✅ Free for public repos (2000 min/month)
   - ✅ Fast, modern caching
   - ✅ YAML-based, easy to understand
   - ❌ Vendor lock-in to GitHub
   - **Verdict**: Natural choice for GitHub-hosted projects

2. **GitLab CI**
   - ✅ Similar feature set to GitHub Actions
   - ❌ Requires GitLab hosting
   - **Verdict**: No benefit over GitHub Actions for this project

3. **CircleCI / Travis CI**
   - ✅ Mature, feature-rich
   - ❌ External service, more configuration
   - ❌ Less generous free tier
   - **Verdict**: Unnecessary complexity

## Decision

**Selected Stack:**

- **Warehouse**: DuckDB (embedded OLAP database)
- **Transformation**: dbt (SQL-based analytics engineering)
- **Dashboard**: Evidence (code-based BI)
- **CI/CD**: GitHub Actions (automated testing)
- **Language**: Python (ingestion and scripts)

### Rationale

This stack optimizes for:

1. **Learning velocity**: DuckDB + dbt enable fast iteration without cloud delays
2. **Industry relevance**: dbt skills directly transfer to production analytics teams (Snowflake/BigQuery + dbt is the standard)
3. **Reproducibility**: Everything runs locally, no credentials or cloud setup required
4. **Cost**: Zero operational costs, free tools throughout
5. **Technical quality**: Demonstrates modern best practices (testing, version control, CI/CD)

### Architecture Pattern

```
Chess.com/Lichess APIs
    ↓
Python Ingestion Scripts (API clients, caching)
    ↓
DuckDB Warehouse (embedded OLAP)
    ↓
dbt Models (staging → marts)
    ↓
Evidence Dashboards (static site)
    ↓
GitHub Actions (CI/CD)
```

## Consequences

### Positive

1. **Fast feedback loops**: Query results in milliseconds, dbt builds in seconds
2. **Version control**: All code, config, schema, and (sample) data in git
3. **Automated quality**: dbt tests catch data issues before merge
4. **Zero infrastructure**: No servers, no cloud accounts, no ops burden
5. **Transferable skills**: DuckDB SQL patterns work on Snowflake/BigQuery; dbt is identical in prod
6. **Easy demonstration**: Clone, run 3 commands, see results

### Negative

1. **DuckDB limitations**: Single-writer (fine for batch), not web-scale (not the goal)
2. **Evidence maturity**: Smaller community than Metabase, fewer plugins
3. **GitHub coupling**: CI tied to GitHub (acceptable tradeoff)
4. **Learning curve**: dbt requires understanding Jinja and YAML conventions

### Mitigations

- **DuckDB scalability**: Project scope limited to < 1M rows (chess analytics at personal scale)
- **Evidence limitations**: Can swap to Metabase/Superset later without changing dbt models
- **dbt complexity**: Strong documentation and incremental learning (start simple, add complexity)

### Upgrade Path

When moving to production scale:

- **DuckDB** → Snowflake/BigQuery/Redshift (same SQL, same dbt code)
- **Local files** → Cloud storage (S3/GCS)
- **Python scripts** → Airflow/Dagster (orchestration)
- **Evidence** → Looker/Mode/Hex (enterprise BI)

**Key insight**: All tools have production equivalents with minimal code changes. The architecture patterns learned here transfer directly.

## References

- [DuckDB: An in-process SQL OLAP database](https://duckdb.org/)
- [dbt: Transform data in your warehouse](https://www.getdbt.com/)
- [Evidence: Business Intelligence as Code](https://evidence.dev/)
- [The Modern Data Stack](https://www.moderndatastack.xyz/)

## Review

This decision will be reviewed if:

1. DuckDB performance degrades beyond acceptable limits (> 10s queries)
2. Evidence limitations block critical dashboard features
3. Project scope expands to require multi-user collaboration

**Next review date**: After Evidence dashboard implementation (Q1 2026)
