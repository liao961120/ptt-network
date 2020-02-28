#%%
import datetime
import jieba
import json
import networkx as nx

class Graph(nx.Graph):

    def get_node_ids(self):
        return [n.id for n in self.nodes]
    
    def get_node(self, id_):
        for node in self.nodes:
            if node.id == id_:
                return node
        raise Exception("Node not found")


class Node():

    def __init__(self, id_: [str, int]=None, fromJson: str=None):
        if id_ is None and fromJson is None:
            raise Exception("Need either id_ or fromJson")

        if fromJson is not None:
            self.__fromJson(fromJson)
        else:
            self.id = id_
            self.corpus = {}
            self.vocab = {}

    def __repr__(self):
        return f"<Node, node_id: {self.id}>"


    def __fromJson(self, json_str: str):
        node = json.loads(json_str)
        self.id = node['id']
        self.corpus = node['corpus']
        self.vocab = node['vocab']


    def toJson(self):
        return json.dumps({
            "id": self.id,
            "corpus": self.corpus,
            "vocab": self.vocab
        }, ensure_ascii=False)
    

    def add_comment(self, date, content, type="pos"):
        """Add comment to corpus
        
        Parameters
        ----------
        date : str
            Date in yyyy-mm-dd format
        content : str
            Segmented comment string, with space separating each
            word.
        type : str
            Comment type. One of ``pos``, ``neg``, or ``neu``.
        """

        if self.corpus.get(date) is None:
            self.corpus[date] = []
        
        self.corpus[date].append({
            "type": type,
            "content": content
        })

        '''
        Corpus Structure
        ----------------

        {
            '2019-01-20': [
                {   
                    type: "pos",
                    content: "segmented string"
                },
                {...}
            ],
            '2020-01-20': [...],
            ...
        }
        '''
    

    def getVocab(self, start="1900-01-01", end="2050-12-31", force=False):
        
        if force or self.vocab.get(f"{start}_{end}") is None:

            start_d = datetime.date.fromisoformat(start)
            end_d = datetime.date.fromisoformat(end)

            raw_content = ''
            for k, cmts in self.corpus.items():
                # Get all comments of specific date
                dt = datetime.date.fromisoformat(k)
                if start_d <= dt and dt <= end_d:
                    raw_content += '\n'.join(c['content'] for c in cmts)

            # Renew comment
            self.vocab[f"{start}_{end}"] = list(set(raw_content.split()))
        
        '''
        Vocab Structure
        ---------------

        {
            '1900-01-01_2050-12-31' : ['word1', 'word2', ...],
            ...
        }
        '''
        return self.vocab[f"{start}_{end}"]


