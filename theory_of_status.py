#%%
import os
import sys
import json
import logging
from time import time
from pttnet.signed_network.graph import MultiDiGraph


BOARD = 'Boy-Girl'
YEARS = ['2015']
TRIANGLES_OUTPUT_FILE = f'data/signed_network/triangles_{".".join(YEARS)}_{BOARD}.jsonl'

if os.path.exists(TRIANGLES_OUTPUT_FILE):
    os.remove(TRIANGLES_OUTPUT_FILE)


logging.basicConfig(filename=f'{sys.argv[0][:-3]}.log', filemode='w', format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S', level=logging.DEBUG)
start0 = time()  # Time execution
logging.info("Start execution...")


# Load Graph data
G = MultiDiGraph(board=BOARD, years=YEARS)


def neighbors(G, node):
    
    t = [(k, 'to') for k in G.successors(node)]
    f = [(k, 'from') for k in G.predecessors(node)]

    return t + f

#%%
#triangles = {}
triangles = []

#for A in list(G.nodes)[:100]:
for A in G.nodes:
    for B in G.successors(A):
        for X, type2 in neighbors(G, B):

            # Checking
            if X == A: continue
            AX = G.has_edge(A, X)
            XA = G.has_edge(X, A)
            if (not AX) and (not XA): continue

            c_type = {
                "AB": {
                    'drct': [],       # 1: A to B, only 1 is possible
                    'sign': [],       # 1: pos, 0: neu, -1: neg
                    'date': []
                },
                "AX": {
                    'drct': [],       # 1: A to X, -1: X to A
                    'sign': [],       # 1: pos, 0: neu, -1: neg
                    'date': []
                },
                "BX": {
                    'drct': [],       # 1: B to X, -1: X to B
                    'sign': [],       # 1: pos, 0: neu, -1: neg
                    'date': []
                }
            }

            # Direction: A to X
            if AX:
                edge_data = G.get_edge_data(A, X)
                for num, attr in edge_data.items():
                    c_type["AX"]['sign'].append(attr['sign'])
                    c_type["AX"]['date'].append(attr['date'])
                    c_type["AX"]['drct'].append(1)
            
            # Direction: X to A
            if XA:
                edge_data = G.get_edge_data(X, A)
                for num, attr in edge_data.items():
                    c_type["AX"]['sign'].append(attr['sign'])
                    c_type["AX"]['date'].append(attr['date'])
                    c_type["AX"]['drct'].append(-1)

            # Direction: B to X
            if G.has_edge(B, X):
                edge_data = G.get_edge_data(B, X)
                for num, attr in edge_data.items():
                    c_type["BX"]['sign'].append(attr['sign'])
                    c_type["BX"]['date'].append(attr['date'])
                    c_type["BX"]['drct'].append(1)

            # Direction: X to B
            if G.has_edge(X, B):
                edge_data = G.get_edge_data(X, B)
                for num, attr in edge_data.items():
                    c_type["BX"]['sign'].append(attr['sign'])
                    c_type["BX"]['date'].append(attr['date'])
                    c_type["BX"]['drct'].append(-1)
            
            # Direction: A to B
            edge_data = G.get_edge_data(A, B)
            for num, attr in edge_data.items():
                c_type["AB"]['sign'].append(attr['sign'])
                c_type["AB"]['date'].append(attr['date'])
                c_type["AB"]['drct'].append(1)
        

            with open(TRIANGLES_OUTPUT_FILE, "a") as f:
                f.write(json.dumps({f'{A}_{B}_{X}': c_type}))
                f.write('\n')
                #triangles.append(f"{A}_{B}_{X}")
                #triangles[(A, B, X)] = c_type


#%%
#with open("triangles_ids.txt", "w") as f:
#    out = '\n'.join(triangles)
#    f.write(out)


logging.info(f"Finished in {time() - start0} secs")


#%%
"""
import pickle
with open("triangles_Gossiping_2015.pkl", "wb") as f:
   pickle.dump(triangles, f)


#%%

import networkx as nx

G1 = nx.MultiDiGraph() # or MultiDiGraph
G1.add_edge(0, 1, k='a', weight=7)
G1.add_edge(0, 1, k='b', weight=7)
G1.add_edge(0, 1, k='bb', weight=7)
G1.add_edge(0, 2, k='c', weight=7)
G1.add_edge(2, 0, k='d', weight=7)

#%%

#G1.number_of_edges(0, 1)    
attr = G1.get_edge_data(0, 1)

for num, attr in attr.items():
    print(num, attr['weight'])

#%%
#import itertools
#len(list(itertools.combinations(G.nodes, r=3)))

"""