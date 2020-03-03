import os
import re
import jieba_zh_TW as jieba
import sys
import json


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
    jieba.load_userdict("data/word_list/all")

    total_post_num = 0    
    for year in YEARS:
        start = time()

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
            data['post_body'] = segment(data['post_body'])
            for i, cmt in enumerate(data['comments']):
                data['comments'][i]['content'] = segment(cmt['content'])
            
            # Save result to new json
            with open(os.path.join(year_folder_outpath, post), "w") as f:
                json.dump(data, f, ensure_ascii=False)
    
        logging.info(f"Processed {year} ({j+1} posts) in {(time() - start)/60:3.2f} mins")
        total_post_num += j + 1

    logging.info(f"Finished {total_post_num} posts in {(time() - start0)/60:3.2f} mins")


def segment(text):
    text = [jieba.cut(sent.strip()) for sent in text.split('\n') if sent != '']

    pat = re.compile('\s+')
    out_str = ''
    sent_num = len(text)
    for i, sent in enumerate(text):
        out_str += '\u3000'.join(w for w in sent if w != '' and pat.match(w) is None)

        if i != sent_num - 1:
            out_str += '\n'

    return out_str



if __name__ == "__main__":
    main()
