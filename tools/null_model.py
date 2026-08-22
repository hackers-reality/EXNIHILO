#!/usr/bin/env python3
"""Monte Carlo null model for nearby dictionary-word clusters.

The observed dataset and every synthetic trial are scanned with the same
Aho-Corasick matcher. Cluster selection is streamed with a small heap, so the
program does not materialize every word hit in a huge Python list.
"""
from __future__ import annotations
import argparse, hashlib, heapq, random
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
    q=deque(nxt[0].values())
    while q:
        r=q.popleft()
        for x,u in list(nxt[r].items()):
            q.append(u)
            f=fail[r]
            while f and x not in nxt[f]:
                f=fail[f]
            fail[u]=nxt[f].get(x,0)
            out[u].extend(out[fail[u]])
    return nxt,fail,out,words


def count_clusters_stream(chunks,nxt,fail,out,words,gap,min_hits):
    """Count clusters using the same greedy non-overlap rule as the old code.

    Hits are held only until their start position is older than max_word_len;
    after that no future match can have the same or an earlier start.
    """
    max_len=max(map(len,words))
    pending=[]
    state=0
    last_end=-1
    clusters=0
    cluster_count=0
    prev_end=None
    pos=0

    def consume_selected(s,e):
        nonlocal last_end, clusters, cluster_count, prev_end
        if s < last_end:
            return
        last_end=e
        if prev_end is None or s-prev_end<=gap:
            cluster_count+=1
        else:
            if cluster_count>=min_hits:
                clusters+=1
            cluster_count=1
        prev_end=e

    for data in chunks:
        for x in data:
            pos += 1
            while state and x not in nxt[state]:
                state=fail[state]
            state=nxt[state].get(x,0)
            for wi in out[state]:
                L=len(words[wi])
                s=pos-L
                # heap key: earliest start, then longest match first.
                heapq.heappush(pending,(s,-L,pos))

            cutoff=pos-max_len
            while pending and pending[0][0] <= cutoff:
                s,neg_len,e=heapq.heappop(pending)
                consume_selected(s,e)

    # At EOF every remaining hit is now safe to process in start order.
    while pending:
        s,neg_len,e=heapq.heappop(pending)
        consume_selected(s,e)

    if cluster_count>=min_hits:
        clusters+=1
    return clusters


def file_chunks(path,chunk_size):
    with path.open('rb') as f:
        while True:
            chunk=f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def random_chunks(nbytes,rng,chunk_size):
    remaining=nbytes
    while remaining:
        n=min(chunk_size,remaining)
        yield rng.randbytes(n)
        remaining-=n


def sha256_file(path,chunk_size):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while True:
            chunk=f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('dataset',type=Path)
    p.add_argument('--lang',default='en'); p.add_argument('--wordlist',default='large')
    p.add_argument('--max-words',type=int,default=200000); p.add_argument('--min-length',type=int,default=5)
    p.add_argument('--gap',type=int,default=16); p.add_argument('--min-hits',type=int,default=2)
    p.add_argument('--trials',type=int,default=100); p.add_argument('--seed',type=int,default=20260822)
    p.add_argument('--chunk',type=int,default=8*1024*1024)
    args=p.parse_args()

    nbytes=args.dataset.stat().st_size
    nxt,fail,out,words=build_automaton(args.lang,args.wordlist,args.max_words,args.min_length)
    observed=count_clusters_stream(
        file_chunks(args.dataset,args.chunk),nxt,fail,out,words,args.gap,args.min_hits
    )
    digest=sha256_file(args.dataset,args.chunk)

    rng=random.Random(args.seed); values=[]
    print(f'Dataset bytes:       {nbytes:,}',flush=True)
    print(f'SHA-256:             {digest}',flush=True)
    print(f'Candidates:           {len(words)}',flush=True)
    print(f'Min word length:      {args.min_length}',flush=True)
    print(f'Gap:                  {args.gap} bytes',flush=True)
    print(f'Min hits per cluster: {args.min_hits}',flush=True)
    print(f'Observed clusters:    {observed}',flush=True)
    print(f'Null trials:          {args.trials:,} (size-matched)',flush=True)

    for t in range(1,args.trials+1):
        value=count_clusters_stream(
            random_chunks(nbytes,rng,args.chunk),nxt,fail,out,words,args.gap,args.min_hits
        )
        values.append(value)
        if t==1 or t%10==0 or t==args.trials:
            print(f'Trial {t}/{args.trials}: clusters={value}',flush=True)

    mean=sum(values)/len(values); ge=sum(v>=observed for v in values); zero=sum(v==0 for v in values)
    print(f'Null mean:            {mean:.6g}')
    print(f'Null median:          {sorted(values)[len(values)//2]}')
    print(f'Null maximum:         {max(values)}')
    print(f'Null zero fraction:   {zero/len(values):.6g}')
    print(f'P(null >= observed):  {ge/len(values):.6g}')

if __name__=='__main__': main()
