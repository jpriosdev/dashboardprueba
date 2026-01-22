import re,json
s = open('dashboard_executive.html', encoding='utf-8').read()
m = re.search(r"window\.DASH_DATA\s*=\s*(\{.*?\})\s*;", s, re.S)
if not m:
    print('NO_DASH_DATA')
else:
    data = json.loads(m.group(1))
    print('rows:', len(data.get('rows',[])))
    rows = data.get('rows',[])
    def apply_filter(rows, sprint='', ttype='', prio='', status=''):
        def match(r):
            if sprint and 'todos' not in sprint.lower() and sprint!='':
                if not r.get('sprint') or sprint not in r.get('sprint'):
                    return False
            if ttype and 'todos' not in ttype.lower() and ttype!='':
                tt = ttype.lower()
                if tt=='bugs' and r.get('type','').lower()!='bug':
                    return False
            if prio and 'tod' not in prio.lower() and prio!='':
                if not r.get('priority') or prio.lower() not in r.get('priority','').lower():
                    return False
            return True
        f = [r for r in rows if match(r)]
        from collections import Counter
        return len(f), Counter(r.get('priority') for r in f)
    print('no filter:', apply_filter(rows))
    print('type=Bug:', apply_filter(rows, ttype='Bugs'))
