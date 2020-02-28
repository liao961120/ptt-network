#%%
import datetime
import jieba
import json
import pickle
import networkx as nx


def Graph(count_edges_in, edge_condition=None, MG=None, edge_attrs_to_keep=['date', 'opinion'], node_path="all_nodes.pkl", edge_path="all_edges.jsonl"):
    """Generate nx.Graph from PTT comment data
    
    Parameters
    ----------
    edge_condition : dict
        Conditions for filtering edges from edge file. Valid only when
        argument ``MG`` is not None. Specified as a dictionary. Only values 
        in a condition are kept. To keep all values of a condition, just leave out
        the key-value pair from the dictionary. The structure of ``edge_condition`` 
        is as below:

        .. code-block:: python
            
            {
              'date': {'2010-01-01', '2010-01-02', ...},
              'opinion': {'pos-pos', 'pos-neg', 'pos-neu', ...}
            }
        
        Data passed to :py:func:`.loadMGraph`.
    count_edges_in : dict, optional
        Criteria to reduce nx.MultiGraph into nx.Graph. The structure is similar 
        to that of ``edge_condition``. The same edges (having same nodes u, v) with 
        values in a criterion are collapsed into 1 edge (with weight equals count).
        Edges in the MultiGraph not matching the criteria are pruned. Use emty dict
        ``{}`` to collapse all the same edges in the MultiGraph (regardless of criteria).
    MG : nx.MultiGraph, optional
        nx.MultiGraph to start from. If specified, will use the MultiGraph (created from
        :py:func:`.loadMGraph`) from memory instead of reading the node and edge files
        from disk (ignoring ``node_path`` and ``edge_path``). By default None.
    edge_attrs_to_keep : list, optional
        Edge attributes to keep when reading file from disk, by default ['date', 'opinion']. 
        Data passed to :py:func:`.loadMGraph`.
    node_path : str, optional
        File path to node file, by default "all_nodes.pkl". 
        Data passed to :py:func:`.loadMGraph`.
    edge_path : str, optional
        File path to edge file, by default "all_edges.jsonl". 
        Data passed to :py:func:`.loadMGraph`.
    
    Returns
    -------
    nx.Graph
        Undirected graph with weighted edges.

    Examples
    --------
    First create a ``networkx.MultiGraph`` with :py:func:`.loadMGraph`
    then reduce it to a ``networkx.Graph`` with :py:func:`.Graph`

    >>> conditions = {
    ...     'date': set(
    ...             (datetime.date(2010,1,1) + datetime.timedelta(days=x)).isoformat() 
    ...             for x in range(30)  # get 30 days comments starting from 2010-01-01
    ...         ), 
    ...     'opinion': set(['pos-pos', 'pos-neg', 'pos-neu', 'neg-pos', 'neg-neg', 'neg-neu'])
    ... }
    >>> MG = loadMGraph(edge_condition=conditions, node_path="data/all_nodes.pkl", edge_path="data/all_edges.jsonl")
    >>> 
    >>> criteria = {
    ... 'opinion': ['pos-pos', 'neg-neg'],
    ... }
    >>> G = Graph(count_edges_in=criteria, MG=MG)  # Further reduce graph

    Alternatively, directly create a ``networkx.Graph`` from reading disk file:

    >>> G = Graph(edge_condition=conditions, count_edges_in=criteria, node_path="data/all_nodes.pkl", edge_path="data/all_edges.jsonl")
    """

    if MG is None:
        MG = loadMGraph(edge_condition, edge_attrs_to_keep, node_path, edge_path)

    G = nx.Graph()
    for n1, n2, attr in MG.edges(data=True, keys=False):
        
        # Reduce Graph with only relevent attributes
        skip = False
        for k, v in count_edges_in.items():
            if attr[k] not in v:
                skip = True
                break
        if skip: continue

        # use edge weight
        if not G.has_edge(n1, n2):
            G.add_edge(n1, n2, weight=1)
        else:
            G[n1][n2]['weight'] += 1
    
    return G


def loadMGraph(edge_condition, edge_attrs_to_keep=['date', 'opinion'], node_path="all_nodes.pkl", edge_path="all_edges.jsonl"):
    """Generate nx.Graph from PTT comment data
    
    Parameters
    ----------
    edge_condition : dict
        See ``edge_condition`` in :py:func:`.Graph`.
    edge_attrs_to_keep : list, optional
        [description], by default ['date', 'opinion']
    node_path : str, optional
        [description], by default "all_nodes.pkl"
    edge_path : str, optional
        [description], by default "all_edges.jsonl"
    
    Returns
    -------
    nx.MultiGraph
        Undirected graph allowing multiple edges between 
        any pair of nodes.
    """


    # Load nodes
    nodes = load_Nodes(node_path)
    node_ids = nodes.keys()

    # Create nx.Graph
    G = nx.MultiGraph()

    # Loop over edges in file
    with open(edge_path) as f:

        for line in f:
            data = json.loads(line)
            edge = data['edge']
            attr = data['attr']

            skip = False
            # Check nodes present
            for node in edge:
                if node not in node_ids:
                    skip = True
                    break
            if skip: continue
            
            # Check conditions
            for k, v in edge_condition.items():
                if attr[k] not in v:
                    skip = True
                    break
            if skip: continue

            # Keep only relevant attributes
            for a in attr.copy().keys():
                if a not in edge_attrs_to_keep: del attr[a]
            
            # Save valid edge
            G.add_edge(nodes[edge[0]], nodes[edge[1]], **attr)

    return G



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

    def __eq__(self, that):
        return self.id == that.id
        
    def __hash__(self):
        hash_str = ''
        for char in self.id:
            if char.isdigit():
                hash_str += char
            else:
                hash_str += str(ord(char))
        return int('1' + hash_str)


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
    

    def getVocab(self, start="1900-01-01", end="2050-12-31", boards=None, force=False):
        
        if force or self.vocab.get(f"{start}_{end}") is None:

            start_d = datetime.date.fromisoformat(start)
            end_d = datetime.date.fromisoformat(end)

            raw_content = ''
            for k, cmts in self.corpus.items():
                
                # Get all comments of specific date
                dt = datetime.date.fromisoformat(k)
                if start_d <= dt and dt <= end_d:
                    
                    # Get all comments of matching boards
                    if board is not None:
                        raw_content += '\u3000'.join(c['content'] for c in cmts if c['board'] in boards)
                    else:
                        raw_content += '\u3000'.join(c['content'] for c in cmts)

            # Renew comment
            self.vocab[f"{start}_{end}"] = list(set(raw_content.split('\u3000')))
        
        '''
        Vocab Structure
        ---------------

        {
            '1900-01-01_2050-12-31' : ['word1', 'word2', ...],
            ...
        }
        '''
        return self.vocab[f"{start}_{end}"]


def load_Nodes(path):
    with open(path, "rb") as f:
        nodes = pickle.load(f)
    return nodes


# networkx
# G.add_edge(n1, n2, object=x)

#%%
if __name__ == "__main__":
        
    from time import time

    conditions = {
        'date': set((datetime.date(2010,1,1) + datetime.timedelta(days=x)).isoformat() \
            for x in range(30)),
        #'board': set("Gossiping"),
        #'opinion': set(['pos-pos', 'pos-neg', 'pos-neu', 'neg-pos', 'neg-neg', 'neg-neu', 'neu-pos', 'neu-neg', 'neu-neu'])
    }
    count_edges_in = {
        'opinion': ['pos-pos', 'neg-neg'], 
        'date': set((datetime.date(2003,1,1) + datetime.timedelta(days=x)).isoformat() for x in range(20*365))
    }

    s = time()
    MG = loadMGraph(edge_condition=conditions)
    #G = Graph(count_edges_in=count_edges_in, MG=MG)
    end = time() - s
    print(end)

    # Gossiping: start_date=2010-01-01
    # 30d MultiGraph (load  94 secs)         : 1121 nodes; 132,1558 edges
    # 30d Graph (count_edges_in, add 13 secs): 1009 nodes;  10,8758 edges
    # 60d MultiGraph (load 113 secs)         : 1784 nodes; 156,3725 edges
    # 60d Graph (count_edges_in, add 20 secs): 1651 nodes;  26,2826 edges

    #%%
    s = time()
    G = Graph(count_edges_in=count_edges_in, MG=MG)
    print(time() - s)   