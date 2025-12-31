"""
Chess.com Ingestion Runner

Orchestrates the fetching and storage of chess game data from Chess.com API,
with ETag caching to minimize bandwidth and respect rate limits.
"""

import json
import os
import re
from pathlib import Path
from typing import Optional

from .chesscom_client import ChessComClient
from .etag_cache import load_etags, save_etags, get_etag, set_etag


def run_chesscom_ingest(
    username: str,
    out_dir: str = "data/raw",
    max_months: int = 3,
    since: Optional[str] = None,
    cache_path: str = ".cache/chesscom_etags.json",
) -> dict:
    """
    Ingest chess game data from Chess.com for a specific user.
    
    Fetches monthly game archives, respects ETags to avoid redundant downloads,
    and writes raw JSON files for later processing.
    
    Args:
        username: Chess.com username to fetch games for.
        out_dir: Output directory for raw JSON files. Default: "data/raw".
        max_months: Maximum number of recent months to fetch. Default: 3.
        since: Optional "YYYY-MM" filter - only fetch months >= this date.
        cache_path: Path to ETag cache file. Default: ".cache/chesscom_etags.json".
    
    Returns:
        Summary dictionary with keys:
        - username: The username ingested
        - months_selected: List of YYYY-MM strings selected for ingestion
        - months_fetched: List of YYYY-MM strings actually fetched (200 status)
        - months_unchanged: List of YYYY-MM strings unchanged (304 status)
        - total_games: Total number of games fetched
        - out_dir: Output directory path
    
    Example:
        >>> result = run_chesscom_ingest("hikaru", max_months=2, since="2024-01")
        >>> print(f"Fetched {result['total_games']} games")
    """
    print(f"[ChessBI] Starting ingestion for user: {username}")
    
    # Initialize client and load ETag cache for bandwidth optimization
    client = ChessComClient()
    etags = load_etags(cache_path)
    
    # Fetch available archives
    print(f"[ChessBI] Fetching archive list...")
    archive_urls = client.get_archives(username)
    
    # Sort archives by date (they're already in ascending order, but be explicit)
    archive_urls.sort()
    
    # Filter by 'since' date if provided (YYYY-MM format)
    if since:
        since_filtered = []
        for url in archive_urls:
            year_month = _extract_year_month(url)
            if year_month and year_month >= since:
                since_filtered.append(url)
        archive_urls = since_filtered
        print(f"[ChessBI] Filtered to {len(archive_urls)} archives since {since}")
    
    # Select last max_months
    if len(archive_urls) > max_months:
        archive_urls = archive_urls[-max_months:]
    
    selected_months = [_extract_year_month(url) for url in archive_urls]
    print(f"[ChessBI] Selected {len(archive_urls)} month(s): {', '.join(selected_months)}")
    
    # Process each archive
    months_fetched = []
    months_unchanged = []
    total_games = 0
    
    for url in archive_urls:
        year_month = _extract_year_month(url)
        if not year_month:
            print(f"[ChessBI] Warning: Could not parse year/month from {url}, skipping")
            continue
        
        print(f"[ChessBI] Processing {year_month}...", end=" ")
        
        # Get cached ETag to enable conditional request
        cached_etag = get_etag(etags, url)
        
        # Fetch archive
        status_code, data, new_etag = client.get_month_archive(url, cached_etag)
        
        if status_code == 304:
            # ETag match - content unchanged, skip download
            print("unchanged (304)")
            months_unchanged.append(year_month)
        elif status_code == 200:
            game_count = len(data.get("games", []))
            print(f"fetched ({game_count} games)")
            
            # Write to disk
            output_path = _get_output_path(out_dir, username, year_month)
            _write_json(output_path, data)
            
            months_fetched.append(year_month)
            total_games += game_count
            
            # Update ETag cache for next run if present
            if new_etag:
                set_etag(etags, url, new_etag)
        else:
            print(f"unexpected status {status_code}")
    
    # Save updated ETag cache to disk for future runs
    save_etags(cache_path, etags)
    
    # Prepare summary
    summary = {
        "username": username,
        "months_selected": selected_months,
        "months_fetched": months_fetched,
        "months_unchanged": months_unchanged,
        "total_games": total_games,
        "out_dir": out_dir,
    }
    
    # Print summary
    print(f"\n[ChessBI] Ingestion complete!")
    print(f"  • Months selected: {len(selected_months)}")
    print(f"  • Months fetched: {len(months_fetched)}")
    print(f"  • Months unchanged: {len(months_unchanged)}")
    print(f"  • Total games: {total_games}")
    print(f"  • Output directory: {out_dir}/chesscom/{username}/")
    
    client.close()
    
    return summary


def _extract_year_month(url: str) -> Optional[str]:
    """
    Extract YYYY-MM from a Chess.com archive URL.
    
    Args:
        url: Archive URL like "https://api.chess.com/pub/player/user/games/2023/12"
    
    Returns:
        String like "2023-12" or None if pattern doesn't match.
    """
    # Pattern: /YYYY/MM at end of URL
    match = re.search(r'/(\d{4})/(\d{2})$', url)
    if match:
        year, month = match.groups()
        return f"{year}-{month}"
    return None


def _get_output_path(out_dir: str, username: str, year_month: str) -> str:
    """
    Generate output path for a monthly archive JSON file.
    
    Args:
        out_dir: Base output directory.
        username: Chess.com username.
        year_month: String like "2023-12".
    
    Returns:
        Path like "data/raw/chesscom/username/2023-12.json"
    """
    return os.path.join(out_dir, "chesscom", username, f"{year_month}.json")


def _write_json(path: str, data: dict) -> None:
    """
    Write JSON data to a file, creating parent directories as needed.
    
    Args:
        path: Output file path.
        data: Dictionary to serialize as JSON.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
