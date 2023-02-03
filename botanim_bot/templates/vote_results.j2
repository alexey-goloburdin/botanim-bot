<b>ТОП книг
  {% if leaders.voting.is_voting_has_passed() %}прошедшего{% else %}текущего{% endif %}
  голосования</b><br>
<br>
{% if leaders.leaders|length == 0 %}
  Пока никто не проголосовал, ты можешь стать первым, вжух!<br>
{% else %}
  {% for books_in_rank in leaders.leaders %}
  {{ loop.index }}. 
    {% if books_in_rank.books|length > 1 %}
      Несколько книг занимают это место:<br>
    {% endif %}
    {% for book in books_in_rank.books %}
      {% if books_in_rank.books|length > 1 %}{FOURPACES}{% endif %}{{ book.book_name }}
      <br>
    {% endfor %}
  {% endfor %}
{% endif %}
<br>
<i>Даты голосования: с {{ leaders.voting.voting_start }} по
  {{ leaders.voting.voting_finish }}<br>
  Голосов: {{ leaders.votes_count }}</i><br>
<br>
{% if not your_vote %}
Ты ещё не проголосовал.
{% else %}
<b>Твой выбор</b><br>
<br>
1. {{ your_vote.first_book_name }}<br>
2. {{ your_vote.second_book_name }}<br>
3. {{ your_vote.third_book_name }}<br>
{% endif %}
<br>
{% if not leaders.voting.is_voting_has_passed() %}
Переголосовать: /vote
{% endif %}
