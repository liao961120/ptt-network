#%%

BOARD = 'Gossiping'
YEARS = ['2009', '2010']
BASE_DIR = 'data/corpus/'
OUTPUT_EDGE_DATA = f"data/signed_network/edges_{'.'.join(YEARS)}_{BOARD}.jsonl"
OUTPUT_NODE_DATA = f"data/signed_network/nodes_{'.'.join(YEARS)}_{BOARD}.pkl"

import os
import json
import pickle
from pttnet import preprocess

# Read post data
posts = preprocess.load_comments_data_from_corpus(boards=[BOARD], years=YEARS, basedir=BASE_DIR)
#post_num = len(posts)

#%% Extract network

# Clean up
if os.path.exists(OUTPUT_EDGE_DATA): 
    os.remove(OUTPUT_EDGE_DATA)
if os.path.exists(OUTPUT_NODE_DATA): 
    os.remove(OUTPUT_NODE_DATA)


#------------- Index author ---------------#
# Find all authors
authors = set()
for post in posts:
    for cmt in post['comments']:
        if post['author'] not in authors:
            authors.add(post['author'])
        if cmt['author'] not in authors:
            authors.add(cmt['author'])
if '' in authors:
    authors.remove('')

# Indexing
auth_idx = {auth: i for i, auth in enumerate(authors) }

# Save node data
with open(OUTPUT_NODE_DATA, 'wb') as f:
    pickle.dump(auth_idx, f)


#%%
#-------------- Extract network --------------#
edges = []
for post in posts:

    # Check author exist
    if post['author'] not in authors: continue

    for cmt in post['comments']:

        # Check author exist
        if cmt['author'] not in authors: continue
        
        # Edge data
        data = {
            'edge': (auth_idx[cmt['author']], auth_idx[post['author']]),
            'sign': cmt['type'],
            'date': post['date'],
            'id': (post['id'], cmt['order'])
        }

        # Save edge data
        with open(OUTPUT_EDGE_DATA, 'a') as f:
            f.write(json.dumps(data, ensure_ascii=False))
            f.write('\n')

