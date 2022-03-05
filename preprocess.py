#!/usr/bin/env python3
import os,sys
from collections import deque

dic = 'oxford_ame_3000'
curr_dir = '.'
dir = os.path.join(curr_dir, dic)
filename = os.path.join(curr_dir, dic + ".txt")

word_types = [
 'number',
 'definite article',
 'indefinite article',
 'infinitive marker',
 'adj.',
 'adv.',
 'auxiliary v.',
 'conj.',
 'det.',
 'exclam.',
 'modal v.',
 'n.',
 'noun.',
 'prep.',
 'pron.',
 'v.',
 ]

word_levels = [('%c%d' % (i,o)) for i in ['A','B'] for o in range(1,10,1)]


#cache concated text from all the files.
def cached_read_data(data_file, data_dir=dir):
    if not os.path.exists(data_file):
        with open(data_file, 'w') as cachefile:
            paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
            texts = [open(p).read() for p in paths]
            full_text = '\n'.join([one_text.strip() for one_text in texts])
            cachefile.write(full_text)
            cachefile.flush()
    full_txt = open(data_file).read().strip()
    return full_txt


# Correction for line continuity
def line_continuity(text):
    line_array = []
    for line in text.splitlines():
        line = line.strip()
        if len(line_array)>0 and line_array[-1][-1] in (',', '.','/'):
            full_line = line_array.pop() + ' ' + line
            line_array.append(full_line)
        else:
            line_array.append(line)
    text = '\n'.join(line_array)
    return text


def get_word(marks, word=''):
    while len(marks)>0:
        # Correction for word:
        #  "all det., pron. A1, adv. A2"
        #  "all right adj./adv. A2"
        if len(word)>0 and any([marks.startswith(kw) for kw in word_types]):
            break
        
        #combine the word and note as a packed word
        # eg: will use 'light(from the sun/a lamp)' as the packed word for:
        #    'light (from the sun/a lamp) n.,'  
        if marks.startswith('('):
            idx = marks.find(')')
            word = word + marks[:(1+idx)]
            marks = marks[(1+idx):].strip()
            continue
            
        piece,_,marks = marks.partition(' ')
        marks = marks.lstrip()

        # remove ' '(char. space) for multi-word in one line:
        # eg: "a, an indefinite article A1"
        if len(word) == 0:
            word = piece
            continue
        elif word.endswith(','):
            word = (word + piece) if len(piece)>0 else word
            continue
        else:
            word = (word + ' ' + piece) if len(piece)>0 else word

    return word, marks


def get_attrs(marks, word, line):
    attrs = []
    # multi-word_type: "all right adj./adv. A2" -> "all right adj.,adv. A2"
    marks = marks.replace('/', ',')

    # multi-levels
    levels =[r.strip() for r in marks.split('|')]
    for one_level in levels:
        wtypes, _, level = one_level.rpartition(' ')

        if level not in word_levels:
            print('ERROR:%s' % repr(marks), repr(line), ' -> ', word, attrs)
            break

        level_wtypes = [(tp.strip(), level) for tp in wtypes.split(',')]
        multi_attr = len(level_wtypes) if len(level_wtypes) > 1 else 0

        attrs.extend(level_wtypes)
    return attrs


# For example:
# use char. '|' as unified seperator for multi-levels 
# use char. ' ' as unified seperator between word type and level
#  forturnately enumerate all word types and levels is possible.
def format_text(text):
    results = []

    # "all det., pron. A1, adv. A2" -> "all det., pron. A1| adv. A2"
    for k,n in [('%s,' % lv, '%s|' % lv)  for lv in word_levels]: 
        text = text.replace(k,n)
    
    #from '{WORD_TYPE}{LEVEL}' to '{WORD_TYPE} {LEVEL}'
    # eg: "climb v. A1, n.B1" -> "climb v. A1, n. B1"
    ft=[('%s%s' % (tp,lv), '%s %s' % (tp,lv)) for tp in word_types for lv in word_levels]
    for k,n in ft: 
        text = text.replace(k,n)

    for line in text.splitlines():
        if len(line) < 1:
            continue

        word, marks = '', line.strip()
   
        if 0 and m.startswith('bear'):
            import pdb;pdb.set_trace()

        new_word, new_marks = get_word(marks, word)
        attrs = get_attrs(new_marks, new_word, line)

        results.append((new_word,attrs))
   
    return results

   
def print_results(rets, verbose=0):
    oarray = []
    wtypes = set()
    for word, attrs in rets:
        wtypes.update([wtp for wtp, level in attrs])
        word_fmt = '%s|%s' %(word, ','.join(['%s:%s'%(tp,lv) for tp, lv in attrs]))
        oarray.append(word_fmt)

    if verbose > 0:
        print('\n'.join(sorted(wtypes)))

    if verbose > 1:
        print('\n'.join(oarray))


def main():
    v = int(sys.argv[-1]) if len(sys.argv) > 1 and sys.argv[-1].isdigit() else 0
    import pdb;pdb.set_trace()
    orig_txt = cached_read_data(filename)
    new_txt = line_continuity(orig_txt)
    results = format_text(new_txt)
    print_results(results, v)


if '__main__' == __name__:
    main()

