#!/usr/bin/env python3
from collections import deque

filename = "./oxford_ame_3000.txt"
orig_txt = open(filename).read().strip()

word_types = [
 'number',
 'adj.',
 'adv.',
 'auxiliary v.',
 'conj.',
 'definite article',
 'det.',
 'exclam.',
 'indefinite article',
 'infinitive marker',
 'modal v.',
 'n.',
 'noun.',
 'prep.',
 'pron.',
 'v.',
 ]

levels = [('%c%d' % (i,o)) for i in ['A','B'] for o in range(1,10,1)]

ret = []
line_array = deque()
# Correction for line continuity
for x in orig_txt.splitlines():
    x = x.strip()
    if len(line_array)>0 and line_array[-1][-1] in (',', '.','/'):
        prev_line = line_array.pop() + ' ' + x 
        line_array.append(prev_line)
    else:
        line_array.append(x)

# Sync And Correction for multi levels split:
new_txt = '\n'.join(line_array)

# For example: "all det., pron. A1, adv. A2" -> "all det., pron. A1| adv. A2"
for k,n in [('%s,' % lv, '%s|' % lv)  for lv in levels]: 
    new_txt = new_txt.replace(k,n)

# Correction for "climb v. A1, n.B1" -> "climb v. A1, n. B1"
for k,n in [('.%s' % lv, '. %s' % lv) for lv in levels]: 
    new_txt = new_txt.replace(k,n)

line_array.clear()
line_array.extend(new_txt.splitlines())

for x in line_array:
    if len(x) < 1:
        continue

    w = ''
    multi_word = False
    multi_level = 0
    multi_attr = 0
    attrs = []
    m = x.strip()

    if 0 and m.startswith('bear'):
        import pdb;pdb.set_trace()
            
    while len(m)>0:
        # Correction for word:
        #  "all det., pron. A1, adv. A2"
        #  "all right adj./adv. A2"
        if len(w)>0 and any([m.startswith(kw) for kw in word_types]):
            break

# Correction for some sort of 'light (from the sun/a lamp) n.,' 
        if m.startswith('('):
            idx = m.find(')')
            w = w + m[:(1+idx)]
            m = m[(1+idx):].strip()
            continue
            
        p,_,m = m.partition(' ')
        m = m.lstrip()

        if p.endswith(','):
            multi_word = True
            p = p.rstrip(',')
            w = (w + ',' + p) if (len(w)>0 and len(p)>0) else p
            continue
        else:
            w = (w + ' ' + p) if w else p

# Correction for some sort of "all right adj./adv. A2"
    m = m.replace('/', ',')

    marks =[r.strip() for r in m.split('|')]

    if len(marks)>1:
        multi_level = len(marks)

    for one_mark in marks:
        s, _, level = one_mark.rpartition(' ')

        if level not in levels:
            print('ERROR:%s' % repr(marks), repr(x), ' -> ', w,_,attrs)
            break

        one_attrs = [(g.strip(),level) for g in s.split(',')]
        multi_attr = len(one_attrs) if len(one_attrs) > 1 else 0

        attrs.extend(one_attrs)

    if multi_level > 0:
        #print('MULTI LEVELS:%s' % multi_level, repr(x), ' -> ', w,_,attrs)
        pass
    if multi_attr > 0:
        #print('MULTI ATTRS:', repr(x), ' -> ', w,_,attrs)
        pass

    ret.append((w, attrs))

ts = []
for w,attrs in ret:
    word_fmt = '%s|%s' %(w, ','.join(['%s:%s'%(h,l) for h, l in attrs]))
    ts.append(word_fmt)
print('\n'.join(sorted(set(ts))))
