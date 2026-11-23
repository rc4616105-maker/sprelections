with open('Houses/graphs.html', 'r', encoding='utf-8') as f:
    text = f.read()

b_open = text.count('{')
b_close = text.count('}')
bt = text.count('`')
p_open = text.count('(')
p_close = text.count(')')

assert b_open == b_close, 'Brace mismatch in graphs.html'
assert bt % 2 == 0, 'Backtick mismatch in graphs.html'
assert p_open == p_close, 'Paren mismatch in graphs.html'
assert 'graph-legend-badge' not in text, 'graph-legend-badge should not be present'
assert '👦' not in text, 'Boy emoji should not be in graphs.html'
assert '👧' not in text, 'Girl emoji should not be in graphs.html'
print('graphs.html: ALL CHECKS PASSED!')

with open('Houses/admin/edit-votes.js', 'r', encoding='utf-8') as f:
    ev_text = f.read()

ev_b_open = ev_text.count('{')
ev_b_close = ev_text.count('}')
ev_bt = ev_text.count('`')
ev_p_open = ev_text.count('(')
ev_p_close = ev_text.count(')')

assert ev_b_open == ev_b_close, f'Braces in edit-votes.js: {ev_b_open}/{ev_b_close}'
assert ev_bt % 2 == 0, f'Backticks in edit-votes.js: {ev_bt}'
assert ev_p_open == ev_p_close, f'Parens in edit-votes.js: {ev_p_open}/{ev_p_close}'
print('edit-votes.js: ALL CHECKS PASSED!')
