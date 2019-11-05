## coding: utf-8
'''
This python file is used to tranfer the words in corpus to vector, and save the word2vec model under the path 'w2v_model'.
'''

from gensim.models.word2vec import Word2Vec
import pickle
import os
import gc

'''
DirofCorpus class
-----------------------------
This class is used to make a generator to produce sentence for word2vec training

# Arguments
    dirname: The src of corpus files 
    
'''

class DirofCorpus(object):
    def __init__(self, dirname):
        self.dirname = dirname
    
    def __iter__(self):
        for d in self.dirname:
            for fn in os.listdir(d):
                print(fn)
                for filename in os.listdir(os.path.join(d, fn)):
                    samples = pickle.load(open(os.path.join(d, fn, filename), 'rb'))[0]
                    for sample in samples:
                        yield sample
                    del samples
                    gc.collect()

'''
generate_w2vmodel function
-----------------------------
This function is used to learning vectors from corpus, and save the model

# Arguments
    decTokenFlawPath: String type, the src of corpus file 
    w2vModelPath: String type, the src of model file 
    
'''

def generate_w2vModel(decTokenFlawPath, w2vModelPath):
    print("training...")
    model = Word2Vec(sentences= DirofCorpus(decTokenFlawPath), size=30, alpha=0.01, window=5, min_count=0, max_vocab_size=None, sample=0.001, seed=1, workers=1, min_alpha=0.0001, sg=1, hs=0, negative=10, iter=5)
    model.save(w2vModelPath)

def evaluate_w2vModel(w2vModelPath):
    print("\nevaluating...")
    model = Word2Vec.load(w2vModelPath)
    for sign in ['(', '+', '-', '*', 'main']:
        print(sign, ":")
        print(model.most_similar_cosmul(positive=[sign], topn=10))
    
def main():
    dec_tokenFlaw_path = ['./data/cdg_ddg/corpus/']
    w2v_model_path = "./w2v_model/wordmodel3" 
    generate_w2vModel(dec_tokenFlaw_path, w2v_model_path)
    evaluate_w2vModel(w2v_model_path)
    print("success!")
 
if __name__ == "__main__":
    main()


