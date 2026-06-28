with staged as (
    select * from {{ ref('stg_co_business_entities') }}
),

cleaned as (
    select
        entity_id,
        trim(regexp_replace(
                entity_name,
                ',\s+(Dissolved|Voluntarily Dissolved|Administratively Dissolved|Delinquent|Withdrawn|Merged|Consolidated|Converted|Revoked|Noncompliant|Exists|Colorado Authority Relinquished).*$',
                ''
            )) as entity_name,
        entity_name as entity_name_raw,
        entity_status,
        entity_type,
        jurisdiction_of_formation,
        principal_city,
        principal_state,
        entity_form_date
    from staged
)

select * from cleaned