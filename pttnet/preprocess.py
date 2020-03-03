import os
import json
import re
from datetime import datetime

def load_comments_data_from_corpus(boards=["Gossiping"], years=[2009]):
    
    posts = []

    for board in boards:
        for year in years:
            fp = f"data/corpus/segmented/{board}/{year}/"

            for post_name in os.listdir(fp):
                post_path = fp + post_name

                with open(post_path) as f:
                    data = json.load(f)
                    title = titleProcess(data['post_title'])

                    posts.append({
                        'title': title['title'],
                        'isRe': title['isRe'],
                        'tag': title['tag'],
                        'id': post_name,
                        'board': board,
                        'date': datetime.fromtimestamp(int(data['post_time'])).strftime("%Y-%m-%d"),
                        'author': data['post_author'],
                        'comments': data["comments"],
                        'content': data["post_body"],
                    })

    return posts


def titleProcess(title: str):
    m = re.match('(^Re: ?)?(\[(.+)\] ?)?(.*)', title)
    try:
        out = {
            'title': m[4],
            'isRe': 0 if m[1] is None else 1,
            'tag': m[3]
        }
    except:
        raise Exception("RegEx parse error")
    return out


def segment(str):
    #return jieba.cut(str)
    return [str]

#%%
if __name__ == "__main__":
    
    import json
    with open("data/Gossiping/2010/20100103_2339_M.1262533140.A.CFA.json") as f:
        data = json.load(f)