with source as (
    select * from {{ source('colorado', 'raw_co_business_entities') }}
),

renamed as (
    select
        id as _landing_id,
        loaded_at,

        data->>'entityid'                as entity_id,
        data->>'entityname'              as entity_name,
        data->>'entitystatus'            as entity_status,
        data->>'entitytype'              as entity_type,
        data->>'jurisdictonofformation'  as jurisdiction_of_formation,

        data->>'principaladdress1'       as principal_address,
        data->>'principalcity'           as principal_city,
        data->>'principalstate'          as principal_state,
        data->>'principalzipcode'        as principal_zip,

        data->>'agentfirstname'          as agent_first_name,
        data->>'agentlastname'           as agent_last_name,

        (data->>'entityformdate')::timestamp as entity_form_date

    from source
)

select * from renamed
