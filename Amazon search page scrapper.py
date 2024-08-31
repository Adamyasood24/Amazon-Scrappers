from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import time
import random

# Function to extract Product Title
def get_title(soup):
    try:
        return soup.find("span", attrs={"id": 'productTitle'}).text.strip()
    except AttributeError:
        return ""

# Function to extract Product Price
def get_price(soup):
    try:
        return soup.find("span", attrs={'id': 'priceblock_ourprice'}).text.strip()
    except AttributeError:
        try:
            return soup.find("span", attrs={'id': 'priceblock_dealprice'}).text.strip()
        except AttributeError:
            return ""

# Function to extract Product Rating
def get_rating(soup):
    try:
        return soup.find("span", attrs={'class': 'a-icon-alt'}).text.strip()
    except AttributeError:
        return ""

# Function to extract Number of User Reviews
def get_review_count(soup):
    try:
        return soup.find("span", attrs={'id': 'acrCustomerReviewText'}).text.strip()
    except AttributeError:
        return ""

# Function to extract Availability Status
def get_availability(soup):
    try:
        return soup.find("div", attrs={'id': 'availability'}).find("span").text.strip()
    except AttributeError:
        return "Not Available"

if __name__ == '__main__':
    URL = input("Enter the Amazon search results URL: ")

    HEADERS = ({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.amazon.in/',
        'DNT': '1',  # Do Not Track Request Header
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
    })

    try:
        webpage = requests.get(URL, headers=HEADERS)
        webpage.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"Error occurred: {e}")

    soup = BeautifulSoup(webpage.content, "html.parser")

    links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})

    links_list = ["https://www.amazon.com" + link.get('href') for link in links]

    d = {"title": [], "price": [], "rating": [], "reviews": [], "availability": [], "link": []}

    for link in links_list:
        try:
            new_webpage = requests.get(link, headers=HEADERS)
            new_webpage.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to retrieve {link}: {err}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            continue

        new_soup = BeautifulSoup(new_webpage.content, "html.parser")

        title = get_title(new_soup)
        price = get_price(new_soup)
        rating = get_rating(new_soup)
        reviews = get_review_count(new_soup)
        availability = get_availability(new_soup)

        print(f"Title: {title}, Price: {price}, Rating: {rating}, Reviews: {reviews}, Availability: {availability}")

        d['title'].append(title)
        d['price'].append(price)
        d['rating'].append(rating)
        d['reviews'].append(reviews)
        d['availability'].append(availability)
        d['link'].append(link)

        time.sleep(random.uniform(1, 3))  # Introduce random delays to mimic human behavior

    amazon_df = pd.DataFrame.from_dict(d)

    amazon_df['title'] = amazon_df['title'].replace('', np.nan)
    amazon_df = amazon_df.dropna(subset=['title'])

    amazon_df.to_csv("amazon_data.csv", header=True, index=False)

    print("Data has been successfully saved to amazon_data.csv")
