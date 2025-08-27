{% if style == 'google' %}
{{ doc.summary }}

{{ doc.description }}

Attributes:
{% for attr in doc.attributes %}
    {{ attr.name }} ({{ attr.type }}): {{ attr.description }}
{% endfor %}

{% if doc.examples %}
Examples:
{% for example in doc.examples %}
    {{ example.description }}:
    
    ```python
    {{ example.code }}
    ```
{% endfor %}
{% endif %}

{% elif style == 'numpy' %}
{{ doc.summary }}

{{ doc.description }}

Attributes
----------
{% for attr in doc.attributes %}
{{ attr.name }} : {{ attr.type }}
    {{ attr.description }}
{% endfor %}

{% if doc.examples %}
Examples
--------
{% for example in doc.examples %}
{{ example.description }}

>>> {{ example.code }}
{% endfor %}
{% endif %}

{% elif style == 'sphinx' %}
{{ doc.summary }}

{{ doc.description }}

{% for attr in doc.attributes %}
:ivar {{ attr.name }}: {{ attr.description }}
:vartype {{ attr.name }}: {{ attr.type }}
{% endfor %}

{% elif style == 'jsdoc' %}
/**
 * {{ doc.summary }}
 *
 * {{ doc.description }}
 *
{% for attr in doc.attributes %}
 * @property { {{ attr.type }} } {{ attr.name }} - {{ attr.description }}
{% endfor %}
{% if doc.examples %}
 *
 * @example
{% for example in doc.examples %}
 * {{ example.description }}
 * {{ example.code }}
{% endfor %}
{% endif %}
 */
{% endif %}
