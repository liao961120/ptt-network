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
YEARS = [int(y) for y in sys.argv[2].split(',')]

# Check command line arguments
if BOARD not in os.listdir("data/corpus/"): 
    raise Exception(f"{BOARD} doesn't exist!" )
for y in YEARS:
    years = os.listdir(f"data/corpus/{BOARD}")
    if y not in years:
        raise Exception(f"data/corpus/{BOARD}/{y} doesn't exist!") 

# Read post data
posts = preprocess.load_comments_data_from_corpus(boards=[BOARD], years=YEARS)
post_num = len(post)

logging.info(f"Start processing posts. Executed {time() - start0} secs")
start = time()  # Time execution

# Construct network data from post comments
cmt_count = 0
for post in posts:

    # Determine outfile from post year
    year = post['date'][:4]
    OUT_FILE = f'data/network/{BOARD}_{year}_edges.jsonl'

    with open(OUT_FILE, "a") as f:

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
            f.write(json.dumps(edge, ensure_ascii=False))
            f.write('\n')
    
    # Show progress
    if i % int(post_num/20) == 0: logging.info(f"Progressed: {i/post_num:.2%}")


logging.info(f"Processed {cmt_count} comments ({post_count} posts) in {(time() - start)/60:.2} mins")
logging.info(f"Finished in {(time() - start0)/60:.2} mins")