import pandas as pd
from tqdm import tqdm

from utils import get_unibo_teachers, get_coauthors_to_analyze
from scrape_author import get_author_data, recover_missing_publications, recover_study_field_and_url


def main_flow():
    df = pd.read_csv('dbs/db_scrape.csv')

    filtered_names_analyzed = df.loc[df['coauthors'].apply(lambda x: x != '{}'), 'name'].tolist()
    teacher_list = get_unibo_teachers('https://corsi.unibo.it/2cycle/artificial-intelligence/faculty', filtered_names_analyzed)
    #teacher_list = get_coauthors_to_analyze(df)

    for teacher in teacher_list:
        teacher_data = get_author_data(teacher)
        df = df._append(teacher_data, ignore_index=True)
        df.dropna(axis=0, how='all', inplace=True)
        df.to_csv('dbs/db_scrape.csv', index=False)

    df.to_csv('dbs/db_scrape.csv', index=False)


def get_coauthor_main_data():
    df = pd.read_csv('dbs/db_scrape.csv')

    teacher_list = get_coauthors_to_analyze(df)

    for teacher in tqdm(teacher_list):
        teacher_data = get_author_data(teacher, coauthors=False)
        df = df._append(teacher_data, ignore_index=True)
        df.dropna(axis=0, how='all', inplace=True)
        df.to_csv('dbs/db_scrape.csv', index=False)

    df.to_csv('dbs/db_scrape.csv', index=False)


if __name__ == '__main__':
    get_coauthor_main_data()
    