# API Reference - {{ file_path }}

*Auto-generated documentation for {{ file_path }}*

{% if modules %}
## Module Information

{% for module in modules %}
{{ ai_docs.get(module.name + '_' + module.line_number|string, {}).get('summary', 'Module documentation not available.') }}

### Imports
{% for import in module.imports %}
- `{{ import }}`
{% endfor %}

{% endfor %}
{% endif %}

{% if functions %}
## Functions

{% for func in functions %}
### `{{ func.name }}({{ func.parameters | map(attribute='name') | join(', ') }})`

{{ ai_docs.get(func.name + '_' + func.line_number|string, {}).get('summary', 'Function documentation not available.') }}

**Signature:**
```{{ 'python' if file_path.endswith('.py') else 'javascript' }}
{{ func.signature if func.signature else func.name }}
