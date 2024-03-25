from tqdm import tqdm
from bs4 import BeautifulSoup
import ast


from scrape_publication import get_publication_data, extract_publication_data
from url_request import make_request, make_multiple_request


def get_author_page_url(complete_name):
    print(f"Getting url of {complete_name}")
    try:
        url = f"https://scholar.google.com/citations?view_op=search_authors&hl=it&mauthors={complete_name.replace(' ', '+')}&btnG="
    except Exception:
            return None

    response = make_request(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all elements with the specified structure
    elements = soup.find_all('div', class_='gs_ai gs_scl gs_ai_chpr')

    # Iterate through elements to find a match
    for element in elements:
        name_element = element.find('h3', class_='gs_ai_name')
        if name_element:
            full_name = name_element.get_text(strip=True)
            if complete_name.lower() in full_name.lower():
                href_element = element.find('a', class_='gs_ai_pho')
                if href_element:
                    return href_element['href']

    # Return None if no match is found
    return None


def get_author_main_page(author_url):
    print("Getting personal data")
    url = f"https://scholar.google.com{author_url}&cstart=1&pagesize=400&"

    response = make_request(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    name = soup.find('div', {'id': 'gsc_prf_in'}).text.strip()
    try:
        university = soup.find('div', {'class': 'gsc_prf_il'}).find('a').text.strip()
    except Exception:
        university = soup.find('div', class_='gsc_prf_il').text.strip()

    table_element = soup.find('table', {'id': 'gsc_rsb_st'})

    # If the table element is found, extract the data from the table
    if table_element:
        # Find all rows in the table body
        rows = table_element.select('tbody tr')

        # Initialize a dictionary to store the data
        data = {}

        # Loop through rows and extract data
        for row in rows:
            columns = row.find_all('td')
            if columns:
                key = columns[0].text.strip()
                total_value = columns[1].text.strip()
                last_5_years_value = columns[2].text.strip()
                data[key] = {'All': total_value, 'Last5': last_5_years_value}

        study_field_element = soup.find('div', class_='gsc_prf_il', id='gsc_prf_int')

        if study_field_element:
            study_field = [child.text for child in study_field_element.find_all('a')]
            data['study_field'] = study_field

        # Find all elements with the class "gsc_a_at"
        elements = soup.find_all('a', class_='gsc_a_at')

        publications = []
        # Extract and print the href values
        for element in elements:
            href_value = element['href']
            publications.append(href_value)

    return name, university, data, publications


def get_author_coauthors(author_name, publications):
    coauthors_list = []
    for i, pub in tqdm(enumerate(publications), total=len(publications), desc=f"Searching coauthors for {author_name}"):
        try:
            author_list, year, citations = get_publication_data(pub)

        except Exception as e:
            coauthors_dict = {cohautor: coauthors_list.count(cohautor) for cohautor in coauthors_list}
            coauthors_dict.pop(author_name, None)
            return coauthors_dict.keys(), coauthors_dict, publications[i:]  # Return the missing publications
        if author_list:
            coauthors_list += author_list
        coauthors_list = [coauthor.strip() for coauthor in coauthors_list]

    coauthors_dict = {cohautor: coauthors_list.count(cohautor) for cohautor in coauthors_list}
    coauthors_dict.pop(author_name, None)
    return coauthors_dict.keys(), coauthors_dict, []


def get_author_data(complete_name, coauthors=True):
    try:
        url = get_author_page_url(complete_name)
        if not url:
            raise Exception("No author found")
        name, uni, data, publications = get_author_main_page(url)
    except Exception as e:
        print(e)
        return {"name": complete_name, "org": None, "data": None, "coauthors": {}, "publications": None, "missing_publications": None, "profile_url": None}

    if coauthors:
        coauthor_list, coauthor_dict, missing_publications = get_author_coauthors(name, publications)
        return {"name": name, "org": uni, "data": data, "coauthors": coauthor_dict, "publications": publications, "missing_publications": missing_publications, "profile_url": url}
    else:
        return {"name": name, "org": uni, "data": data, "coauthors": {}, "publications": [], "missing_publications": publications, "profile_url": url}


def recover_missing_publications(df, name_list):
    for index, row in df.iterrows():
        if row['name'].lower() not in name_list or row['missing_publications'] == '[]':
            continue
        missing_pubs = row['missing_publications'].replace('[','').replace(']','').replace("'",'').split(',')

        coauthors_list = []
        for pub in tqdm(missing_pubs, desc=f"Getting missing publications of {row['name']}"):
            author_list, year, citations = get_publication_data(pub.strip())
            if author_list:
                coauthors_list += author_list
            coauthors_list = [coauthor.strip() for coauthor in coauthors_list]
        coauthors_dict = {cohautor: coauthors_list.count(cohautor) for cohautor in coauthors_list}
        coauthors_dict.pop(row['name'], None)

        old_dict = ast.literal_eval(row['coauthors'])
        result_dict = {key: old_dict.get(key, 0) + coauthors_dict.get(key, 0) for key in set(old_dict) | set(coauthors_dict)}
        df.loc[df['name'] == row['name'], 'coauthors'] = str(result_dict)
        df.loc[df['name'] == row['name'], 'missing_publications'] = '[]'
        df.to_csv('dbs/db_scrape.csv', index=False)


def recover_study_field_and_url(df, name_list):
    for index, row in df.iterrows():
        old_data = ast.literal_eval(row['data'])
        if row['name'].lower() not in name_list or 'study_field' in old_data.keys():
            continue
        url = get_author_page_url(row['name'])
        df.loc[df['name'] == row['name'], 'url'] = url
        name, uni, data, publications = get_author_main_page(url)
        df.loc[df['name'] == row['name'], 'data'] = str(data)
        df.to_csv('dbs/db_scrape.csv', index=False)