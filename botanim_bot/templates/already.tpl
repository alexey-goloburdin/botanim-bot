Прочитанные книги:<br>
<br>
{% for book in already_read_books %}
  {{ loop.index }}. {{ book.name }}<br><br>
  {{ book.read_comments }}. Читали с {{ book.read_start }} по {{ book.read_finish }}.
  <br><br>
{% endfor %}
