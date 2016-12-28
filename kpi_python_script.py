#############################################
#Folder X:\HomeDirs\Documents\KPI Tests\Test#
#
#execfile('kpi_python_script.py')
#############################################



import matplotlib.pyplot as plt
plt.rcdefaults()
import pandas as pd
import numpy as np

from dateutil.parser import parse

import networkx as nx
from collections import defaultdict, deque
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>'])
__all__ = ['bfs_edges']

###################################################################################
def bfs_edges(G, source, reverse=True):
	
	if reverse and isinstance(G, nx.DiGraph):
		neighbors = G.predecessors_iter
	else:
		neighbors = G.neighbors_iter
	
	visited = set([source])
	queue = deque([(source, neighbors(source))])
	while queue:
		parent, children = queue[0]
		try:
			child = next(children)
			if child not in visited:
				yield parent, child
				visited.add(child)
				queue.append((child, neighbors(child)))
		except StopIteration:
			queue.popleft()

#########################################################################
#A simple recursive algorithm. It assumes there is at most a single parent.
#If something doesn't have a parent, it's the root. Otherwise, it returns the root of its parent.
#http://stackoverflow.com/questions/36488758/networkx-find-root-node-for-a-particular-node-in-a-directed-graph

def find_root(G,node):
    if G.predecessors(node):  #True if there is a predecessor, False otherwise
        root = find_root(G,G.predecessors(node)[0])
		
    else:
        root = node
    return root

	
#load parent child relationship file
with open('import_edges.txt','rb') as inf:
	next(inf, '')
	G=nx.read_edgelist(inf,delimiter='\t',nodetype=str,encoding="utf-8")


#Convert undirected graph to directed graph
DI = nx.DiGraph(G)

#find the root node. Use root[0] to call string. 
#root = [n for n,d in DI.in_degree().items() if d==0]
root = 'NND'

#Converter directed graph to tree structure with NND as root
tree = nx.bfs_tree(DI,root)
 

#creat a list of leaf nodes. A leaf node has no child. 
#leafs = [x for x in tree.nodes_iter() if tree.out_degree(x)==0 and tree.in_degree(x)==1]

#creates graph to look to see how data connected
#pos = nx.spring_layout(tree)

nx.draw(tree)

plt.show()

#import KPI file
data= pd.read_csv('T-1 Data Export (P6 Data).csv', sep='\t', header=None)

#Delete a column by label name if not using the report
#data = data.drop(['wbs_id','status_code','delete_record_flag'],1)

#take the first row and make it the column header
data.columns = data.iloc[0]

#remove the first row of data
data = data.drop(data.index[[0]])

#format the date time to be %Y%b%d:%H:%M:%S.%f
data = data.apply(lambda x: pd.to_datetime(x, errors='ignore'))

#Split the Primary Resource column into resource id and resource name. This necessary to connect the key of the tree to the P6 data.
rsrc_id = data['Primary Resource'].str.split('.').str[0]
rsrc_name = data['Primary Resource'].str.split('.').str[1]

#Drop the primary resource column
data.drop('Primary Resource', axis=1, inplace=True)

#Add the new resource id and resource name columns
data['rsrc_id'] = rsrc_id
data['rsrc_name'] = rsrc_name

#enter the current start of interval
report_month = raw_input("Please enter the report month of the analysis (ex. 6/1/2016): ")

#parse the date the user entered and save to variable
report_month = parse(report_month)

#Save a variable intervals to analyze how many months to analyze
periods = raw_input("Please enter number of monthly reporting periods to analyze (ex. T-1 = 1 or T-4 = 4: ")

periods = int(periods)

p = pd.Period(report_month, freq='M')

start_periods = p - periods

finish_periods = p + periods

rng = pd.period_range(start_periods, finish_periods, freq='M')

rng = rng.to_timestamp()

#create a list of time periods depending on number of periods ex. [4,3,2,1,0,-1,-2,-3,-4]
time_periods = list(range((-(len(rng)-1)/2),(len(rng)+1)/2))

time_periods = time_periods[::-1]

T = pd.Series(rng, index=time_periods)

#filter data to categorize start or finish type of change
if periods == 1:
	no_change_start = (data['T+1 Start (BL1)'] >= T[1]) & (data['T+1 Start (BL1)'] < T[0]) & (data['T-0 Start (BL0)'] >= T[1]) & (data['T-0 Start (BL0)'] < T[0])
	no_change_finish = (data['T+1 Finish (BL1)'] >= T[1]) & (data['T+1 Finish (BL1)'] < T[0]) & (data['T-0 Finish (BL0)'] >= T[1]) & (data['T-0 Finish (BL0)'] < T[0])
	
	moved_out_start = ((data['T+1 Start (BL1)'] >= T[1]) & (data['T+1 Start (BL1)'] < T[0]) & (data['T-0 Start (BL0)'] >= T[0])) | ((data['T+1 Start (BL1)'] >= T[1]) & (data['T+1 Start (BL1)'] < T[0]) & (data['T-0 Start (BL0)'] < T[1]))
	moved_out_finish = ((data['T+1 Finish (BL1)'] >= T[1]) & (data['T+1 Finish (BL1)'] < T[0]) & (data['T-0 Finish (BL0)'] >= T[0])) | ((data['T+1 Finish (BL1)'] >= T[1]) & (data['T+1 Finish (BL1)'] < T[0]) & (data['T-0 Finish (BL0)'] < T[1]))
	
	moved_into_start = (data['T-0 Start (BL0)'] >= T[1]) & (data['T-0 Start (BL0)'] < T[0])
	moved_into_finish = (data['T-0 Finish (BL0)'] >= T[1]) & (data['T-0 Finish (BL0)'] < T[0])

	#[i for i, x in enumerate(no_change_start) if x] no_change_start[30060:30070,]
	#Need to not count the "Moved Into" True values if the "No Change" is true
	#use np.where(cond, A, B) or  np.select
	
	########################################
	#Before inverted
	test = pd.concat([data, no_change_start, no_change_finish, moved_out_start,moved_out_finish, moved_into_start,moved_into_finish], axis=1)
	test = test.rename(columns={0 : 'no_change_start',1:'no_change_finish', 2:'moved_out_start',3:'moved_out_finish', 4:'moved_into_start',5: 'moved_into_finish'})
	
	file_name = 'before_inversion.csv'
	test.to_csv(file_name, sep='\t')
	########################################
	
	invert_no_change_start = ~no_change_start
	moved_into_start =  moved_into_start[:] & invert_no_change_start[:]
	
	invert_no_change_finish = ~no_change_finish
	moved_into_finish = moved_into_finish[:] & invert_no_change_finish[:]
	
	#Add the new columns to the original data frame
	df = pd.concat([data, no_change_start, no_change_finish, moved_out_start,moved_out_finish, moved_into_start,moved_into_finish], axis=1)
	
	#Add column names to added columns
	df = df.rename(columns={0 : 'no_change_start',1:'no_change_finish', 2:'moved_out_start',3:'moved_out_finish', 4:'moved_into_start',5: 'moved_into_finish'})
	
	#Export the true false table to csv to check accuracy
	file_name = 't_f_table.csv'
	df.to_csv(file_name, sep='\t')
	
	#group the information by rsrc_id column
	grouped = df.groupby(['rsrc_id'])
	
	#sum up all the true values in the grouped table
	grouped = grouped.sum()
	
	#export the grouped data frame to a csv called
	file_name = 'grouped.csv'
	grouped.to_csv(file_name, sep='\t', encoding='utf-8')
	
	#grab the column names and save to list
	col_names = list(grouped.columns.values)

	#Iterate through tree graph
	for n in nx.nodes_iter(tree):

		#Use iteration value to lookup index in dataframe
		try:
			rsrc = grouped.loc[n]
			#Loop through the column names and values to assign them to node
				
			for i in range(len(col_names)):
				my_value = rsrc[i] or 0.0
				tree.node[n][col_names[i]] = my_value
					
		except KeyError:
			for i in range(len(col_names)):
				tree.node[n][col_names[i]] = 0.0
			
	test_tree = tree
	
	sorted_tree = nx.topological_sort(test_tree, reverse=True)
	
	#raise SystemExit(0)
	
	i = 0
	while i < (len(sorted_tree)-1):
		y = sorted_tree[i]
		parent = test_tree.predecessors(y)
		
		for j in range(len(col_names)):
			child_value = test_tree.node[y][col_names[j]]
			parent_value = test_tree.node[parent[0]][col_names[j]]
			parent_total = parent_value + child_value
			test_tree.node[parent[0]][col_names[j]] = parent_total
		
		i = i + 1
		
	#create empty graphs
	no_change_start_graph = nx.DiGraph()
	no_change_finish_graph = nx.DiGraph()
	
	moved_out_start_graph = nx.DiGraph()
	moved_out_finish_graph = nx.DiGraph()
	
	moved_into_start_graph = nx.DiGraph()
	moved_into_finish_graph = nx.DiGraph()
	
	#add edges to graphs
	no_change_start_graph.add_edges_from(test_tree.edges())
	no_change_finish_graph.add_edges_from(test_tree.edges())
	moved_out_start_graph.add_edges_from(test_tree.edges())
	moved_out_finish_graph.add_edges_from(test_tree.edges())
	moved_into_start_graph.add_edges_from(test_tree.edges())
	moved_into_finish_graph.add_edges_from(test_tree.edges())
	
	#add weights to graphs
	for u, v, a in no_change_start_graph.edges(data=True):
		weight = test_tree.node[v][col_names[0]]
		no_change_start_graph.edge[u][v]['weight'] = weight
	
	
	
	for u, v, a in no_change_finish_graph.edges(data=True):
		weight = test_tree.node[v][col_names[1]]
		no_change_finish_graph.edge[u][v]['weight'] = weight
	
	
	
	for u, v, a in moved_out_start_graph.edges(data=True):
		weight = test_tree.node[v][col_names[2]]
		moved_out_start_graph.edge[u][v]['weight'] = weight	
		
	
	
	for u, v, a in moved_out_finish_graph.edges(data=True):
		weight = test_tree.node[v][col_names[3]]
		moved_out_finish_graph.edge[u][v]['weight'] = weight
	
	
	
	for u, v, a in moved_into_start_graph.edges(data=True):
		weight = test_tree.node[v][col_names[4]]
		moved_out_finish_graph.edge[u][v]['weight'] = weight
	
	
	
	for u, v, a in moved_into_finish_graph.edges(data=True):
		weight = test_tree.node[v][col_names[5]]
		moved_into_finish_graph.edge[u][v]['weight'] = weight
	

	
		
	

	

	
		
	
		
	
		
