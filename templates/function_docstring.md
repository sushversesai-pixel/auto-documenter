{% if style == 'google' %}
{{ doc.summary }}

{{ doc.description }}

Args:
{% for param in doc.parameters %}
    {{ param.name }} ({{ param.type }}): {{ param.description }}
        {% if not param.required %}Optional. {% endif %}
{% endfor %}

{% if doc.returns %}
Returns:
    {{ doc.returns.type }}: {{ doc.returns.description }}
{% endif %}

{% if doc.raises %}
Raises:
{% for exception in doc.raises %}
    {{ exception.exception }}: {{ exception.description }}
{% endfor %}
{% endif %}

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

Parameters
----------
{% for param in doc.parameters %}
{{ param.name }} : {{ param.type }}
    {{ param.description }}
{% endfor %}

{% if doc.returns %}
Returns
-------
{{ doc.returns.type }}
    {{ doc.returns.description }}
{% endif %}

{% if doc.raises %}
Raises
------
{% for exception in doc.raises %}
{{ exception.exception }}
    {{ exception.description }}
{% endfor %}
{% endif %}

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

{% for param in doc.parameters %}
:param {{ param.name }}: {{ param.description }}
:type {{ param.name }}: {{ param.type }}
{% endfor %}

{% if doc.returns %}
:returns: {{ doc.returns.description }}
:rtype: {{ doc.returns.type }}
{% endif %}

{% if doc.raises %}
{% for exception in doc.raises %}
:raises {{ exception.exception }}: {{ exception.description }}
{% endfor %}
{% endif %}

{% elif style == 'jsdoc' %}
/**
 * {{ doc.summary }}
 *
 * {{ doc.description }}
 *
{% for param in doc.parameters %}
 * @param { {{ param.type }} } {{ param.name }} - {{ param.description }}
{% endfor %}
{% if doc.returns %}
 * @returns { {{ doc.returns.type }} } {{ doc.returns.description }}
{% endif %}
{% if doc.raises %}
{% for exception in doc.raises %}
 * @throws { {{ exception.exception }} } {{ exception.description }}
{% endfor %}
{% endif %}
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
