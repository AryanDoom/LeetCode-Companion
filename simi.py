import math
import re

#stop words
STOP = set("the a an and or to of in on for with without by is are be find return given that such as up into from if".split())

def norm(text):
    x = text.lower()
    x = re.sub(r'[^a-z0-9]', ' ', x)
    return x

def tokenize(s):
    res = []
    words = norm(s).split()
    for w in words:
        if w not in STOP:
            res.append(w)
    return res


def dot(a, b):
    ans = 0
    for i in range(len(a)):
        ans = ans + (a[i] * b[i])
    return ans

def mag(a):
    s = 0
    for x in a:
        s = s + (x * x)
    return math.sqrt(s)

def cos_sim(a, b):
    ma = mag(a)
    mb = mag(b)
    if ma == 0:
        return 0
    if mb == 0:
        return 0
    
    return dot(a, b) / (ma * mb)


def make_vocab(items):
    #finding all unique words
    v = {}
    idx = 0
    for item in items:
        #combine title and text
        txt = item["title"] + " " + item.get("content", "")
        words = tokenize(txt)
        for w in words:
            if w not in v:
                v[w] = idx
                idx = idx + 1
    return v

def make_vec(text, vocab):
    #making the zero vector
    vec = [0] * len(vocab)
    words = tokenize(text)
    
    count = {}
    for w in words:
        if w in count:
            count[w] = count[w] + 1
        else:
            count[w] = 1
            
    for w in count:
        if w in vocab:
            i = vocab[w]
            vec[i] = count[w]
            
    return vec

def get_idf(items, vocab):
    n = len(items)
    idf = [0] * len(vocab)
    

    for word in vocab:
        idx = vocab[word]
        c = 0
        for item in items:
            txt = item["title"] + " " + item.get("content", "")
            ws = tokenize(txt)
            if word in ws:
                c = c + 1
        
    
        if c > 0:
            val = math.log(n / c)
            idf[idx] = val
        else:
            idf[idx] = 0
            
    return idf

def mul(a, b):
    res = []
    for i in range(len(a)):
        res.append(a[i] * b[i])
    return res


def build_index(items):
    print("starting index build...")
    vocab = make_vocab(items)
    print("vocab size: " + str(len(vocab)))
    
    idf = get_idf(items, vocab)
    
    vecs = []
    for item in items:
        txt = item["title"] + " " + item.get("content", "")
        freq_vec = make_vec(txt, vocab)
        

        final_vec = mul(freq_vec, idf)
        vecs.append(final_vec)
        
    return {
        "items": items,
        "vocab": vocab,
        "idf": idf,
        "vecs": vecs
    }


def extract_query_features(items, query):
    toks = tokenize(query)
    
    #check for known tags
    all_tags = set()
    for item in items:
        for t in item.get("tags", []):
            all_tags.add(t.lower())
            
    found_tags = []
    for t in all_tags:
        if t in query.lower():
            found_tags.append(t)
            
    return {
        "text": query,
        "tokens": toks,
        "tags": found_tags
    }


def overlap(a, b):
    #simple intersection count
    c = 0
    for x in a:
        x_lower = x.lower()
        for y in b:
            if x_lower == y.lower():
                c = c + 1
    return c

def score(index, feats, top=10):
    candidates = []
    
    items = index["items"]
    vocab = index["vocab"]
    idf = index["idf"] 
    vecs = index["vecs"]
    
    #process query
    q_vec = make_vec(feats["text"], vocab)
    q_tfidf = mul(q_vec, idf)
    
    for i in range(len(items)):
        item = items[i]
        doc_vec = vecs[i]
        
        #get cosine score
        s = cos_sim(q_tfidf, doc_vec)
        
        #tag bonus
        tags = item.get("tags", [])
        common_tags = overlap(tags, feats["tags"])
        
        if common_tags > 0:
            s = s + 0.1 * common_tags #give points for tags
            
        candidates.append({
            "item": item,
            "score": s
        }) 
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top]
