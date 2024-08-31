from bs4 import BeautifulSoup
import requests
import pandas as pd
import json


# Function to extract Product Title
def get_title(soup):
    try:
        return soup.find("span", attrs={"id": 'productTitle'}).text.strip()
    except AttributeError:
        return ""


# Function to extract Product Price
def get_price(soup):
    try:
        price = soup.find("span", attrs={'id': 'priceblock_ourprice'}).text.strip()
    except AttributeError:
        try:
            price = soup.find("span", attrs={'id': 'priceblock_dealprice'}).text.strip()
        except AttributeError:
            try:
                price = soup.find("span", attrs={'class': 'a-price-whole'}).text.strip()
            except AttributeError:
                price = ""
    return price


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


# Function to extract Product Brand
def get_brand(soup):
    try:
        return soup.find("a", attrs={'id': 'bylineInfo'}).text.strip()
    except AttributeError:
        return ""


# Function to extract Brand Store Link
def get_brand_store_link(soup):
    try:
        return soup.find("a", attrs={'id': 'bylineInfo'})['href']
    except (AttributeError, TypeError):
        return ""


# Function to extract Product Category
def get_category(soup):
    try:
        return soup.find("a", attrs={'class': 'a-link-normal a-color-tertiary'}).text.strip()
    except AttributeError:
        return ""


# Function to extract and clean Product Specifications/Details
def get_product_details(soup):
    try:
        details = {}
        table = soup.find("table", attrs={"id": "productDetails_techSpec_section_1"})
        if not table:
            table = soup.find("table", attrs={"id": "productDetails_detailBullets_sections1"})
        for row in table.find_all("tr"):
            key = row.find("th").text.strip().replace('\u200e', '')
            value = row.find("td").text.strip().replace('\u200e', '')
            details[key] = value
        return details
    except AttributeError:
        return {}


# Function to extract "About this item" section
def get_about_this_item(soup):
    try:
        about_section = soup.find("div", attrs={"id": "feature-bullets"}).find_all("span",
                                                                                   attrs={"class": "a-list-item"})
        about_text = "\n".join([item.text.strip() for item in about_section])
        return about_text
    except AttributeError:
        return ""


if __name__ == '__main__':
    URL = input("Enter the Amazon product page URL: ")

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

    title = get_title(soup)
    price = get_price(soup)
    rating = get_rating(soup)
    reviews = get_review_count(soup)
    availability = get_availability(soup)
    brand = get_brand(soup)
    category = get_category(soup)
    product_details = get_product_details(soup)
    about_item = get_about_this_item(soup)
    brand_store_link = get_brand_store_link(soup)

    # Constructing the full URL for the brand store link
    if brand_store_link and not brand_store_link.startswith("https://"):
        brand_store_link = "https://www.amazon.in" + brand_store_link

    # Printing the output
    print(f"Title: {title}")
    print(f"Price: {price}")
    print(f"Rating: {rating}")
    print(f"Reviews: {reviews}")
    print(f"Availability: {availability}")
    print(f"Brand: {brand}")
    print(f"Brand Store Link: {brand_store_link}")
    print(f"Category: {category}")
    print(f"Product Details: {product_details}")
    print(f"About This Item: {about_item}")

    # Storing data in a dictionary
    product_data = {
        "title": title,
        "price": price,
        "rating": rating,
        "reviews": reviews,
        "availability": availability,
        "brand": brand,
        "brand_store_link": brand_store_link,
        "category": category,
        "details": product_details,
        "about_item": about_item,
        "link": URL
    }

    # Converting dictionary to DataFrame for CSV output
    amazon_df = pd.DataFrame([product_data])

    # Saving DataFrame to CSV
    amazon_df.to_csv("amazon_product_data.csv", header=True, index=False)

    # Saving dictionary to JSON
    with open("amazon_product_data.json", "w") as json_file:
        json.dump(product_data, json_file, indent=4)

    print("Data has been successfully saved to amazon_product_data.csv and amazon_product_data.json")
