NODE_FILE = 'all_nodes.pkl'
EDGE_FILE = 'all_edges.jsonl'

# TODO: Separate nodes and edge processing
import os
import utils
import graph
import itertools
import json
import pickle
from time import time
import logging
logging.basicConfig(filename='test.log', filemode='w', format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S', level=logging.DEBUG)
start0 = time()  # Time execution

# Clean up
if os.path.exists(EDGE_FILE):
    os.remove(EDGE_FILE)

# Read post data
posts = utils.load_comments_data(boards=["Gossiping"], years=[2010])

logging.info(f"Start processing posts. Executed {time() - start0} secs")
start = time()  # Time execution

# Construct network data from post comments
all_nodes = {}
cmt_count = 0
post_count = 0
for post in posts:
    post_count += 1

    # Get nodes in a post
    for cmt in post['comments']:
        cmt_count += 1

        # Create new node
        if cmt['author'] not in all_nodes.keys():
            all_nodes[cmt['author']] = graph.Node(id_=cmt['author'])

        # Add comments
        comment = {
            'date': post['date'],
            'content': ' '.join(utils.segment(cmt['content'])),
            'type': cmt['type']
        }
        all_nodes[cmt['author']].add_comment(**comment)
    
    # Get edges in a post
    for cmt1, cmt2 in itertools.combinations(post['comments'], r=2):
        
        # Avoid self-loops
        if cmt1['author'] == cmt2['author']: continue
        
        edge = {
            'edge': (cmt1['author'], cmt2['author']),
            'attr': {
                'date': post['date'],
                'board': post['board'],
                'connected_by': post['id'],
                'opinion': f"{cmt1['type']}-{cmt2['type']}"
            }
        }
        # Save edge data
        with open(EDGE_FILE, "a") as f:
            f.write(json.dumps(edge, ensure_ascii=False))
            f.write('\n')

logging.info(f"Processed {cmt_count} comments ({post_count} posts) in {(time() - start)/60:.2} mins")

# Save node data
with open(NODE_FILE, "wb") as f:
    pickle.dump(all_nodes, f)

logging.info(f"Finished in {(time() - start0)/60:.2} mins")
