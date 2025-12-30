# Key Performance Indicators (KPIs)

This document defines the core KPIs tracked in ChessBI, providing standardized metrics for chess analytics.

## Game Outcome Metrics

### Win Rate
**Definition**: Percentage of games won by a player.
**Formula**: `(Wins / Total Games) * 100`
**Dimensions**: By opening, time control, opponent rating bucket, color played

### Draw Rate
**Definition**: Percentage of games that ended in a draw.
**Formula**: `(Draws / Total Games) * 100`
**Dimensions**: By opening, time control, opponent rating bucket, color played

### Loss Rate
**Definition**: Percentage of games lost by a player.
**Formula**: `(Losses / Total Games) * 100`
**Dimensions**: By opening, time control, opponent rating bucket, color played

## Performance by Opening

### Opening Win Rate
**Definition**: Win rate specifically for games starting with a particular opening.
**Formula**: `(Wins with Opening / Games with Opening) * 100`
**Dimensions**: By ECO code, opening name, player skill level

### Opening Frequency
**Definition**: How often a particular opening is played.
**Formula**: `(Games with Opening / Total Games) * 100`
**Dimensions**: By player, time control, rating range

## Performance by Time Control

### Time Control Win Rate
**Definition**: Win rate segmented by game time limits.
**Formula**: `(Wins in Time Control / Games in Time Control) * 100`
**Dimensions**: By time control category (Bullet, Blitz, Rapid, Classical), player rating

### Average Game Length
**Definition**: Average number of moves per game.
**Formula**: `SUM(Move Count) / Total Games`
**Dimensions**: By time control, opening, player

## Performance by Color

### White Win Rate
**Definition**: Win rate when playing as White.
**Formula**: `(White Wins / White Games) * 100`

### Black Win Rate
**Definition**: Win rate when playing as Black.
**Formula**: `(Black Wins / Black Games) * 100`

### Color Advantage
**Definition**: Difference between White and Black win rates.
**Formula**: `White Win Rate - Black Win Rate`

## Performance by Opponent Rating

### Rating Bucket Definitions
- **Beginner**: 0-1199
- **Intermediate**: 1200-1599
- **Advanced**: 1600-1999
- **Expert**: 2000-2399
- **Master**: 2400+

### Win Rate by Rating Bucket
**Definition**: Win rate against opponents in specific rating ranges.
**Formula**: `(Wins vs Bucket / Games vs Bucket) * 100`
**Dimensions**: By player's own rating, time control

### Rating Performance
**Definition**: Average opponent rating in won/lost games.
**Formula**: `AVG(Opponent Rating) WHERE Result = 'Win'`
**Dimensions**: By game outcome, time control
