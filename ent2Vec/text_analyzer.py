import os, nltk, string
import numpy as np
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

w2vglove_dir = os.environ["MMKG_DATA_PATH"] + "/word2vec"

class Tokenizer:
    def tokenizer(self, t):
        wordnet_lemmatizer = WordNetLemmatizer()
        tokens = nltk.word_tokenize(t.lower())
        filtered = [w for w in tokens\
                    if w not in stopwords.words("english")\
                    and w not in string.punctuation]
        tagged = [word[0] for word in nltk.pos_tag(filtered)]
        lemma = [wordnet_lemmatizer.lemmatize(tag) for tag in tagged]
        return lemma


def read_glove(fname):
    W = {}
    with open(fname) as f:
        content = f.readlines()
        for c in content:
            l = c.split()
            W[l[0]] = l[1:]
    f.close()
    return W


def get_t2v_vector(titles):
    # title to vector
    f_glove = os.path.join(w2vglove_dir, "glove.6B.50d.txt")
    W = read_glove(f_glove)
    vectors = []
    T = Tokenizer()
    for t in titles:
        v = np.zeros(50) # number of dim
        words = []
        l = T.tokenizer(t)
        for w in l:
            if w in W:
                words.append(w)
                np.add(v, np.array(W[w], dtype='float64'), out=v)
        vectors.append(v)
    return vectors
