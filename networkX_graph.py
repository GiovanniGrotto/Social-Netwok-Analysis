import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from networkx.algorithms.community import greedy_modularity_communities, label_propagation_communities

# Assuming you have DataFrames named nodes and edges

# Example DataFrames
nodes = pd.read_csv('nodes_finale_clean.csv')
edges = pd.read_csv('edges_final.csv')


# Create a directed graph from the edges DataFrame
G = nx.from_pandas_edgelist(edges, 'Source', 'Target', ['Weight'], create_using=nx.DiGraph())

# Make the graph undirected
G = G.to_undirected()

# Add nodes with attributes from the nodes DataFrame
node_attributes = nodes.set_index('id').to_dict(orient='index')
nx.set_node_attributes(G, node_attributes)

# 1. Number of nodes and edges
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()

# 2. Degree distribution
degree_sequence = [degree for node, degree in G.degree]
avg_degree = sum(degree_sequence) / num_nodes

# 3. Density of the graph
density = nx.density(G)

# 5. Clustering coefficient
clustering_coefficient = nx.average_clustering(G)

# Display the analysis results
print(f"Number of nodes: {num_nodes}")
print(f"Number of edges: {num_edges}")
print(f"Average degree: {avg_degree}")
print(f"Graph density: {density}")
print(f"Average clustering coefficient: {clustering_coefficient}")

# Measure node properties
degree = dict(G.degree())
closeness = nx.closeness_centrality(G)
betweenness = nx.betweenness_centrality(G)
eigenvector = nx.eigenvector_centrality(G)
pagerank = nx.pagerank(G)


# Print the top 5 nodes for each centrality measure
def print_top_nodes(centrality, centrality_name):
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"Top 5 nodes for {centrality_name}:")
    for node, value in sorted_nodes:
        print(f"  Node {nodes.iloc[node]['name']}: {value}")
    print()


print_top_nodes(degree, "Degree")
print_top_nodes(closeness, "Closeness Centrality")
print_top_nodes(betweenness, "Betweenness Centrality")
print_top_nodes(eigenvector, "Eigenvector Centrality")
print_top_nodes(pagerank, "PageRank")

# Label Propagation
label_propagation_communities = list(label_propagation_communities(G))
print("\nLabel Propagation:")
for i, community in enumerate(label_propagation_communities):
    print(f"Community {i+1}: {community}")
