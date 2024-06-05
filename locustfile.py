import random

import requests
from locust import HttpUser, task, between
from faker import Faker
import json

fake = Faker()


class MyUser(HttpUser):
    wait_time = between(1, 5)  # Wait time between each task execution
    provider_data = None
    product_ids = []
    warehouses = []

    @classmethod
    def fetch_product_ids(cls):
        response = requests.get("http://localhost:3000/products")
        if response.status_code == 200:
            products = response.json()
            cls.product_ids = [product['id'] for product in products]
        else:
            print(f"Failed to fetch products. Status code: {response.status_code}")

    def on_start(self):
        provider_data = {
            "name": fake.first_name(),
            "lastName": fake.last_name(),
            "email": fake.email(),
        }
        response = self.client.post("/client", json=provider_data)
        self.provider_data = response.json()
        if response.status_code == 201:
            print("Provider created successfully")
        try:
            self.provider_data = response.json()
        except json.JSONDecodeError:
            print("Response body is not in valid JSON format")
        else:
            print(f"Failed to create provider: {response.status_code}")

    @task(1)
    def create_warehouse(self):
        warehouse = self.client.post("/warehouse", json={"address": "teke", "providerId": "1"})
        self.warehouses.append(warehouse.json()["id"])


    @task(3)
    def add_product_to_warehouse(self):
        randomWh = random.choice(list(self.warehouses))
        randomProduct = random.choice(list(self.product_ids))
        self.client.post(f"/warehouse/{randomWh}", json={
            "productId": randomProduct,
            "stock": 10
        })