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
{{ func.signature if func.signature else func.name }}({{ func.parameters | map(attribute='name') | join(', ') }})
```

**Parameters:**
{% for param in func.parameters %}
- `{{ param.name }}`: {{ param.param_type or 'Any' }}{% if param.default_value %} (default: {{ param.default_value }}){% endif %}
{% endfor %}

{% if func.return_type %}
**Returns:** {{ func.return_type }}
{% endif %}

{% endfor %}
{% endif %}

{% if classes %}
## Classes

{% for cls in classes %}
### `{{ cls.name }}`

{{ ai_docs.get(cls.name + '_' + cls.line_number|string, {}).get('summary', 'Class documentation not available.') }}

{% if cls.base_classes %}
**Inherits from:** {{ cls.base_classes | join(', ') }}
{% endif %}

{% if cls.attributes %}
**Attributes:**
{% for attr in cls.attributes %}
- `{{ attr }}`
{% endfor %}
{% endif %}

**Methods:**
{% for method in cls.methods %}
- `{{ method.name }}({{ method.parameters | map(attribute='name') | join(', ') }})`
{% endfor %}

{% endfor %}
{% endif %}
