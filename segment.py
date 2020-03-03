import os
import re
import sys
import json
from ckiptagger import data_utils, construct_dictionary, WS
#os.environ["CUDA_VISIBLE_DEVICES"] = "0"              # running on server
#ws = WS("../ckiptagger/data", disable_cuda=False)     # running on server
ws = WS("../ckiptagger/data")                        # testing on local


def main():
    import logging
    from time import time
    start0 = time()
    logging.basicConfig(filename=f'{sys.argv[0][:-3]}_{sys.argv[1]}_{sys.argv[2]}.log', filemode='w', format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S', level=logging.DEBUG)
    logging.info(f"Start segmenting: {sys.argv[1]} {sys.argv[2]}")
    
    BOARD = sys.argv[1]
    YEARS = [y for y in sys.argv[2].split(',')]
    corp_path = "data/corpus/"
    out_path = "data/corpus/segmented/"

    # Check command line arguments
    if BOARD not in os.listdir("data/corpus/"): 
        raise Exception(f"{BOARD} doesn't exist!" )
    if not os.path.exists(os.path.join(out_path, BOARD)):
        os.mkdir(os.path.join(out_path, BOARD))
    for y in YEARS:
        years = os.listdir(f"data/corpus/{BOARD}")
        if y not in years:
            raise Exception(f"data/corpus/{BOARD}/{y} doesn't exist!") 

    # Set up segmenter
    user_dict = load_word_list()  # Load custom recommend dict
    
    for year in YEARS:
        start = time()
        total_post_num = 0

        year_folder_outpath = os.path.join(out_path, BOARD, str(year))
        if not os.path.exists(year_folder_outpath):
            os.mkdir(year_folder_outpath)

        # Segment posts in a year
        year_folder_inpath = os.path.join(corp_path, BOARD, str(year))
        for j, post in enumerate(os.listdir(year_folder_inpath)):

            # Load a new post from json
            with open(os.path.join(year_folder_inpath, post)) as f:
                data = json.load(f)
        
            # Segment post body and comments
            data['post_body'] = ckipseg(data['post_body'], user_dict)
            for i, cmt in enumerate(data['comments']):
                data['comments'][i]['content'] = ckipseg(cmt['content'], user_dict)
            
            # Save result to new json
            with open(os.path.join(year_folder_outpath, post), "w") as f:
                json.dump(data, f, ensure_ascii=False)
    
        logging.info(f"Processed {year} ({j+1} posts) in {(time() - start)/60:.2} mins")
        total_post_num += j + 1

    logging.info(f"Finished {total_post_num} posts in {(time() - start0)/60:.2} mins")


def ckipseg(text, user_dict=None):
    global ws
    text = [sent.strip() for sent in text.split('\n') if sent != '']

    # Split sentence
    if user_dict:
        word_sentence_list = ws(text, recommend_dictionary = user_dict)
    else: 
        word_sentence_list = ws(text)

    pat = re.compile('\s+')
    out_str = ''
    sent_num = len(word_sentence_list)
    for i, sent in enumerate(word_sentence_list):
        if len(sent) == 0: continue
        out_str += '\u3000'.join(w for w in sent if w != '' and pat.match(w) is None)

        if i != sent_num - 1:
            out_str += '\n'

    return out_str


def load_word_list(path="data/word_list/all"):
    with open(path) as f:
        user_dict = {line.strip(): 1 for line in f}
    return construct_dictionary(user_dict)



if __name__ == "__main__":
    main()
