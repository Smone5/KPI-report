# Primavera P6 Network Graph / KPI Report

## Problem
The project management team on a nuclear startup was not meeting planned performance in the Key Performance Indicator (KPI) reports. Management wanted to hold departments more accountable by tracking project KPI performance at an organizational resource level. The scheduling department created an Excel spreadsheet to track performance at an organizational level, but it was very complex, prone to human errors, computationally expensive and took a lot of time to produce. Instead of using Excel to perform the analysis, I created VBA and Python scripts to perform the analysis computationally faster and less prone to errors.

## Steps
In order to computationally speed up the analysis and do it more accurately I needed to define what tools I needed to accomplish the task. After a lot of research, I decided to use the following tools:
1.	[Oracle Primavera P6 version 8.3](https://www.oracle.com/applications/primavera/products/project-management.html)
2.	[Microsoft Excel 2010](https://products.office.com/en-us/microsoft-excel-2010)
3.	[Visual Basic for Applications (VBA)](https://en.wikipedia.org/wiki/Visual_Basic_for_Applications)
4.	[Python 2.7](https://www.python.org/)
5.	[Pandas 0.17.1](http://pandas.pydata.org/)
6.	[Numpy](http://pandas.pydata.org/)
7.	[NetworkX](https://networkx.github.io/)

I would use the tools in the following way:
1.	Export relationship data from Oracle Primavera P6
2.	Export node data from Oracle Primavera P6
3.	Use VBA to clean and prepare relationship data for analysis in NetworkX
4.	Use Python Pandas to clean prepare node data for analysis in NetworkX
5.	Combine relationship and node data in NetworkX
6.	Create a customized algorithm that would traverse and calculate the data in NetworkX
7.	Output the results of calculation in Excel for analysis

### Creating Relationship Data
In order to import network graph data correctly into NetworkX, I needed the data in a one-to-one relationship format. Unfortunately, at this time the company did not have any Python software approved for use. So, I needed to go through a slow process of getting the Python software approved by IT in order to complete the project. While I was waiting for Python and NetworkX to be approved by the IT department, I decided to clean and prepare the data from Oracle Primavera P6 using a VBA script. This proved to be little trickier than I thought. When Oracle Primavera P6 outputs the data, it only allows exporting many-to-one relationships between parent nodes and child nodes from the project network. Like the example below:


To import the data into NetworkX the data must be formatted into a one-to-one relationship where each child node has only one parent node:

In order to flatten the data coming from Oracle Primavera P6 Project Scheduling software I needed to make a recursive VBA script that systematically found each child node (project activity) and assigned just one parent node to it. This can be seen in the file [flatten_macro script.txt]( https://github.com/Smone5/P6-Network-Graph/blob/master/flatten_macro%20script.txt). Once the relationship data from Oracle Primavera P6 was flattened, I was able to import the data into NetworkX using a Python script.

### Creating Node Data
The next step was to export node data from the Oracle Primavera P6. If one assumes relationship data are like the roads in a network, node data are like the houses in the network. Relationships get you from one node to the other, but nodes are the destinations and can contain the heart of information. In this case, the node contained dates of activities in the schedule. Using a one-month lag method, each node contained the current start and finish of an activity in the schedule and the previous month’s start and finish date of an activity in the schedule (if you want to be technical, it was early start and early finish dates). I also made sure the nodes contained other data like the activity name, activity id and total float for other analyses. Once the data was exported from Oracle P6 and imported into Python, I used Numpy and Pandas to clean and filter the data appropriately for the NetworkX calculations. This can be seen in the python script [kpi_python_script]( https://github.com/Smone5/KPI-report/blob/master/kpi_python_script.py) starting at line 83 to line 188. This was my first use of Pandas so I probably did not implement the code the most efficient way, but I got it done. 

### Combining Relationship and Node Data
With the relationship data and node data ready, I combined the data using NetworkX. In order to make the network graph work for the algorithm I had to change the graph into a directional, tree-structure graph. At time of these calculations, the Oracle Primavera P6 schedule had over 40,000 activities and at least two to three relationships for each activity. This created a rather larger network for analysis. An image of the Oracle P6 Network graph can be seen below when the data was imported into Gephi for visual analysis (the orange dot represents the first activity in the schedule and large purple dot represents the last activity in the schedule).



### Customized Algorithm
This step proved to be the trickiest to complete. Going into this project I knew absolutely nothing about network graphs or network graph algorithms. I had to teach myself basic concepts by watching YouTube videos and reading books. Ultimately, I had to design an algorithm that started at the bottom of a tree structure branch at leaf nodes and traveled up the tree structure to the root node. Then repeated the process until all leaf nodes were traveled. An example can be seen below:


At each node, the algorithm needed to add a value calculated at the child node to parent node to create summarized value at the parent node all the way to root node. Essentially summarizing data from the bottom of the tree structure to the top of the tree structure. Like below:

I was able to implement a simple solution to this problem using NetworkX and a [topological sort]( https://en.wikipedia.org/wiki/Topological_sorting). First, the algorithm finds all the leaf nodes in the tree structure. Once all the leaf nodes are known, the algorithm does a slightly modified reverse depth-first-search all the way to the root node at the top of the tree structure. Once the algorithm reaches the root node, the process starts over at the next leaf. This cycle is repeated until the algorithm has started at each leaf node and traveled to the root node. The Python implementation can be seen below:

	sorted_tree = nx.topological_sort(test_tree, reverse=True)

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

The full python script to generate the network graph tree structure and calculations can be seen here on GitHub [KPI Report]( https://github.com/Smone5/KPI-report/blob/master/kpi_python_script.py)

At the end of process, I had an Excel spreadsheet with all the calculated KPI results for management at an organizational level. A process that might have taken over week before and prone to human errors, could be done in roughly 10 minutes with no errors assuming the data coming from Oracle Primavera P6 was correct. 


## Overall Experience
I feel like this project was just a test of pure grit. Every solution I had presented itself with a new problem. I got to learn Python, Pandas, NetworkX and Graph Theory which was really fun. I also got to apply the mathematical concept of induction to develop algorithms that would solve the problems like flattening relationships and traveling network graphs. I had to come up with unique solutions for problems I could not Google on Stack Overflow. I also had to really break problems down to their core being in order to understand what the real issue was.  Overall, I am really grateful for this experience.  This experience lead me to Dataquest in order to improve my Data Analysis skills. It was challenging, but rewarding at the same time. 

