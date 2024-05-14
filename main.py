import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient


def scrape_quotes():
    base_url = "http://quotes.toscrape.com"
    url = base_url
    quotes_data = []
    authors_data = []

    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = soup.find_all('div', class_='quote')

        for quote in quotes:
            text = quote.find('span', class_='text').get_text()
            author = quote.find('small', class_='author').get_text()
            tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]

            quotes_data.append({
                'author': author,
                'quote': text,
                'tags': tags
            })

            author_info = get_authors_info(quote)
            authors_data.append(author_info)

        next_page = soup.find('li', class_='next')
        if next_page:
            url = base_url + next_page.find('a')['href']
        else:
            break

    return quotes_data, authors_data


def get_authors_info(quote):
    author_name = quote.find('small', class_='author').text
    author_url = quote.find('a')['href']
    author_info_page = requests.get(f'http://quotes.toscrape.com{author_url}')
    author_soup = BeautifulSoup(author_info_page.content, 'html.parser')
    born_date = author_soup.find('span', class_='author-born-date').text.strip()
    born_location = author_soup.find('span', class_='author-born-location').text.strip()
    description = author_soup.find('div', class_='author-description').text.strip()
    return {
        "fullname": author_name,
        "born_date": born_date,
        "born_location": born_location,
        "description": description
    }


def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# change URL if using a different MongoDB server
def import_to_mongodb():
    client = MongoClient('mongodb+srv://vitst:P1q2w3e4r@cluster0.0uj64vn.mongodb.net/')
    db = client['authors_database']

    with open('authors.json', 'r', encoding='utf-8') as file:
        authors_data = json.load(file)

    with open('quotes.json', 'r', encoding='utf-8') as file:
        quotes_data = json.load(file)

    db['authors'].insert_many(authors_data)
    db['quotes'].insert_many(quotes_data)
    print("Data imported successfully to MongoDB!")


if __name__ == "__main__":
    quotes, authors = scrape_quotes()
    save_to_json(quotes, 'quotes.json')
    save_to_json(authors, 'authors.json')
    import_to_mongodb()
