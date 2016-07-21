#############################################
#Folder X:\HomeDirs\Documents\KPI Tests\Test#
#
#execfile('import_resources.py')
#############################################


import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

from dateutil.parser import parse



#load parent child relationship file
with open('import_edges.txt','rb') as inf:
	next(inf, '')
	G=nx.read_edgelist(inf,delimiter='\t',nodetype=str,encoding="utf-8")


#Convert undirected graph to directed graph
DI = nx.DiGraph(G)


#Converter directed graph to tree structure with NND as root
tree = nx.bfs_tree(DI,'NND')

#creates graph to look to see how data connected
pos = nx.spring_layout(tree)
nx.draw(G,pos)

plt.show()

#import KPI file
data= pd.read_csv('T-1 Data Export (AM).csv')

#Delete a column by label name
data = data.drop(['wbs_id','status_code','delete_record_flag'],1)

#remove the first row of data
data = data.drop(data.index[[0]])

#format the date time to be %Y%b%d:%H:%M:%S.%f
data = data.apply(lambda x: pd.to_datetime(x, errors='ignore'))

#enter the current start of interval
report_month = raw_input("Please enter the report month of the analysis (ex. 6/1/2016): ")

#parse the date the user entered and save to variable
report_month = parse(report_month)

#Save a variable intervals to analyze how many months to analyze
periods = raw_input("Please enter a number for the number of monthly reporting periods to analyze: ")

periods = int(periods)

p = pd.Period(report_month, freq='M')

start_periods = p - periods

finish_periods = p + periods

rng = pd.period_range(start_periods, finish_periods, freq='M')