#%%
import json
import pickle
import networkx as nx
from os.path import join


def MultiDiGraph(board="Gossiping", years=[2015], data_dir='data/signed_network/', load_node_mapping=False):
    
    # Get file paths
    years = [str(y) for y in years]
    edge_file = join(data_dir , f'edges_{".".join(years)}_{board}.jsonl')
    node_file = join(data_dir, f'nodes_{".".join(years)}_{board}.pkl')

    # Init Graph
    G = nx.MultiDiGraph()

    # Load edges
    with open(edge_file) as f:
        for l in f:
            edge = json.loads(l)
            attr = {
                'sign': sign(edge['sign']),
                'date': edge['date']
            }

            G.add_edge(edge['edge'][0], edge['edge'][1], **attr)


    if load_node_mapping:
        
        # Load nodes
        with open(node_file, 'rb') as f:
            nodes = pickle.load(f)
    
        return G, nodes


    return G


def sign(x):
    if x == 'neu':
        return 0
    elif x == 'pos':
        return 1
    elif x == 'neg':
        return -1
    else:
        raise Exception('Not `pos`, `neg` nor `neu` edge signs.')