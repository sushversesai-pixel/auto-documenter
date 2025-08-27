# {{ module.name | title_case }}

{{ ai_content }}

## Module Structure

- **Language**: {{ module.language }}
- **Total Files**: {{ module.total_files }}
- **Documentation Style**: {{ style }}

### Files in this Module

{% for file_module in module.modules %}
- `{{ file_module }}`
{% endfor %}

## Directory Tree

