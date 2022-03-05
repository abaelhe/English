#!/usr/bin/env python3
import os,sys,json
from collections import deque

dic = 'oxford_ame_3000'
curr_dir = '.'
dir = os.path.join(curr_dir, dic)
filename = os.path.join(curr_dir, dic + ".txt")
filejson = os.path.join(curr_dir, dic + ".json")

word_types = {
        'n.':0,
        'noun.':0,
        'pron.':1,
        'v.':2,
        'auxiliary v.':3,
        'modal v.':4,
        'adv.':5,
        'prep.':6,
        'adj.':7,
        'conj.':8,
        'det.':9,
        'exclam.':10,
        'number':11,
        'definite article':12,
        'indefinite article':13,
        'infinitive marker':14,
 }

# word_levels = [('%c%d' % (i,o)) for i in ['A','B'] for o in range(1,10,1)]
word_levels = ["A1", "A2", "B1", "B2"]


#cache concated text from all the files.
def cached_read_data(data_file, data_dir=dir):
    full_text = ''
    if not os.path.exists(data_file):
        with open(data_file, 'w') as cachefile:
            paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
            texts = [open(p).read() for p in paths]
            full_text = '\n'.join([one_text.strip() for one_text in texts])
            cachefile.write(full_text)
            cachefile.flush()
    else:
        with open(data_file, 'r') as cachefile:
            full_text = cachefile.read()
    return full_text


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

    # unified name for Noun
    text = text.replace('noun.', 'n.')

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
   
        new_word, new_marks = get_word(marks, word)
        attrs = get_attrs(new_marks, new_word, line)

        results.append((new_word,attrs))
   
    return results

def save_results(rets, data_file=filejson, force=0):
    if force != 0 or not os.path.exists(data_file):
        with open(data_file, 'w') as cachefile:
            ret_dic = {}
            for word, attrs in rets:
                if word not in ret_dic:
                    ret_dic[word] = {}
                wdic = ret_dic[word]
                for wtype, wlevel in attrs:
                    wdic[wtype] = wlevel

            json_text = json.dumps(ret_dic)
            cachefile.write(json_text)
            cachefile.flush()
            return ret_dic


def read_results(data_file=filejson):
    if os.path.exists(data_file):
        with open(data_file, 'r') as cachefile:
            ret_dic = json.load(cachefile)
            return ret_dic

   
def print_results(rets, verbose=0):
    oarray = []
    wtypes = set()
    for word, attrs in rets:
        wtypes.update([wtp for wtp, level in attrs])
        word_fmt = '%s|%s' %(word, ','.join(['%s:%s'%(tp,lv) for tp, lv in attrs]))
        oarray.append(word_fmt)

    if verbose == 1:
        print(repr(sorted(wtypes)))
    elif verbose == 2:
        print('\n'.join(oarray))
    elif verbose == 3:
        print('\n'.join(oarray))
        print(repr(sorted(wtypes)))


def main():
    v = int(sys.argv[-1]) if len(sys.argv) > 1 and sys.argv[-1].isdigit() else 0
    json_dic = read_results()
    if json_dic:
        pass
    else:
        orig_txt = cached_read_data(filename)
        new_txt = line_continuity(orig_txt)
        results = format_text(new_txt)
        json_dic = save_results(results)
        print_results(results, v)


if '__main__' == __name__:
    main()

