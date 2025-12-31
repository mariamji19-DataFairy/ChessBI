# Chess Analytics Dashboard

## Recent Games

```sql recent_games
SELECT 
    created_at_ts as "Timestamp",
    white_player_id as "White Player",
    black_player_id as "Black Player",
    white_rating as "White Rating",
    black_rating as "Black Rating",
    result_label as "Result",
    opening_name as "Opening"
FROM {fact_games}
ORDER BY created_at_ts DESC
LIMIT 50
```

<DataTable data={recent_games} search=true/>

## Win Rate by Opening

```sql opening_stats
SELECT 
    opening_eco as "ECO Code",
    opening_name as "Opening Name",
    COUNT(*) as "Total Games",
    ROUND(SUM(CASE WHEN result_label = 'white_win' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as "White Win %",
    ROUND(SUM(CASE WHEN result_label = 'black_win' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as "Black Win %",
    ROUND(SUM(CASE WHEN result_label = 'draw' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as "Draw %"
FROM {fact_games}
WHERE opening_name IS NOT NULL
GROUP BY opening_eco, opening_name
HAVING COUNT(*) >= 10
ORDER BY "Total Games" DESC
LIMIT 20
```

<DataTable data={opening_stats}/>

## Rating Distribution

```sql rating_distribution
SELECT 
    CASE 
        WHEN white_rating < 800 THEN '< 800'
        WHEN white_rating < 1000 THEN '800-999'
        WHEN white_rating < 1200 THEN '1000-1199'
        WHEN white_rating < 1400 THEN '1200-1399'
        WHEN white_rating < 1600 THEN '1400-1599'
        WHEN white_rating < 1800 THEN '1600-1799'
        ELSE '1800+' 
    END as "Rating Range",
    COUNT(*) as "Game Count"
FROM {fact_games}
WHERE white_rating IS NOT NULL
GROUP BY "Rating Range"
ORDER BY MIN(white_rating)
```

<BarChart 
    data={rating_distribution} 
    x="Rating Range"
    y="Game Count"
/>

## Game Results Summary

```sql results_summary
SELECT 
    result_label as "Result",
    COUNT(*) as "Count",
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as "Percentage"
FROM {fact_games}
GROUP BY result_label
ORDER BY "Count" DESC
```

<DataTable data={results_summary}/>

<BigValue 
    data={results_summary} 
    value="Count"
/>
