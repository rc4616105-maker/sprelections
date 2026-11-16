houses = ['bheeshma', 'central', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']

for h in houses:
    with open(f'Houses/{h}/app.js', 'r', encoding='utf-8') as f:
        code = f.read()
    stack = []
    pairs = {')':'(', '}':'{', ']':'['}
    line = 1
    col = 1
    error = None
    in_str = None
    in_line_comment = False
    in_block_comment = False
    i = 0
    while i < len(code):
        ch = code[i]
        if ch == '\n':
            line += 1
            col = 1
            in_line_comment = False
            i += 1
            continue
        if in_line_comment:
            i += 1
            col += 1
            continue
        if in_block_comment:
            if ch == '*' and i+1 < len(code) and code[i+1] == '/':
                in_block_comment = False
                i += 2
                col += 2
                continue
            i += 1
            col += 1
            continue
        if in_str:
            if ch == '\\':
                i += 2
                col += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            col += 1
            continue
        if ch == '/' and i+1 < len(code) and code[i+1] == '/':
            in_line_comment = True
            i += 2
            col += 2
            continue
        if ch == '/' and i+1 < len(code) and code[i+1] == '*':
            in_block_comment = True
            i += 2
            col += 2
            continue
        if ch in ('"', "'", '`'):
            in_str = ch
            i += 1
            col += 1
            continue
        if ch in '({[':
            stack.append((ch, line, col))
        elif ch in ')}]':
            if not stack:
                error = f"Unmatched closing {ch} at line {line}:{col}"
                break
            top, tl, tc = stack.pop()
            if pairs[ch] != top:
                error = f"Mismatched {top} from line {tl}:{tc} with {ch} at line {line}:{col}"
                break
        i += 1
        col += 1
    if not error and stack:
        top, tl, tc = stack[-1]
        error = f"Unclosed {top} from line {tl}:{tc}"
    if error:
        print(f"{h}: FAILED - {error}")
    else:
        print(f"{h}: PASSED 100% (bracket balance OK)")
