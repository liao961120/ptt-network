# Usage: python3 comment2nodes.py <board_name> <year1,year2,...>

import os
import sys
import itertools
import json
import pickle
import logging
from time import time
from pttnet import preprocess
from pttnet import graph

logging.basicConfig(filename=f'{sys.argv[0][:-3]}.log', filemode='w', format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S', level=logging.DEBUG)
start0 = time()  # Time execution

# Parse command line arguments
BOARD = sys.argv[1]
YEARS = [y for y in sys.argv[2].split(',')]
OUT_DIR = 'data/network/nodes'

# Check command line arguments
if BOARD not in os.listdir("data/corpus/"): 
    raise Exception(f"{BOARD} doesn't exist!" )
for y in YEARS:
    years = os.listdir(f"data/corpus/{BOARD}")
    if y not in years:
        raise Exception(f"data/corpus/{BOARD}/{y} doesn't exist!") 


# Read post data
posts = preprocess.load_comments_data_from_corpus(boards=[BOARD], years=YEARS)
post_num = len(posts)

logging.info(f"Start processing posts. Executed {time() - start0} secs")
start = time()  # Time execution

# Construct network data from post comments
all_nodes = {}
cmt_count = 0
for i, post in enumerate(posts):

    # Get nodes in a post
    for cmt in post['comments']:
        cmt_count += 1

        # Create new node
        if cmt['author'] not in all_nodes.keys():
            all_nodes[cmt['author']] = graph.Node(id_=cmt['author'])

        # Add comments
        comment = {
            'date': post['date'],
            'board': post['board'],
            'content': '\u3000'.join(preprocess.segment(cmt['content'])),
            'type_': cmt['type']
        }
        all_nodes[cmt['author']].add_comment(**comment)
    
    # Show progress / save nodes to disk
    if i % int(post_num/20) == 0 or i == post_num - 1: 
        logging.info(f"Progressed: {(i+1)/post_num:.2%}")
        
        # Write node data to disk
        for id_, node in all_nodes.items():
            node._saveNode(dir_=OUT_DIR)
        
        # Clean up (release memory)
        del all_nodes
        all_nodes = {}


logging.info(f"Processed {cmt_count} comments ({post_num} posts) in {(time() - start)/60:.2} mins")

logging.info(f"Finished in {(time() - start0)/60:.2} mins")