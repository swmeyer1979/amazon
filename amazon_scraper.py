from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class AmazonScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()
        self.base_url = 'https://www.amazon.com'

    def handle_two_factor_authentication(self):
        # Wait for user to enter two-factor authentication code
        print("Please enter the two-factor authentication code sent to your device.")
        time.sleep(30)  # Wait time for user to enter the code

    def login(self):
        self.driver.get(f"{self.base_url}/gp/sign-in.html")
        self.driver.find_element(By.ID, "ap_email").send_keys(self.username)
        self.driver.find_element(By.ID, "ap_password").send_keys(self.password)
        self.driver.find_element(By.ID, "signInSubmit").click()
        time.sleep(3)  # Wait for page to load
        self.handle_two_factor_authentication()

    def scrape_orders(self):
        self.driver.get(f"{self.base_url}/gp/css/order-history")
        time.sleep(3)  # Wait for page to load
        orders_html = self.driver.page_source
        soup = BeautifulSoup(orders_html, 'html.parser')
        orders = []  # List to hold order data

        for order in soup.find_all('div', class_='order'):
            order_data = self.extract_order_data(order)
            orders.append(order_data)
            self.generate_pdf_receipt(order_data)

        return orders

    def extract_order_data(self, order):
        # Extract data from each order
        # This is a simplified example, add more extraction logic as needed
        order_id = order.find('span', class_='order-id').text
        order_date = order.find('span', class_='order-date').text
        order_total = order.find('span', class_='order-total').text
        return {
            'order_id': order_id,
            'order_date': order_date,
            'order_total': order_total
        }

    def generate_pdf_receipt(self, order_data):
        # Create a PDF receipt for the order
        c = canvas.Canvas(f"receipt_{order_data['order_id']}.pdf", pagesize=letter)
        c.drawString(100, 750, f"Order ID: {order_data['order_id']}")
        c.drawString(100, 730, f"Order Date: {order_data['order_date']}")
        c.drawString(100, 710, f"Order Total: {order_data['order_total']}")
        c.save()

    def scrape_product_listings(self, search_query):
        self.driver.get(f"{self.base_url}/s?k={search_query}")
        time.sleep(3)  # Wait for page to load

        products = []  # List to hold product data
        products_html = self.driver.page_source
        soup = BeautifulSoup(products_html, 'html.parser')

        for product in soup.find_all('div', {'data-component-type': 's-search-result'}):
            product_data = self.extract_product_data(product)
            if product_data:
                products.append(product_data)

        return products

    def extract_product_data(self, product):
        product_data = {}

        # Try extracting each attribute, skip if not found
        title_tag = product.find('span', class_='a-size-medium')
        if title_tag:
            product_data['title'] = title_tag.text.strip()

        price_tag = product.find('span', class_='a-price')
        if price_tag:
            product_data['price'] = price_tag.find('span', class_='a-offscreen').text.strip()

        rating_tag = product.find('span', class_='a-icon-alt')
        if rating_tag:
            product_data['rating'] = rating_tag.text.strip()

        review_count_tag = product.find('span', class_='a-size-base')
        if review_count_tag:
            product_data['review_count'] = review_count_tag.text.strip()

        product_data['category'] = self.extract_product_category(product)


        return product_data if product_data else None

    def extract_product_category(self, product):
        # Extract the category from the product's breadcrumb navigation or other relevant element
        category_tag = product.find('span', class_='a-color-secondary')  # Example class, adjust as needed
        if category_tag:
            category_parts = category_tag.text.strip().split('>')
            if category_parts:
                return category_parts[-1].strip()  # Return last element as category
        return "Unknown"

    def close(self):
        self.driver.close()

# Usage
scraper = AmazonScraper('meyer.samuel@gmail.com', 'Sl@teBlu3!')
scraper.login()
products = scraper.scrape_product_listings('search_query_here')
print(products)
scraper.close()
