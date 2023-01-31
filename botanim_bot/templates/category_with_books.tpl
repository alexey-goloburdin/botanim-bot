<b>{{ category.name }}</b><br>
<br>
{% for book in category.books %}
  {% if start_index is none: %}◦{% else %}{{ start_index + loop.index }}.{% endif %} {{ book.name }}
    {% if book.is_started() %}
      —<b>
      {% if book.is_finished() %}
        прочитана
      {% else %}
        читаем сейчас
      {% endif %}
      . {{ book.read_comments }}
    </b>
  {% elif book.is_planned(): %}
    —<b>
      будем читать с {{ book.read_start }} по {{ book.read_finish }}.
      {{ book.read_comments }}
    </b>
  {% endif %}
<br>
{% endfor %}
