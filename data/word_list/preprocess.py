#%%
import csv

# PTT 鄉民百科詞表
selected = []
with open("raw/ptt_wiki.csv") as f:
    for row in csv.DictReader(f, delimiter=','):
        if row['source'] == 'link_new':
            selected.append(row['term'])
with open("ptt_wiki.txt", "w") as f:
    f.writelines(l + '\n' for l in set(selected))


