import re
import os
import argparse
import statistics
import difflib

from find import extractdiff

w = open('./diff.txt','w')

def split_sentence(lines):
    result_list = []
    for i in lines:
        i = i.strip()
        result = re.sub('다\.','다.###',i)
        result = re.sub('\?','?###',result)
        result = re.sub('!','!###', result)
        result = re.split('###', result)
        result_list.extend(result)
    return result_list

def clean_sentence(lines):
    if re.search(':', lines) or re.search('"',lines) or re.search("'", lines):
        return ""
    elif re.search('png',lines) or re.search('align=', lines) or re.search('width=', lines):
        return ""
    
    if re.search('\(.*\)',lines): #괄호 안에 들어간 것들 다 삭제
        #s, e = re.search('\(.+\)',lines).span()
        #lines = lines[:s]+lines[e:]
        lines = lines.replace(re.search('\s?\(.*\)\s?', lines).group(), '')

    lines = lines.replace('&lt;','').replace('&gt;','')
    lines = re.sub(r'[^a-zA-Zㄱ-ㅣ가-힣0-9.,?!"\'()\s/·]', '',lines)
    lines = re.sub('[\s]{2,}',' ', lines)
    lines = lines.strip()

    return lines

def write_file(args, new, old, _doc):
    trg = open(args.write_path+'/result_val.trg','a')
    src = open(args.write_path+'/result_val.src','a')

    for n, o in zip(new, old):
        if len(n) < 3:
            continue
        #w.write(_doc+'\t'+n.strip() +'\t'+ o.strip() +'\n')
        #w.write(n.strip() +'\t'+ o.strip() +'\n')
        trg.write(o.strip() + '\n')
        src.write(n.strip() + '\n')

    trg.close()
    src.close()

    return 0

def read_file(file):
    return open(file, 'r')

def get_diff(args, diff_lines, _doc):
    '''
    Args
    - diff_lines : list of list, because wiki history data have too many overlab sentence. 
    '''
    value_dic = {}
    for i in diff_lines:
        i = split_sentence(i)
        for j in i:
            if j[:5] in value_dic:
                value_dic[j[:5]] += [j] #list 로 넣어주기 위해서 감쌈
            else:
                value_dic[j[:5]] = [j]
    
    new = []
    old = []
    for v in value_dic.values():
        v_set = set(v)
        if len(v_set) == 1 : continue
        median = statistics.median([len(i) for i in v_set])

        # index가 높을 수록 최근에 수정된 글임
        max_v = -999
        min_v = 999
        for item in v_set:
            if len(item) < median:
                continue
            elif v.index(item) >= max_v:
                max_v = v.index(item)
            elif v.index(item) <= min_v:
                min_v = v.index(item)
        
        # 현재 아래에 나와있는건 중간값을 넘는 max 랑 min index인 것!
        if max_v != -999 and min_v != 999:
            try: # 가끔 difflib에서 너무 오래 걸리는 것들이 있음;;
                if len([ li for li in difflib.ndiff(v[max_v], v[min_v]) if li[0] != ' ']) < 6:
                    _max_v = clean_sentence(v[max_v])
                    _min_v = clean_sentence(v[min_v])
                    
                    # 숫자랑 영어 달라지는거 체크
                    numal_max = re.findall('[0-9,?a-zA-Z]+', _max_v)
                    numal_min = re.findall('[0-9,?a-zA-Z]+', _min_v)

                    # Todo : 한글에서 달라지는거 찾아서 자소 거리 따져서 체크하기
                    # 숫자나 영어 철자 같은게 달라진거는 포함 x 
                    if _max_v != _min_v and abs(len(_max_v) - len(_min_v)) < 3 and numal_max == numal_min:
                        # extractdiff( trg, src)
                        diff_result = extractdiff(_max_v, _min_v)
                        
                        w.write('-----------------------------------\n')
                        w.write('R : '+_max_v+'\nW : '+_min_v+'\n'+str(diff_result)+'\n')
                        w.write('-----------------------------------\n')
                        
                        #print(diff_result)

                        new.append(_max_v)
                        old.append(_min_v)
            except:
                print(v[max_v])    
    write_file(args, new, old, _doc)
        
    return 0

def find_diff(args, fline,_doc):
    '''
    find pages and get difference sentence result
    '''
    result = []
    sub_line = []

    for i in fline:
        if i.startswith('</doc>'):
            get_diff(args, result,_doc)
            result = []
            sub_line = []
        elif i.startswith('<doc id'):
            continue
        else:
            if len(i) < 10 and len(i) > 3: # 의미 없는 문장이나 빈 문장 같은건 제외하기 위해서
                result.append(sub_line)
                sub_line = []
            elif len(i) >= 10 and len(i) < 200:
                sub_line.append(i)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str)
    parser.add_argument('--write-path', type=str)
    args = parser.parse_args()

    dic_list = os.listdir(args.path)

    for _dic in sorted(dic_list):
        path = args.path+'/'+_dic
        doc_list = os.listdir(path)
        print('-----start {}-----'.format(_dic))
        for _doc in sorted(doc_list):
            print(_doc)
            f = read_file(path+'/'+_doc)
            fline = f.readlines()
            result = find_diff(args, fline,_doc)
            f.close()
    w.close()
