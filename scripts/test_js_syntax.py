from pathlib import Path

def check_brackets(file_path):
    text = Path(file_path).read_text(encoding='utf-8')
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    in_str = False
    str_char = ''
    in_comm = False
    in_blk_comm = False
    i = 0
    while i < len(text):
        c = text[i]
        nxt = text[i+1] if i + 1 < len(text) else ''
        if not in_str and not in_comm and not in_blk_comm:
            if c == '/' and nxt == '/':
                in_comm = True
                i += 2
                continue
            elif c == '/' and nxt == '*':
                in_blk_comm = True
                i += 2
                continue
            elif c in ('"', "'", '`'):
                in_str = True
                str_char = c
                i += 1
                continue
            elif c in ('(', '[', '{'):
                stack.append((c, i))
            elif c in (')', ']', '}'):
                if not stack or stack[-1][0] != pairs[c]:
                    return False, f'Mismatched {c} at index {i}'
                stack.pop()
        elif in_comm:
            if c == '\n':
                in_comm = False
        elif in_blk_comm:
            if c == '*' and nxt == '/':
                in_blk_comm = False
                i += 2
                continue
        elif in_str:
            if c == '\\':
                i += 2
                continue
            elif c == str_char:
                in_str = False
        i += 1
    if stack:
        return False, f'Unclosed {stack[-1][0]} at index {stack[-1][1]}'
    return True, 'OK'

failed = 0
for p in sorted(Path('Houses').glob('**/*.js')):
    ok, msg = check_brackets(p)
    if not ok:
        print(f'FAIL {p}: {msg}')
        failed += 1
    else:
        print(f'PASS {p}')

if failed == 0:
    print('ALL JS FILES PASSED BRACKET BALANCE!')
else:
    print(f'{failed} files failed!')
