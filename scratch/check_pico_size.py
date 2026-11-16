import os

houses = ['bheeshma', 'central', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'assets']
for h in houses:
    path = f'Houses/{h}/pico.js'
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f'{path}: size={size}')
    else:
        print(f'{path}: NOT FOUND')
