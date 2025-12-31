{{
    config(
        materialized='table'
    )
}}

with parsed_controls as (
    select distinct
        time_control_raw,
        
        -- Parse "base+increment" format (e.g., "300+0")
        case
            when time_control_raw ~ '^\d+\+\d+$' then
                cast(split_part(time_control_raw, '+', 1) as integer)
            else null
        end as base_seconds,
        
        case
            when time_control_raw ~ '^\d+\+\d+$' then
                cast(split_part(time_control_raw, '+', 2) as integer)
            else null
        end as increment_seconds
        
    from {{ ref('stg_games') }}
    where time_control_raw is not null
)

select
    time_control_raw,
    base_seconds,
    increment_seconds,
    
    -- Categorize time control
    case
        when base_seconds < 180 then 'bullet'
        when base_seconds >= 180 and base_seconds < 600 then 'blitz'
        when base_seconds >= 600 and base_seconds < 1800 then 'rapid'
        when base_seconds >= 1800 then 'classical'
        else 'unknown'
    end as time_control_category
    
from parsed_controls
order by base_seconds nulls last, increment_seconds nulls last
