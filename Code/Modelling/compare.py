from itertools import chain
import json
from tqdm import tqdm
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import sys
import os

NUM_TOPICS = int(sys.argv[1])
outName = sys.argv[2] if len(sys.argv) > 2 else "out.png"


def cosine_similarity(topic1, topic2):
    list1 = list(topic1.keys())
    list2 = list(topic2.keys())
    allWords = list(set([*list1, *list2]))
    vec1 = []
    vec2 = []
    for word in allWords:
        vec1.append(topic1[word] if word in list1 else 0)
        vec2.append(topic2[word] if word in list2 else 0)
    return np.dot(vec1, vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))


def format_party(party):
    return list(party["topic-words"].values())


def ranked_similarity(topic_distance_matrix):
    if len(topic_distance_matrix) == 0:
        return []
    maxV = topic_distance_matrix[0][0]
    maxR = 0
    maxC = 0
    for r in range(len(topic_distance_matrix)):
        for c in range(len(topic_distance_matrix[0])):
            value = topic_distance_matrix[r][c]
            if value > maxV:
                maxV = value
                maxR = r
                maxC = c
    tdp_next = np.delete(topic_distance_matrix, maxR, 0)
    tdp_next = np.delete(tdp_next, maxC, 1)
    return [maxV, *ranked_similarity(tdp_next)]


# party = [[w1,w2,w3....], [w1,w2,w3....], ....]

# party is the topic-words_list
def model_simlarity(party1, party2):
    topic_distance = [[cosine_similarity(
        party1_topic, party2_topic) for party2_topic in party2] for party1_topic in party1]
    ranked_sim = ranked_similarity(np.array(topic_distance))
    return sum(ranked_sim)


def diff_table(party_models):
    parties = party_models.keys()
    return [[model_simlarity(party_models[party1], party_models[party2])
             for party2 in parties] for party1 in tqdm(parties, desc="Calculating diff table")]


def plot_graph(data_table, parties):
    df = pd.DataFrame(data_table, columns=parties, index=parties)

    # Round to two digits to print nicely
    vals = np.around(df.values, 2)

    flattened = list(set(list(chain(*df.values.tolist()))))
    flattened.remove(NUM_TOPICS)
    minVal = min(flattened)
    maxVal = max(flattened)
    normal = df.applymap(lambda x: (x - minVal) / (maxVal - minVal))
    # Normalize data to [0, 1] range for color mapping below
    # normal = (df - minVal) / (maxVal - minVal)
    fig = plt.figure(figsize=[100, 100])
    ax = fig.add_subplot(111)
    ax.axis('off')
    the_table = ax.table(cellText=vals,
                         rowLabels=[f"   {i}   " for i in df.index],
                         colLabels=df.columns,
                         loc='center',
                         cellColours=plt.cm.YlOrBr(normal),
                         cellLoc='center'
                         )
    the_table.scale(1, 9)
    the_table.set_fontsize(40)
    for i in range(len(parties)):
        the_table[(i+1, i)].set_facecolor("#454545")
    # for cell in the_table._cells:
    #    if cell[0] == 0:
    #        the_table._cells[cell].get_text().set_rotation(90)
    fig.savefig(outName)


def output_text_table(data_table, parties):
    parties = [party.replace("_", "\_") for party in parties]
    lines = []
    lines.append("\\begin{table}")
    lines.append("\\begin{tabular}{" + "c"*(len(data_table)+1) + "}")
    lines.append("&".join([" ", *parties]) + "\\\\")
    for i, line in enumerate(data_table):
        lines.append("&".join([parties[i], *[str(round(value, 3))
                                             for value in line]]) + "\\\\")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    with open("table.tex", "w") as f:
        f.writelines([line + "\n" for line in lines])


def normalize_section(table, s1, e1, s2, e2):
    # s1 < e1 <= s2 < e2
    table = np.array(table)
    table1 = table[s1:e1, s1:e1]
    table2 = table[s2:e2, s2:e2]
    diagCells = e1-s1 + e2-s2
    sumTotal = np.sum(table1) + np.sum(table2) - NUM_TOPICS*diagCells
    cellNum = table1.size + table2.size - diagCells
    avg1 = sumTotal / cellNum
    table3 = table[s1:e1, s2:e2]
    table4 = table[s2:e2, s1:e1]
    avg2 = np.sum(table3)/table3.size
    diff = abs(avg1-avg2)
    table3 += diff
    table4 += diff
    #print(avg1, avg2, diff)
    return table.tolist()


def normalize_table(table, keys):
    leg_nums = [int(party[:party.index("_")]) for party in keys]
    ranges = [leg_nums.index(x) for x in [1, 12, 17]]
    ranges.append(len(keys))
    ranges = [[ranges[i], ranges[i+1]] for i in range(len(ranges)-1)]
    for i in range(len(ranges)-1):
        for j in range(i+1, len(ranges)):
            table = normalize_section(table, *ranges[i], *ranges[j])
    return table


with open("lda_results.json") as f:
    data = json.load(f)
    data = {party: format_party(data[party]) for party in data.keys()}

tokenized_parties = {}
for leg_num in [1, 12, 17, 18]:
    with open(f"./parties_tokenized_{leg_num}.json") as f:
        tp = json.load(f)
    for key in tp:
        tokenized_parties[f"{leg_num}_{key}"] = tp[key]

for party in tokenized_parties:
    tokenized_parties[party] = list(chain(*tokenized_parties[party].values()))

for party in tokenized_parties:
    if len(tokenized_parties[party]) < 500:
        del(data[party])


comparison = diff_table(data)
comparison = normalize_table(comparison, data.keys())

parties = [party if len(party) <= 5 else party[:5] for party in data.keys()]


print("Plotting graph")
plot_graph(comparison, parties)
print(
    f"The final table has been plotted. You can find in in {os.getcwd()}/{outName}")
#output_text_table(comparison, parties)
