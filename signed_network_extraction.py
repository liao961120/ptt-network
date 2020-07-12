# Usage: python3 signed_network_extraction.py <board_name> <year1,year2,...>
import os
import sys
import json
import pickle
import logging
from time import time
from pttnet import preprocess


BOARD = sys.argv[1]   # 'Gossiping'
YEARS = [y for y in sys.argv[2].split(',')]   # ['2015']
BASE_DIR = 'data/corpus/'
OUTPUT_EDGE_DATA = f"data/signed_network/edges_{'.'.join(YEARS)}_{BOARD}.jsonl"
OUTPUT_NODE_DATA = f"data/signed_network/nodes_{'.'.join(YEARS)}_{BOARD}.pkl"


# Configure logging
logging.basicConfig(filename=f'{sys.argv[0][:-3]}_{".".join(YEARS)}_{BOARD}.log', filemode='w', format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S', level=logging.DEBUG)
logging.info(f"Start executing...")
start0 = time()  # Time execution


# Read post data
posts = preprocess.load_comments_data_from_corpus(boards=[BOARD], years=YEARS, basedir=BASE_DIR)
#post_num = len(posts)

#%% Extract network

# Clean up
if os.path.exists(OUTPUT_EDGE_DATA): 
    os.remove(OUTPUT_EDGE_DATA)
if os.path.exists(OUTPUT_NODE_DATA): 
    os.remove(OUTPUT_NODE_DATA)


logging.info(f"Start indexing authors...")
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


start = time()
logging.info(f"     Finished indexing authors in {time() - start0} secs.")
logging.info(f"Start extracting networks...")

#-------------- Extract network --------------#
edges = []
for post in posts:

    # Check author exist
    if post['author'] not in authors: continue

    for cmt in post['comments']:

        # Check author exist
        if cmt['author'] not in authors: continue
        # Avoid self loops
        if cmt['author'] == post['author']: continue

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



logging.info(f"     Finished extracting network in {time() - start} secs.")
logging.info(f"Total execution time: {time() - start0} secs.")