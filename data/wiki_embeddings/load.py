#%%
import pickle
import numpy as np

class Embeddings():
    
    def __init__(self):
        self.vocab = None
        self.wi = None
        self.wordvec = None
        self._load()

    def _load(self):
        # Load vocabulary
        with open(f"wiki_zh-vocab.pkl", "rb") as f:
            self.vocab = pickle.load(f)
        # Load wordvec
        self.wordvec = np.load(f"wiki_zh-vec.npy")
        self.wi = {w:i for i, w in enumerate(self.vocab)}
        
    def getWordvec(self, w):
        if isinstance(w, str):
            try:
                idx = self.wi[w]
            except:
                raise Exception("Word not in vocabulary")
        else:
            idx = w
        return self.wordvec[idx]


    def cossim(self, w1, w2, isVec=False):
        """Assume word vectors are normalized"""
        if isinstance(w1, str) or isinstance(w1, int):
            return self.getWordvec(w1).dot(self.getWordvec(w2))
        else:
            return w1.dot(w2)
    
    def analogy(self, a1, a2, b1, top_n=3, e=0.001):
        """Get analogy by cosine multiplication
        
        Parameters
        ----------
        a1 : Union[str, int]
            A word
        a2 : Union[str, int]
            A word
        b1 : Union[str, int]
            A word
        top_n : int, optional
            Number of analogies to return, by default 3
        """

        # Get vocab
        vocab = set(self.wi.keys())
        for w in [a1, a2, b1]:
            if w in vocab:
                vocab.remove(w)

        # Analogy cosine (see Levy et al. 2015)
        def cosMul(b2):
            try:
                out = (self.cossim(b2, a1) * self.cossim(b2, b1)) / (self.cossim(b2, a1) + e)
            except:
                print(a1, b1, b2)
                return
            return out

        similarities = sorted(( (cosMul(b2), b2) for b2 in vocab ), reverse=True)

        return similarities[:top_n]

embed = Embeddings()

#%%
embed.cossim("美國", "中國")

#%%
embed.analogy("陳水扁", "呂秀蓮", "馬英九", top_n=10)