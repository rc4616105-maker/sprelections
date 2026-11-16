# Test logic for edit-votes.js renderBallotsTable
ballots = [
    {'admissionNo': '7016', 'fullName': 'SAMANTHVIKA LANDE', 'className': '7', 'section': 'ALLURI SITARAMARAJU', 'houseCode': 'HANUMAN', 'status': 'cancelled', 'cancelledBy': 'rc4616105@gmail.com', 'cancelledAt': '2026-11-16T17:19:12Z'}
]

voter_map = {}
for b in ballots:
    adm = b['admissionNo']
    if adm not in voter_map:
        voter_map[adm] = {'admissionNo': adm, 'fullName': b['fullName'], 'hasAccepted': False, 'hasCancelled': False, 'ballots': []}
    v = voter_map[adm]
    v['ballots'].append(b)
    if b['status'] == 'accepted': v['hasAccepted'] = True
    if b['status'] == 'cancelled': v['hasCancelled'] = True

for status in ['accepted', 'cancelled', 'all']:
    filtered = [v for v in voter_map.values() if 
        (status == 'accepted' and v['hasAccepted']) or
        (status == 'cancelled' and (v['hasCancelled'] and not v['hasAccepted'])) or
        (status == 'all')
    ]
    print(f'Status: {status} -> {len(filtered)} voters')

print('Test successful!')
