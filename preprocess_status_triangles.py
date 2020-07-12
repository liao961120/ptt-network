#%%
import json
import networkx as nx
import datetime


with open("data/signed_network/triangles_2015_HatePolitics.jsonl") as f:

    for line in f:
        data = json.loads(line)

        # Extract triads
        key = list(data.keys())[0]
        triads = tuple(int(i) for i in key.split("_"))

        edge_num_AB = len(data[key]['AB']['drct'])
        edge_num_AX = len(data[key]['AX']['drct'])
        edge_num_BX = len(data[key]['BX']['drct'])

        for i in range(edge_num_AB):
            for j in range(edge_num_AX):
                for k in range(edge_num_BX):

                    # date
                    dt_AB = datetime.date.fromisoformat(data[key]['AB']['date'][i])
                    dt_AX = datetime.date.fromisoformat(data[key]['AX']['date'][j])
                    dt_BX = datetime.date.fromisoformat(data[key]['BX']['date'][k])

                    # AB formed after AX and BX
                    if dt_AB > dt_AX and dt_AB > dt_BX:
                        G = nx.DiGraph()
                        G.add_edge(triads[0], triads[1], sign = data[key]['AB']['sign'], date = dt_AB.isoformat())

                        if data[key]['AX']['drct'][j] == 1:
                            G.add_edge(triads[0], triads[2], sign = data[key]['AX']['sign'], date = dt_AX.isoformat())
                        elif data[key]['AX']['drct'][j] == -1:
                            G.add_edge(triads[2], triads[0], sign = data[key]['AX']['sign'], date = dt_AX.isoformat())
                        else:
                            raise Exception("Unexpected direction in `AX`")

                        if data[key]['BX']['drct'][k] == 1:
                            G.add_edge(triads[1], triads[2], sign = data[key]['BX']['sign'], date = dt_BX.isoformat())
                        elif data[key]['BX']['drct'][k] == -1:
                            G.add_edge(triads[2], triads[1], sign = data[key]['BX']['sign'], date = dt_BX.isoformat())
                        else:
                            raise Exception("Unexpected direction in `BX`")

                        with open("data/signed_network/triangles_2015_HatePolitics_processed.gmll", "a") as f:
                            G_s = ''.join(nx.generate_gml(G))
                            f.write(G_s)
                            f.write('\n')


#H = nx.parse_gml(G_s, destringizer=lambda x: int(x))