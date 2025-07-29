{% extends "view.sql" %}
{% macro spark__indbt_view_materialization() -%}
    {%- set file_format = config.get('file_format', default='openhouse') -%}

    {% if file_format == 'openhouse' %}
        {% do exceptions.raise_compiler_error("Persisted views are not supported for file_format='openhouse'") %}
    {% endif %}

    {{ return(create_or_replace_view()) }}
{%- endmacro %}
