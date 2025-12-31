{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'raw_games') }}
),

deduplicated as (
    -- Remove duplicates, keeping first occurrence
    select
        *,
        row_number() over (partition by id order by created_at) as row_num
    from source
),

renamed as (
    select
        id as game_id,
        
        -- Parse created_at timestamp
        -- If it's a numeric epoch, convert it; otherwise try casting
        case
            when try_cast(created_at as double) is not null
            then epoch_ms(cast(created_at as bigint))
            else try_cast(created_at as timestamp)
        end as created_at_ts,
        
        -- Normalize winner
        lower(coalesce(winner, '')) as winner_norm,
        
        -- Derive standardized result label
        case
            when lower(coalesce(winner, '')) = 'white' then 'white_win'
            when lower(coalesce(winner, '')) = 'black' then 'black_win'
            when lower(coalesce(winner, '')) in ('draw', 'none', '') then 'draw'
            else 'unknown'
        end as result_label,
        
        -- Game metrics
        try_cast(turns as integer) as turns,
        
        -- Players
        white_id as white_player_id,
        black_id as black_player_id,
        try_cast(white_rating as integer) as white_rating,
        try_cast(black_rating as integer) as black_rating,
        
        -- Time control
        increment_code as time_control_raw,
        
        -- Opening
        opening_eco,
        opening_name

    from deduplicated
    where row_num = 1
)

select * from renamed
