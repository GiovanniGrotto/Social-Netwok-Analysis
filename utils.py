import requests
import re
import ast
import math


def get_unibo_teachers(url, analyzed_name_list):
    response = requests.get(url)
    if response.status_code == 200:
        pattern = re.compile(r'<h2 class="text-secondary">(.*?)</h2>', re.DOTALL)
        matches = re.findall(pattern, response.text)
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")

    teacher_list = ['asperti' if x == 'Andrea Asperti' else x for x in matches]
    teacher_list.remove('Alexis Ghyselen')
    teacher_list_filtered = [name for name in teacher_list if name.lower() not in [n.lower() for n in analyzed_name_list]]

    return teacher_list_filtered


def get_coauthors_to_analyze(df):
    all_coauthors = []
    for index, row in df.iterrows():
        coauthors = ast.literal_eval(row['coauthors']).keys()
        all_coauthors += coauthors

    # Finding names that are not present in the 'name' column of the DataFrame
    all_coauthors = [name.strip().lower() for name in all_coauthors]
    all_coauthors_filtered = [name for name in all_coauthors if all(len(part) > 2 for part in name.split())]
    existing_author = [author_name.lower().strip() for author_name in df['name']]
    names = set(process_names(all_coauthors_filtered, existing_author))

    return list(names)


def process_names(list_a, list_b):
    # Function to split, sort, and filter names
    def process(name_list):
        return [sorted(name.split()) for name in name_list]

    # Process names in lists A and B
    processed_a = process(list_a)
    processed_b = process(list_b)

    # Filter elements in A that are not present in the processed B
    result = [original_name for original_name, processed_name in zip(list_a, processed_a) if processed_name not in processed_b]

    return result
