import os
import json
import jieba
from datetime import datetime

def load_comments_data(boards=["Gossiping"], years=[2009]):
    
    posts = []

    for board in boards:
        for year in years:
            fp = f"data/corpus/{board}/{year}/"

            for post_name in os.listdir(fp):
                post_path = fp + post_name

                with open(post_path) as f:
                    data = json.load(f)


                    posts.append({
                        'title': data['post_title'],
                        'id': data['post_id'],
                        'board': board,
                        'date': datetime.fromtimestamp(int(data['post_time'])).strftime("%Y-%m-%d"),
                        'author': data['post_author'],
                        'comments': data["comments"]
                    })

    return posts


def segment(str):
    #return jieba.cut(str)
    return [str]

#%%
if __name__ == "__main__":
    
    import json
    with open("data/Gossiping/2010/20100103_2339_M.1262533140.A.CFA.json") as f:
        data = json.load(f)