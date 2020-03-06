#%%
import datetime
import json
import pickle
import os
import itertools
import networkx as nx
from pttnet.utils import merge_dicts


def Graph(count_edges_in, edge_condition=None, MG=None, years=[], boards=[], node_path="data/network/nodes", edge_path="data/network/edges"):
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
        :py:func:`.MutiGraph`) from memory instead of reading the node and edge files
        from disk (ignoring ``node_path`` and ``edge_path``). By default None.
    node_path : str, optional
        Path to the directory of node files, by default "data/network/nodes". 
        Data passed to :py:func:`.MutiGraph`.
    edge_path : str, optional
        Path to the directory of edge files, by default "data/network/edges". 
        Data passed to :py:func:`.MutiGraph`.
    
    Returns
    -------
    nx.Graph
        Undirected graph with weighted edges.

    Examples
    --------
    First create a ``networkx.MultiGraph`` with :py:func:`.loadMGraph`
    then reduce it to a ``networkx.Graph`` with :py:func:`.Graph`

    >>> conditions = {
    ...     #'nodes': ['node_id1', 'node_id2', 'node_id3', ...]
    ...     'date': set(
    ...             (datetime.date(2010,1,1) + datetime.timedelta(days=x)).isoformat() 
    ...             for x in range(30)  # get 30 days comments starting from 2010-01-01
    ...         ), 
    ...     'opinion': set(['pos-pos', 'pos-neg', 'pos-neu', 'neg-pos', 'neg-neg', 'neg-neu'])
    ... }
    >>> MG = MultiGraph(edge_condition=conditions, boards=['Boy-Girl'] ,years=[2007, 2008, 2009])
    >>> 
    >>> criteria = {
    ...     'opinion': ['pos-pos', 'neg-neg'],
    ... }
    >>> G = Graph(count_edges_in=criteria, MG=MG)  # Further reduce graph

    Alternatively, directly create a ``networkx.Graph`` from reading disk file:

    >>> G = Graph(edge_condition=conditions, count_edges_in=criteria)
    """

    if MG is None:
        MG = MultiGraph(edge_condition, years, boards, node_path, edge_path)

    G = nx.Graph()
    for n1, n2, attr in MG.edges(data=True, keys=False):
        
        # Reduce Graph to only relevent attributes
        skip = False
        for k, v in count_edges_in.items():
            # check node conditions
            if k == 'nodes':
                if sum(1 for n in v if n in {n1.id, n2.id}) == 0: 
                    skip = True
                    break
            # Skip if no specified nodes present in edge
            elif attr[k] not in v:
                skip = True
                break
        if skip: continue

        # use edge weight
        if not G.has_edge(n1, n2):
            G.add_edge(n1, n2, weight=1, corpus=[attr])
        else:
            G[n1][n2]['weight'] += 1
            G[n1][n2]['corpus'].append(attr)
    
    return G


def MultiGraph(edge_condition, years=[y + 2006 for y in range(7)], boards=['Boy-Girl'], node_path="data/network/nodes", edge_path='data/network/edges'):
    """Generate nx.Graph from PTT comment data
    
    Parameters
    ----------
    edge_condition : dict
        See ``edge_condition`` in :py:func:`.Graph`.
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

    # Get edge files' paths
    fps = []
    for board, year in [(b, str(y)) for b in boards for y in years]:
        fp = os.path.join(edge_path, f"{board}_{year}_edges.jsonl")
        if not os.path.exists(fp):
            raise Exception(f"Edge file `{fp}` doesn't exist!")
        fps.append(fp)
    
    # Create nx.Graph
    G = nx.MultiGraph()

    nodes = {}
    for fp in fps:
        # Loop over edges in a file
        with open(fp) as f:

            for line in f:
                ed = json.loads(line)

                # Check conditions
                skip = False
                for k, v in edge_condition.items():
                    # Skip if no specified nodes present in edge
                    if k == 'nodes':
                        if sum(1 for n in v if n in ed['edge']) == 0: 
                            skip = True
                            break
                    
                    # Skip if edge attributes don't matched specified conditions
                    elif ed['attr'][k] not in v:
                        skip = True
                        break
                if skip: continue

                # Load nodes
                for node_id in ed['edge']:
                    if node_id not in nodes:
                        nodes[node_id] = Node(node_id, from_disk=node_path)
                
                # Save valid edge
                G.add_edge(nodes[ed['edge'][0]], nodes[ed['edge'][1]], **ed['attr'])

    return G



class Node():

    def __init__(self, id_: str, from_disk: str=None):
        """Initialize a node object
        
        Parameters
        ----------
        id_ : str
            Node id
        from_disk : str, optional
            Path to the directory of the node file, 
            e.g., ``data/network/nodes``
            by default None
        """

        if from_disk is not None:
            self.__loadNode(id_, from_disk)
        else:
            self.id = id_
            self.corpus = {}
            self.corpus_stats = {}
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


    def __loadNode(self, id_, dir_="data/network/nodes"):
        fp_stats = os.path.join(dir_, id_ + '-stats.json')
        fp_corp = os.path.join(dir_, id_ + '-corp.jsonl')

        # Load node data
        with open(fp_stats) as f:
            node = json.load(f)
        self.id = node['id']
        self.corpus_stats = node['corpus_stats']
        self.vocab = node['vocab']

        # Load corpus
        with open(fp_corp) as f:
            self.corpus = merge_dicts(json.loads(l) for l in f)


    def _saveNode(self, dir_="data/network/nodes"):
        fp_stats = os.path.join(dir_, self.id + '-stats.json')
        fp_corp = os.path.join(dir_, self.id + '-corp.jsonl')

        # Write new file if node file doesn exist
        if not os.path.exists(fp_stats):
            with open(fp_stats, "w") as f:
                json.dump({
                    "id": self.id,
                    "corpus_stats": self.corpus_stats,
                    "vocab": self.vocab
                }, f, ensure_ascii=False)
            
        with open(fp_corp, "a") as f:
            f.write(json.dumps(self.corpus, ensure_ascii=False))
            f.write('\n')


    def cacheStats(self, dir_="data/network/nodes/"):
        fp_stats = os.path.join(dir_, self.id + '-stats.json')

        with open(fp_stats, "w") as f:
            json.dump({
                "id": self.id,
                "corpus_stats": self.corpus_stats,
                "vocab": self.vocab
            }, f, ensure_ascii=False)


    def add_comment(self, date, content, board, src, type_, ord_):
        """Add comment to corpus
        
        Parameters
        ----------
        date : str
            Date in ``yyyy-mm-dd`` format
        content : str
            Segmented comment string, with space separating each
            word.
        board: str
            Board name.
        type_ : str
            Comment type. One of ``pos``, ``neg``, or ``neu``.
        
        Notes
        -----
        Corpus Structure

        .. code-block:: python

            {
              '2019-01-20': [
                {   
                  'type': "pos",
                  'board': "Boy-Girl",
                  'content': "segmented string"
                },
                {...}
              ],
              '2020-01-20': [...],
              ...
            }
        """

        if self.corpus.get(date) is None:
            self.corpus[date] = []
        
        self.corpus[date].append({
            "type": type_,
            "content": content,
            "board": board,
            "ord": ord_,
            "src": src
        })


    def getCorpusStats(self, start="1900-01-01", end="2050-12-31", boards=None, force=False):
        """Get corpus stats and vocabulary in specific time range and boards
        
        Parameters
        ----------
        start : str, optional
            Start date in isoformat, by default "1900-01-01"
        end : str, optional
            End date in isoformat, by default "2050-12-31"
        boards : set, optional
            A set of boards to include, by default None
        force : bool, optional
            Force update cached vocabulary, by default False
        
        Returns
        -------
        dict
            Key-value pairs of statistics and their values in the corpus.
        dict
            Key-value pairs of words with their counts in the corpus.

        Notes
        -----
        Corpus stats structure

        .. code-block:: python
        
            {
              'count-all': 0,
              'count-pos': 0,
              'count-neg': 0,
              'count-neu': 0,
              'chars-all': 0,
              'tokens-all': 0,
              'chars-pos': 0,
              'tokens-pos': 0,
              'chars-neg': 0,
              'tokens-neg': 0,
              'chars-neu': 0,
              'tokens-neu': 0,
            }

        Vocabulary structure

        .. code-block:: python
        
            {
              '1900-01-01_2050-12-31' : {
                  'word1': 1000, 
                  'word2':1030, 
                  ...
               },
              '1900-01-01_2050-12-31_Gossiping-Boy-girl' : {
                  'word1':500, 
                  ...
              },
              ...
            }
        """

        if boards is not None:
            key = f"{start}_{end}_{'-'.join(b for b in boards)}"
        else:
            key = f"{start}_{end}"
        
        # Return cache
        if not force and self.corpus_stats.get(key) is not None:
            return self.corpus_stats[key], self.vocab[key]

        # Corpus stats structure
        stats = {
            'count-all': 0,
            'count-pos': 0,
            'count-neg': 0,
            'count-neu': 0,
            'chars-all': 0,
            'tokens-all': 0,
            'chars-pos': 0,
            'tokens-pos': 0,
            'chars-neg': 0,
            'tokens-neg': 0,
            'chars-neu': 0,
            'tokens-neu': 0,
        }

        # Compute corpus stats
        tokens = []
        for day, corp in self.corpus.items():
            
            # Check date
            start_d = datetime.date.fromisoformat(start)
            end_d = datetime.date.fromisoformat(end)
            day = datetime.date.fromisoformat(day)
            if not (start_d <= day and day <= end_d): continue

            for cmt in corp:
                # Check boards
                if boards is not None:
                    if cmt['board'] in boards: 
                        # Update stats
                        stats['count-' + cmt['type']] += 1
                        stats['chars-' + cmt['type']] += len(''.join(cmt['content'].split()))
                        tks = cmt['content'].replace('\n', '\u3000').split('\u3000')
                        stats['tokens-' + cmt['type']] += len(tks)
                        tokens += tks
                
                # Without boards
                else:
                    # Update stats
                    stats['count-' + cmt['type']] += 1
                    stats['chars-' + cmt['type']] += len(''.join(cmt['content'].split()))
                    tks = cmt['content'].replace('\n', '\u3000').split('\u3000')
                    stats['tokens-' + cmt['type']] += len(tks)
                    tokens += tks
        
        # Get *-all stats
        stats['count-all']  =  stats['count-pos'] +  stats['count-neg'] + stats['count-neu'] 
        stats['chars-all']  =  stats['chars-pos'] +  stats['chars-neg'] + stats['chars-neu'] 
        stats['tokens-all'] = stats['tokens-pos'] + stats['tokens-neg'] + stats['tokens-neu'] 

        # Get all vocabulary
        vocab = {}
        for tk in tokens:
            tk = tk.strip()
            if tk not in vocab:
                vocab[tk] = 1
            else:
                vocab[tk] += 1
        
        # Cache computed results
        self.vocab[key] = vocab
        self.corpus_stats[key] = stats

        return stats, vocab

'''
def load_Nodes(path="data/network/nodes"):
    node_ids = { f[:-11] for f in os.listdir("data/network/nodes") }
    nodes = {
        id_: Node(id_, from_disk=path) for id_ in node_ids
    }
    return nodes
'''

# networkx
# G.add_edge(n1, n2, object=x)

#%%
if __name__ == "__main__":
        
    from time import time

    conditions = {
        #'title': {'她答應了!她答應了!'},
        #'tag': {'心情'}
        'date': set((datetime.date(2010,1,1) + datetime.timedelta(days=x)).isoformat() \
            for x in range(30)),
        #'board': {"Boy-Girl"},
        #'opinion': {'pos-pos', 'pos-neg', 'pos-neu', 'neg-pos', 'neg-neg', 'neg-neu', 'neu-pos', 'neu-neg', 'neu-neu'}
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