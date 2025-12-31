{{
    config(
        materialized='table'
    )
}}

select distinct
    md5(opening_eco || '|' || opening_name) as opening_key,
    opening_eco,
    opening_name
from {{ ref('stg_games') }}
where opening_eco is not null
order by opening_eco, opening_name
