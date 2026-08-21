#!/usr/bin/env python3
"""Monte Carlo null model for nearby dictionary-word clusters.

Uses random bytes only; it does not write giant synthetic datasets.
The statistic is the same longest-match, non-overlapping cluster rule used
by independent_clusters.py, evaluated on sampled windows.
"""
from __future__ import annotations
import argparse, hashlib, random
from pathlib import Path
from wordfreq import iter_wordlist, zipf_frequency


def build_trie(lang, wordlist, max_words, min_length):
    candidates={}
    for word in iter_wordlist(lang, wordlist=wordlist):
        if len(candidates)>=max_words: break
        if len(word)<min_length: continue
        b=word.encode('utf-8')
        candidates.setdefault(b,(word,zipf_frequency(word,lang)))
    root={}
    for b in candidates:
        node=root
        for x in b: node=node.setdefault(x,{})
        node[None]=b
    return root,candidates


def count_clusters(data, root, gap, min_hits):
    n=len(data); hits=[]
    for i in range(n):
        node=root; j=i; best=None
        while j<n and data[j] in node:
            node=node[data[j]]; j+=1
            if None in node: best=(i,j)
        if best: hits.append(best)
    hits.sort(key=lambda h:(h[0],-(h[1]-h[0])))
    selected=[]; last_end=-1
    for s,e in hits:
        if s>=last_end:
            selected.append((s,e)); last_end=e
    clusters=0; count=0; prev_end=None
    for s,e in selected:
        if prev_end is None or s-prev_end<=gap:
            count+=1
        else:
            if count>=min_hits: clusters+=1
            count=1
        prev_end=e
    if count>=min_hits: clusters+=1
    return clusters


def main():
    p=argparse.ArgumentParser()
    p.add_argument('dataset',type=Path)
    p.add_argument('--lang',default='en'); p.add_argument('--wordlist',default='large')
    p.add_argument('--max-words',type=int,default=200000); p.add_argument('--min-length',type=int,default=5)
    p.add_argument('--gap',type=int,default=16); p.add_argument('--min-hits',type=int,default=2)
    p.add_argument('--trials',type=int,default=1000); p.add_argument('--window',type=int,default=1000000)
    p.add_argument('--seed',type=int,default=20260822)
    args=p.parse_args()
    data=args.dataset.read_bytes(); root,candidates=build_trie(args.lang,args.wordlist,args.max_words,args.min_length)
    observed=count_clusters(data,root,args.gap,args.min_hits)
    rng=random.Random(args.seed); values=[]
    for _ in range(args.trials):
        sample=rng.randbytes(args.window)
        values.append(count_clusters(sample,root,args.gap,args.min_hits))
    mean=sum(values)/len(values); ge=sum(v>=observed for v in values)
    zero=sum(v==0 for v in values)
    print(f'Dataset bytes:       {len(data):,}')
    print(f'SHA-256:             {hashlib.sha256(data).hexdigest()}')
    print(f'Candidates:           {len(candidates)}')
    print(f'Min word length:      {args.min_length}')
    print(f'Gap:                  {args.gap} bytes')
    print(f'Min hits per cluster: {args.min_hits}')
    print(f'Observed clusters:    {observed}')
    print(f'Null trials:          {args.trials:,}')
    print(f'Null window:          {args.window:,} bytes')
    print(f'Null mean:            {mean:.6g}')
    print(f'Null maximum:         {max(values)}')
    print(f'Null zero fraction:   {zero/len(values):.6g}')
    print(f'P(null >= observed):  {ge/len(values):.6g}')

if __name__=='__main__': main()
