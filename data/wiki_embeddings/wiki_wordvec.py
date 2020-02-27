#%%
import numpy as np
import pickle

with open("wiki.zh.vector") as f:
    raw = f.readlines()

words = []
wordvecs = []
for i, l in enumerate(raw):
    if i == 0: continue
    
    l = l.split()
    # Bug in vector file: wiki.zh.vector
    if len(l) != 401:
        print(f"{i}th word: `{l[0]}` vector length = {len(l) - 1}")
        continue

    word = l[0]
    vec = np.array( [float(e) for e in l[1:]] , dtype='float')
    vec = vec / np.linalg.norm(vec)  # regularize to unit length

    # Add word
    words.append(word)
    wordvecs.append(vec)

#%%
wordvecs = np.array(wordvecs)

np.save("wiki_zh-vec.npy", wordvecs)
with open("wiki_zh-vocab.pkl", "wb") as f:
    pickle.dump(words, f)