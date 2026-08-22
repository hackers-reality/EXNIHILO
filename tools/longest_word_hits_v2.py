#!/usr/bin/env python3
"""Fast streaming longest-word scanner using Aho-Corasick."""
from __future__ import annotations
import argparse, hashlib
from collections import deque
from pathlib import Path
from wordfreq import iter_wordlist, zipf_frequency


def build_automaton(lang, wordlist, max_words, min_length):
    words=[]; seen=set()
    for word in iter_wordlist(lang, wordlist=wordlist):
        if len(words) >= max_words: break
        b=word.encode('utf-8')
        if len(b)<min_length or b in seen: continue
        seen.add(b); words.append((b, word, zipf_frequency(word, lang)))
    nxt=[{}]; fail=[0]; out=[[]]
    for wi,(b,_,_) in enumerate(words):
        node=0
        for x in b:
            if x not in nxt[node]:
                nxt[node][x]=len(nxt); nxt.append({}); fail.append(0); out.append([])
            node=nxt[node][x]
        out[node].append(wi)
    q=deque()
    for node in nxt[0].values(): q.append(node)
    while q:
        r=q.popleft()
        for x,u in nxt[r].items():
            q.append(u); f=fail[r]
            while f and x not in nxt[f]: f=fail[f]
            fail[u]=nxt[f].get(x,0); out[u].extend(out[fail[u]])
    return nxt,fail,out,words


def main():
    p=argparse.ArgumentParser()
    p.add_argument('dataset',type=Path); p.add_argument('--lang',default='en')
    p.add_argument('--wordlist',default='large'); p.add_argument('--max-words',type=int,default=200000)
    p.add_argument('--min-length',type=int,default=3); p.add_argument('--chunk',type=int,default=8*1024*1024)
    p.add_argument('--top',type=int,default=100)
    a=p.parse_args()
    nxt,fail,out,words=build_automaton(a.lang,a.wordlist,a.max_words,a.min_length)
    size=a.dataset.stat().st_size; sha=hashlib.sha256(); state=0; offset=0; hits=[]; seen=set()
    with a.dataset.open('rb') as f:
        while chunk:=f.read(a.chunk):
            sha.update(chunk)
            for j,x in enumerate(chunk):
                while state and x not in nxt[state]: state=fail[state]
                state=nxt[state].get(x,0)
                for wi in out[state]:
                    b,word,z=words[wi]; end=offset+j+1; start=end-len(b)
                    if wi not in seen:
                        seen.add(wi); hits.append((len(b),word,z,start))
            offset += len(chunk)
            print(f'Processed: {offset:,}/{size:,} bytes ({offset/size*100:.1f}%)',flush=True)
    hits.sort(key=lambda h:(-h[0],-h[2],h[3]))
    print(f'Dataset bytes: {size:,}')
    print(f'SHA-256:       {sha.hexdigest()}')
    print(f'Candidates:    {len(words)}')
    print(f'Words with hit:{len(hits)}')
    if hits:
        L=hits[0][0]; longest=[h for h in hits if h[0]==L]
        print(f'Longest byte length: {L}')
        print(f'Longest unique hits: {len(longest)}')
        print('length chars bytes offset zipf word')
        for n,(bl,w,z,s) in enumerate(hits[:a.top]):
            print(f'{bl:6d} {len(w):5d} {bl:5d} {s:10d} {z:5.2f} {w!r}')

if __name__=='__main__': main()
