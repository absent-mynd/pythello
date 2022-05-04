import matplotlib.pyplot as plt
import numpy as np
import json
from pythello_stats import PythelloStats 

np.random.seed(10)

#ax.pcolor(np.random.randn((10,10)))
#ax.pcolor(np.random.randn(10), np.random.randn(10))
f = open('data.json')
data = json.load(f)
f.close()
dict = {}
agent_labels = ["RANDOM", "GREEDY_MAJ", "GREEDY_WMAJ", "PMC_3", "ab_3_MAJ", "ab_3_WMAJ", "MCTS_3"]
table_data = []
#for agent in data.keys():
#    agent_labels.append(agent)

#agent_labels.sort()

for agent in agent_labels:
    agent_data = []
    for other_agent in agent_labels:
        agent_data.append(data[agent][other_agent]["winpct"])
    table_data.append(agent_data)
import pandas as pd
 
df = pd.DataFrame(table_data,
                  columns=agent_labels,
                  index=agent_labels
                  )
 
plt.imshow(df, cmap="coolwarm")
plt.colorbar(label='Agent 1 Win Percent')
plt.xticks(range(len(df)),df.columns, rotation=20)
plt.yticks(range(len(df)),df.index)
plt.ylabel('Agent 1')
plt.tick_params(labeltop=True, labelbottom=False, top=True, bottom=False)

plt.show()
