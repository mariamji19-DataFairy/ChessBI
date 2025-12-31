"""
Dataset Preparation Script

Creates a small sample dataset from a larger CSV file for testing and CI.
This script extracts the first N rows from a full dataset to create a
committed sample that can be used for development and automated testing.
"""

import argparse
import sys
from pathlib import Path
from typing import List

import pandas as pd


# Required columns that must be present in the dataset
REQUIRED_COLUMNS = [
    "id",
    "created_at",
    "winner",
    "turns",
    "increment_code",
    "white_id",
    "black_id",
    "white_rating",
    "black_rating",
    "opening_eco",
    "opening_name",
]


def prepare_dataset(
    input_path: str,
    output_path: str,
    num_rows: int = 2000
) -> None:
    """
    Extract a sample from a dataset CSV file.
    
    Args:
        input_path: Path to the full dataset CSV.
        output_path: Path where the sample CSV will be written.
        num_rows: Number of rows to extract (default: 2000).
    
    Raises:
        FileNotFoundError: If input file doesn't exist.
        ValueError: If required columns are missing.
    """
    # Validate input file exists
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print(f"[ChessBI] Reading dataset from: {input_path}")
    
    # Read the full dataset
    df = pd.read_csv(input_path)
    total_rows = len(df)
    
    print(f"[ChessBI] Total rows in input: {total_rows:,}")
    print(f"[ChessBI] Columns found: {len(df.columns)}")
    
    # Validate required columns
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}\n"
            f"Available columns: {', '.join(df.columns)}"
        )
    
    print(f"[ChessBI] ✓ All required columns present")
    
    # Extract sample
    sample_rows = min(num_rows, total_rows)
    df_sample = df.head(sample_rows)
    
    # Create output directory if needed
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write sample
    df_sample.to_csv(output_path, index=False)
    
    print(f"\n[ChessBI] Sample dataset created:")
    print(f"  • Output path: {output_path}")
    print(f"  • Rows written: {sample_rows:,}")
    print(f"  • Columns: {len(df_sample.columns)}")
    print(f"\n[ChessBI] Column list:")
    for i, col in enumerate(df_sample.columns, 1):
        print(f"  {i:2d}. {col}")


def main() -> int:
    """
    CLI entry point.
    
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = argparse.ArgumentParser(
        description="Prepare a sample dataset from a full CSV file"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the full dataset CSV"
    )
    parser.add_argument(
        "--out",
        type=str,
        required=True,
        help="Path where the sample CSV will be written"
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=2000,
        help="Number of rows to extract (default: 2000)"
    )
    
    args = parser.parse_args()
    
    try:
        prepare_dataset(
            input_path=args.input,
            output_path=args.out,
            num_rows=args.rows
        )
        print("\n[ChessBI] ✓ Dataset preparation complete!")
        return 0
    
    except FileNotFoundError as e:
        print(f"\n[ChessBI] ✗ Error: {e}", file=sys.stderr)
        return 1
    
    except ValueError as e:
        print(f"\n[ChessBI] ✗ Error: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"\n[ChessBI] ✗ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
