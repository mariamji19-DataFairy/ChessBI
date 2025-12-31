{{
    config(
        materialized='table'
    )
}}

with white_players as (
    select distinct white_player_id as player_id
    from {{ ref('stg_games') }}
    where white_player_id is not null
),

black_players as (
    select distinct black_player_id as player_id
    from {{ ref('stg_games') }}
    where black_player_id is not null
),

all_players as (
    select player_id from white_players
    union
    select player_id from black_players
)

select distinct player_id
from all_players
order by player_id
