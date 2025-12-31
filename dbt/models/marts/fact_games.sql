{{
    config(
        materialized='table'
    )
}}

select
    game_id,
    created_at_ts,
    result_label,
    turns,
    white_player_id,
    black_player_id,
    white_rating,
    black_rating,
    time_control_raw,
    opening_eco,
    opening_name
from {{ ref('stg_games') }}
