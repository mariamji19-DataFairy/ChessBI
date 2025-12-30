"""
ChessBI CLI

Command-line interface for ChessBI data ingestion operations.
"""

import argparse
import sys
from typing import Optional

from .chesscom_ingest import run_chesscom_ingest
from .chesscom_client import ChessComClientError, ChessComAPIError


def main() -> int:
    """
    Main CLI entry point.
    
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = argparse.ArgumentParser(
        prog="python -m ingest.cli",
        description="ChessBI data ingestion CLI",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Ingestion command")
    
    # Chess.com subcommand
    chesscom_parser = subparsers.add_parser(
        "chesscom",
        help="Ingest chess game data from Chess.com"
    )
    chesscom_parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="Chess.com username to fetch games for"
    )
    chesscom_parser.add_argument(
        "--out",
        type=str,
        default="data/raw",
        help="Output directory for raw JSON files (default: data/raw)"
    )
    chesscom_parser.add_argument(
        "--max-months",
        type=int,
        default=3,
        help="Maximum number of recent months to fetch (default: 3)"
    )
    chesscom_parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Only fetch months >= this date (format: YYYY-MM, e.g., 2024-01)"
    )
    chesscom_parser.add_argument(
        "--cache-path",
        type=str,
        default=".cache/chesscom_etags.json",
        help="Path to ETag cache file (default: .cache/chesscom_etags.json)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "chesscom":
        return run_chesscom_cli(
            username=args.username,
            out_dir=args.out,
            max_months=args.max_months,
            since=args.since,
            cache_path=args.cache_path,
        )
    
    return 1


def run_chesscom_cli(
    username: str,
    out_dir: str,
    max_months: int,
    since: Optional[str],
    cache_path: str,
) -> int:
    """
    Execute Chess.com ingestion command.
    
    Args:
        username: Chess.com username.
        out_dir: Output directory for raw files.
        max_months: Maximum number of recent months to fetch.
        since: Optional YYYY-MM filter.
        cache_path: Path to ETag cache file.
    
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    try:
        print(f"\n{'='*60}")
        print(f"ChessBI - Chess.com Ingestion")
        print(f"{'='*60}\n")
        
        result = run_chesscom_ingest(
            username=username,
            out_dir=out_dir,
            max_months=max_months,
            since=since,
            cache_path=cache_path,
        )
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Summary")
        print(f"{'='*60}")
        print(f"  Username:         {result['username']}")
        print(f"  Months selected:  {len(result['months_selected'])}")
        print(f"  Months fetched:   {len(result['months_fetched'])}")
        print(f"  Months unchanged: {len(result['months_unchanged'])}")
        print(f"  Total games:      {result['total_games']}")
        print(f"  Output directory: {result['out_dir']}/chesscom/{result['username']}/")
        print(f"{'='*60}\n")
        
        if result['months_fetched']:
            print(f"✓ Successfully fetched {len(result['months_fetched'])} month(s)")
        
        if result['months_unchanged']:
            print(f"✓ Skipped {len(result['months_unchanged'])} unchanged month(s) (cached)")
        
        print()
        return 0
    
    except ChessComAPIError as e:
        print(f"\n✗ Chess.com API error: {e}", file=sys.stderr)
        return 1
    
    except ChessComClientError as e:
        print(f"\n✗ Client error: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
