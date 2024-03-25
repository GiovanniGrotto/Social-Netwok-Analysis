import pandas as pd
import ast
import numpy as np

# Sample Nodes DataFrame
Nodes_data = {'id': [1,2,3],
              'name': ['Alice', 'Bob', 'Charlie'],
              'coauthors': [{'Bob': 3, 'Charlie': 2}, {'Alice': 5, 'Charlie': 1}, {'Alice': 2, 'Bob': 4}]}

Nodes = pd.DataFrame(Nodes_data)
nodes = pd.read_csv('dbs/db_scrape.csv')
nodes = nodes.dropna(subset=['org', 'data'], how='all')

# If you want to reset the index after dropping rows
nodes = nodes.reset_index(drop=True)
nodes['id'] = nodes.reset_index().index
nodes['Label'] = None
nodes['citations'] = None
nodes['h_index'] = None
nodes['study_field'] = None
nodes['name'] = nodes['name'].apply(lambda x: x.strip().lower())

all_coauthors = []
for index, row in nodes.iterrows():
    coauthors = ast.literal_eval(row['coauthors']).keys()
    all_coauthors += coauthors

# Initialize an empty list to store edges
edges_data = []

# Iterate through each row in Nodes DataFrame
for index, row in nodes.iterrows():
    row_data = ast.literal_eval(row['data'])
    nodes.loc[nodes['name'] == row['name'], 'citations'] = row_data['Citazioni']['All']
    nodes.loc[nodes['name'] == row['name'], 'h_index'] = row_data['Indice H']['All']
    if 'study_field' in row_data:
        nodes.loc[nodes['name'] == row['name'], 'study_field'] = str(row_data['study_field'])
        nodes.loc[nodes['name'] == row['name'], 'Label'] = row['name'] + ' - ' + row['org'] + ' - ' + str(row_data['study_field'])
    else:
        nodes.loc[nodes['name'] == row['name'], 'Label'] = row['name'] + ' - ' + row['org']
    # Get the id and coauthors for the current row
    source_id = row['id']
    coauthors = ast.literal_eval(row['coauthors'])

    # Iterate through each coauthor and create an edge
    for coauthor in coauthors:
        try:
            row_index = nodes.index[nodes['name'] == coauthor.strip().lower()][0] # Get the index of the given name
            coauthor_row = nodes.loc[nodes['id'] == row_index]
            all_nan = coauthor_row['org'].isna().all() and coauthor_row['data'].isna().all() # It means it is one of the author we don't have info about
            if coauthor.strip().lower() == row['name'] or all_nan:
                continue
            # Da errore se il coautore non è presente come nome nel df
            target_id = nodes.loc[nodes['name'] == coauthor.strip().lower(), 'id'].values[0]
            edges_data.append({'Source': source_id, 'Target': target_id, 'Weight': int(coauthors[coauthor]), 'Label': int(coauthors[coauthor])})
        except IndexError:
            continue
        except Exception as e:
            print(e)
            continue

# Create the Edges DataFrame
edges = pd.DataFrame(edges_data)

filtered_nodes = nodes[nodes['id'].isin(edges['Source']) | nodes['id'].isin(edges['Target'])]
filtered_edges = edges[edges['Source'] != edges['Target']]

clean_nodes = filtered_nodes.copy()
for index, row in clean_nodes.iterrows():
    if str(row['profile_url']) != 'nan':
        clean_nodes.loc[clean_nodes['name'] == row['name'], 'url'] = "https://scholar.google.com" + row['profile_url']
    if str(row['url']) != 'nan':
        clean_nodes.loc[clean_nodes['name'] == row['name'], 'url'] = "https://scholar.google.com" + row['url']
clean_nodes.drop(['data', 'coauthors', 'publications', 'missing_publications', 'profile_url'], axis=1, inplace=True)
clean_nodes.loc[clean_nodes['name'] == 'andrea giovanni nuzzolese', 'url'] = "https://scholar.google.com/citations?hl=it&user=5PFmyuIAAAAJ"
clean_nodes.loc[clean_nodes['name'] == 'andrea omicini', 'url'] = "https://scholar.google.com/citations?hl=it&user=cLRxLiwAAAAJ"
clean_nodes.loc[clean_nodes['name'] == 'sasu tarkoma', 'url'] = "https://scholar.google.com/citations?hl=it&user=UTRmf5MAAAAJ"

clean_nodes.to_csv('nodes_finale_clean.csv', index=False)
filtered_edges.to_csv('edges_final.csv', index=False)



