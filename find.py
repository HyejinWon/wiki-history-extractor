import argparse

def detokenize(line):
        line = line.split()
        line = ''.join(line)
        return line.replace('▁', ' ')


def finddiff(tline, sline):
        result = []
        for t, s in zip(tline, sline):
                t = detokenize(t)
                s = detokenize(s)

                if t.strip() != s.strip():
                        temp = extractdiff(t.strip(), s.strip())
                        result.append((t, s, temp))
                        #result.append((t,s,('\t','\t')))
        return result

def extractdiff(t,s):
        tlist = t.split()
        slist = s.split()

        # forward
        for i in range(len(tlist)):
                try:
                        if tlist[i] != slist[i]:
                                tlist = tlist[i:]
                                slist = slist[i:]
                                break
                except:
                        tlist = tlist[i-1:]
                        slist = slist[i-1:]
        # backward
        for i in range(1, len(tlist)+1):

                try:
                        if (tlist[-i] != slist[-i] ) and i != 1:
                                tlist = tlist[:-i+1]
                                slist = slist[:-i+1]
                                break
                        elif (tlist[-i] != slist[-i] ) and i == 1:
                                break
                except:
                        tlist = tlist[-i]
                        slist = []
                        print(i, tlist, slist)

        return tlist, slist

def write_result(args, result):
        w = open(args.write,'w')
        count = 0
        for t, s, r in result:
                count += 1
                w.write('-------------------------------------\n')
                w.write('O : '+t+'\n')
                w.write('R : '+s+'\n')
                w.write('diff \n')
                w.write(' '.join(r[0])+'\n' + ' '.join(r[1])+'\n')
                w.write('-------------------------------------\n')
        w.close()
        print(count)
        return 0

if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument('--ref',type=str,help='reference file')
        parser.add_argument('--sys',type=str,help='system output file')
        parser.add_argument('--write',type=str, help='result file')
        args = parser.parse_args()

        t = open(args.ref,'r')
        s = open(args.sys,'r')

        tline = t.readlines()
        sline = s.readlines()

        print('----find different part----')
        result = finddiff(tline, sline)

        print('----write file part----')
        write_result(args, result)
        print('----END----')
        print(len(tline))
        t.close()
