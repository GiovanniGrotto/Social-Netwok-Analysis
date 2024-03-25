from url_request import make_request
from bs4 import BeautifulSoup


# Function to extract value for a given field
def extract_value_for_field(soup, field_name):
    field_div = soup.find('div', class_='gsc_oci_field', string=field_name)

    if field_div:
        field_value = field_div.find_next_sibling('div', class_='gsc_oci_value')

        if field_value:
            if field_name == 'Citazioni totali':
                return field_value.find('a').text.split(' ')[-1]

            return field_value.text.strip()

    return None


def extract_publication_data(response):
    soup = BeautifulSoup(response.content, 'html.parser')

    author_list = extract_value_for_field(soup, 'Autori')
    if author_list:
        author_list = author_list.split(',')
    year = extract_value_for_field(soup, 'Data pubblicazione')
    if year:
        year = year.split('/')[0]
    citations = extract_value_for_field(soup, 'Citazioni totali')

    return author_list, year, citations


def get_publication_data(publication_url):
    url = f"https://scholar.google.com{publication_url}"

    response = make_request(url)

    return extract_publication_data(response)
