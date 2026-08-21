#!/usr/bin/env python3
"""Find nearby dictionary-word hits in a frozen byte dataset."""
from __future__ import annotations
import argparse, hashlib
from collections import defaultdict
from pathlib import Path
from wordfreq import iter_wordlist, zipf_frequency


def main():
    p=argparse.ArgumentParser()
    p.add_argument('dataset',type=Path)
    p.add_argument('--lang',default='en')
    p.add_argument('--wordlist',choices=['small','large','best'],default='small')
    p.add_argument('--max-words',type=int,default=200000)
    p.add_argument('--min-zipf',type=float,default=0.0)
    p.add_argument('--gap',type=int,default=32,help='maximum byte gap between hit starts')
    p.add_argument('--min-hits',type=int,default=2)
    p.add_argument('--top',type=int,default=50)
    args=p.parse_args()
    data=args.dataset.read_bytes(); n=len(data)
    print(f'Dataset bytes: {n:,}')
    print(f'SHA-256:       {hashlib.sha256(data).hexdigest()}')
    candidates={}
    for word in iter_wordlist(args.lang,wordlist=args.wordlist):
        if len(candidates)>=args.max_words: break
        if len(word)<3: continue
        z=zipf_frequency(word,args.lang)
        if z<args.min_zipf: continue
        b=word.encode('utf-8')
        candidates.setdefault(b,(word,z))
    root={}
    for b in candidates:
        node=root
        for x in b: node=node.setdefault(x,{})
        node[None]=True
    hits=[]
    for i in range(n):
        node=root; j=i
        while j<n and data[j] in node:
            node=node[data[j]]; j+=1
            if None in node:
                word,z=candidates[data[i:j]]
                hits.append((i,j,word,z))
    hits.sort()
    clusters=[]
    cur=[]; last_end=None
    for h in hits:
        if last_end is None or h[0]-last_end<=args.gap:
            cur.append(h)
        else:
            if len(cur)>=args.min_hits: clusters.append(cur)
            cur=[h]
        last_end=max(last_end or h[1],h[1])
    if len(cur)>=args.min_hits: clusters.append(cur)
    clusters.sort(key=lambda c:(-len(c), c[0][0]))
    print(f'Candidates:     {len(candidates)}')
    print(f'Total word hits:{len(hits)}')
    print(f'Clusters:       {len(clusters)}')
    print(f'Gap threshold:  {args.gap} bytes')
    for c in clusters[:args.top]:
        lo=c[0][0]; hi=c[-1][1]
        print(f'\ncluster hits={len(c)} span={hi-lo} offset={lo}')
        print('  '+' | '.join(f"{w!r}@{s-lo}" for s,e,w,z in c))
        ctx=data[max(0,lo-16):min(n,hi+16)]
        print('  ascii: '+''.join(chr(x) if 32<=x<=126 else '.' for x in ctx))

if __name__=='__main__': main()
