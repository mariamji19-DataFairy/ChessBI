"""
ChessBI Data Ingestion Module

This module provides clients and utilities for ingesting chess game data
from various sources including Chess.com and Lichess APIs.
"""

from .chesscom_client import ChessComClient

__all__ = ["ChessComClient"]
