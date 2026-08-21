#!/usr/bin/env python3
"""Monte Carlo null model for nearby dictionary-word clusters.

The null model must match the observed dataset size. Synthetic data is
streamed in chunks and never written to disk. A fast Aho-Corasick matcher
replaces the old Python trie scan so progress is visible and experiments are
practical on phones.
"""
from __future__ import annotations
import argparse, hashlib, random
from pathlib import Path
from collections import deque
from wordfreq import iter_wordlist


def build_automaton(lang, wordlist, max_words, min_length):
    words=[]
    seen=set()
    for word in iter_wordlist(lang, wordlist=wordlist):
        if len(words) >= max_words:
            break
        b=word.encode('utf-8')
        if len(b) < min_length or b in seen:
            continue
        seen.add(b); words.append(b)
    nxt=[{}]; fail=[0]; out=[[]]
    for idx,b in enumerate(words):
        node=0
        for x in b:
            if x not in nxt[node]:
                nxt[node][x]=len(nxt); nxt.append({}); fail.append(0); out.append([])
            node=nxt[node][x]
        out[node].append(idx)
    q=deque()
    for x,node in list(nxt[0].items()):
        q.append(node); fail[node]=0
    while q:
        r=q.popleft()
        for x,u in list(nxt[r].items()):
            q.append(u); f=fail[r]
            while f and x not in nxt[f]: f=fail[f]
            fail[u]=nxt[f].get(x,0)
            out[u].extend(out[fail[u]])
    return nxt,fail,out,words


def count_clusters(data,nxt,fail,out,words,gap,min_hits):
    hits=[]; state=0
    for i,x in enumerate(data):
        while state and x not in nxt[state]: state=fail[state]
        state=nxt[state].get(x,0)
        for wi in out[state]:
            L=len(words[wi]); hits.append((i+1-L,i+1))
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
    p.add_argument('--trials',type=int,default=100); p.add_argument('--seed',type=int,default=20260822)
    p.add_argument('--chunk',type=int,default=1000000)
    args=p.parse_args()
    data=args.dataset.read_bytes()
    nxt,fail,out,words=build_automaton(args.lang,args.wordlist,args.max_words,args.min_length)
    observed=count_clusters(data,nxt,fail,out,words,args.gap,args.min_hits)
    rng=random.Random(args.seed); values=[]; nbytes=len(data)
    print(f'Dataset bytes:       {nbytes:,}',flush=True)
    print(f'SHA-256:             {hashlib.sha256(data).hexdigest()}',flush=True)
    print(f'Candidates:           {len(words)}',flush=True)
    print(f'Min word length:      {args.min_length}',flush=True)
    print(f'Gap:                  {args.gap} bytes',flush=True)
    print(f'Min hits per cluster: {args.min_hits}',flush=True)
    print(f'Observed clusters:    {observed}',flush=True)
    print(f'Null trials:          {args.trials:,} (size-matched)',flush=True)
    for t in range(1,args.trials+1):
        buf=bytearray();
        while len(buf)<nbytes:
            buf.extend(rng.randbytes(min(args.chunk,nbytes-len(buf))))
        values.append(count_clusters(buf,nxt,fail,out,words,args.gap,args.min_hits))
        if t==1 or t%10==0 or t==args.trials:
            print(f'Trial {t}/{args.trials}: clusters={values[-1]}',flush=True)
    mean=sum(values)/len(values); ge=sum(v>=observed for v in values); zero=sum(v==0 for v in values)
    print(f'Null mean:            {mean:.6g}')
    print(f'Null median:          {sorted(values)[len(values)//2]}')
    print(f'Null maximum:         {max(values)}')
    print(f'Null zero fraction:   {zero/len(values):.6g}')
    print(f'P(null >= observed):  {ge/len(values):.6g}')

if __name__=='__main__': main()
