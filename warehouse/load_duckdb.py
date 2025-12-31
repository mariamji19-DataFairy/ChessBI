"""
DuckDB Data Loader

Loads chess game data from CSV files into a DuckDB database.
Supports loading from either the full raw dataset or a committed sample.
"""

import argparse
import sys
from pathlib import Path

import duckdb


def load_duckdb(
    db_path: str,
    source: str = "sample"
) -> None:
    """
    Load chess game data into DuckDB.
    
    Args:
        db_path: Path to the DuckDB database file.
        source: Data source - either "raw" or "sample".
    
    Raises:
        FileNotFoundError: If source CSV file doesn't exist.
        ValueError: If source parameter is invalid.
    """
    # Determine source CSV path
    if source == "raw":
        csv_path = "data/raw/lichess/games.csv"
    elif source == "sample":
        csv_path = "data/sample/games_sample.csv"
    else:
        raise ValueError(f"Invalid source: {source}. Must be 'raw' or 'sample'")
    
    # Validate CSV exists
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(
            f"Source CSV not found: {csv_path}\n"
            f"Please ensure the dataset is in place."
        )
    
    print(f"[ChessBI] Loading data from: {csv_path}")
    print(f"[ChessBI] Target database: {db_path}")
    
    # Ensure database directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to DuckDB
    con = duckdb.connect(db_path)
    
    try:
        # Drop existing table if it exists
        con.execute("DROP TABLE IF EXISTS raw_games")
        
        # Load CSV using DuckDB's read_csv_auto for robust type inference
        print(f"[ChessBI] Creating raw_games table...")
        con.execute(f"""
            CREATE TABLE raw_games AS
            SELECT * FROM read_csv_auto('{csv_path}', header=true)
        """)
        
        # Get row count
        row_count = con.execute("SELECT COUNT(*) FROM raw_games").fetchone()[0]
        print(f"[ChessBI] ✓ Loaded {row_count:,} rows into raw_games")
        
        # Get schema sample
        print(f"\n[ChessBI] Table schema (first 5 columns):")
        schema = con.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'raw_games'
            LIMIT 5
        """).fetchall()
        
        for col_name, col_type in schema:
            print(f"  • {col_name}: {col_type}")
        
        # Create cleaned view
        print(f"\n[ChessBI] Creating raw_games_clean view...")
        con.execute("DROP VIEW IF EXISTS raw_games_clean")
        
        con.execute("""
            CREATE VIEW raw_games_clean AS
            SELECT 
                id,
                CAST(created_at AS TIMESTAMP) AS created_at,
                LOWER(winner) AS winner,
                turns,
                increment_code,
                white_id,
                black_id,
                white_rating,
                black_rating,
                opening_eco,
                opening_name,
                * EXCLUDE (id, created_at, winner, turns, increment_code, 
                           white_id, black_id, white_rating, black_rating,
                           opening_eco, opening_name)
            FROM raw_games
        """)
        
        print(f"[ChessBI] ✓ Created raw_games_clean view with standardized columns")
        
        # Sample data preview
        print(f"\n[ChessBI] Sample row:")
        sample = con.execute("SELECT * FROM raw_games_clean LIMIT 1").fetchone()
        if sample:
            print(f"  • ID: {sample[0]}")
            print(f"  • Created: {sample[1]}")
            print(f"  • Winner: {sample[2]}")
            print(f"  • Turns: {sample[3]}")
        
        print(f"\n[ChessBI] Database ready at: {db_path}")
    
    finally:
        con.close()


def main() -> int:
    """
    CLI entry point.
    
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = argparse.ArgumentParser(
        description="Load chess game data into DuckDB"
    )
    parser.add_argument(
        "--db",
        type=str,
        required=True,
        help="Path to the DuckDB database file"
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=["raw", "sample"],
        default="sample",
        help="Data source: 'raw' (full dataset) or 'sample' (committed sample)"
    )
    
    args = parser.parse_args()
    
    try:
        load_duckdb(
            db_path=args.db,
            source=args.source
        )
        print("\n[ChessBI] ✓ Data loading complete!")
        return 0
    
    except FileNotFoundError as e:
        print(f"\n[ChessBI] ✗ Error: {e}", file=sys.stderr)
        return 1
    
    except ValueError as e:
        print(f"\n[ChessBI] ✗ Error: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"\n[ChessBI] ✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
