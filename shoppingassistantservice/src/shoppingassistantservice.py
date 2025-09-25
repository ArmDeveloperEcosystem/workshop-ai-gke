#!/usr/bin/python
#
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from urllib.parse import unquote
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from flask import Flask, request

OPENAI_API_BASE = os.environ["OPENAI_API_BASE"]



def create_app():
    app = Flask(__name__)

    @app.route("/", methods=['POST'])
    def talkToGemma():
        print("Beginning RAG call")
        print("Using OpenAI API Base: " + OPENAI_API_BASE)
        print("Using image: " + request.json['image'])
        prompt = request.json['message']
        prompt = unquote(prompt)

        # Step 1 – Get a room description from Gemma
        llm_vision = ChatOpenAI(
            openai_api_base=OPENAI_API_BASE,
            openai_api_key="no-api-key",
            model="google/gemma-3-4b-it",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,

        )
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "You are a professional interior designer, give me a detailed decsription of the style of the room in this image",
                },
                {"type": "image_url", "image_url": {"url": request.json['image']}},
            ]
        )
        response = llm_vision.invoke([message])
        print("Description step:")
        print(response)
        description_response = response.content

        #Prepare relevant documents for inclusion in final prompt
        relevant_docs = [
            {
                "id": "OLJCESPC7Z",
                "name": "Sunglasses",
                "description": "Add a modern touch to your outfits with these sleek aviator sunglasses.",
                "picture": "/static/img/products/sunglasses.jpg",
                "priceUsd": {
                    "currencyCode": "USD",
                    "units": 19,
                    "nanos": 990000000
                },
                "categories": ["accessories"]
            },
            {
                "id": "66VCHSJNUP",
                "name": "Tank Top",
                "description": "Perfectly cropped cotton tank, with a scooped neckline.",
                "picture": "/static/img/products/tank-top.jpg",
                "priceUsd": {
                    "currencyCode": "USD",
                    "units": 18,
                    "nanos": 990000000
                },
                "categories": ["clothing", "tops"]
            },
            {
                "id": "1YMWWN1N4O",
                "name": "Watch",
                "description": "This gold-tone stainless steel watch will work with most of your outfits.",
                "picture": "/static/img/products/watch.jpg",
                "priceUsd": {
                    "currencyCode": "USD",
                    "units": 109,
                    "nanos": 990000000
                },
                "categories": ["accessories"]
            },
            {
                "id": "L9ECAV7KIM",
                "name": "Loafers",
                "description": "A neat addition to your summer wardrobe.",
                "picture": "/static/img/products/loafers.jpg",
                "priceUsd": {
                    "currencyCode": "USD",
                    "units": 89,
                    "nanos": 990000000
                },
                "categories": ["footwear"]
            },
            {
                "id": "2ZYFJ3GM2N",
                "name": "Hairdryer",
                "description": "This lightweight hairdryer has 3 heat and speed settings. It's perfect for travel.",
                "picture": "/static/img/products/hairdryer.jpg",
                "priceUsd": {
                    "currencyCode": "USD",
                    "units": 24,
                    "nanos": 990000000
                },
                "categories": ["hair", "beauty"]
            },
            {
                "id": "0PUK6V6EV0",
                "name": "Candle Holder",
                "description": "This small but intricate candle holder is an excellent gift.",
                "picture": "/static/img/products/candle-holder.jpg",
                "priceUsd": {
                    "currencyCode": "USD",
                    "units": 18,
                    "nanos": 990000000
                },
                "categories": ["decor", "home"]
            },
            {
                "id": "LS4PSXUNUM",
                "name": "Salt & Pepper Shakers",
                "description": "Add some flavor to your kitchen.",
                "picture": "/static/img/products/salt-and-pepper-shakers.jpg",
                "priceUsd": {
                    "currencyCode": "USD",
                    "units": 18,
                    "nanos": 490000000
                },
                "categories": ["kitchen"]
            },
            {
                "id": "9SIQT8TOJO",
                "name": "Bamboo Glass Jar",
                "description": "This bamboo glass jar can hold 57 oz (1.7 l) and is perfect for any kitchen.",
                "picture": "/static/img/products/bamboo-glass-jar.jpg",
                "priceUsd": {
                    "currencyCode": "USD",
                    "units": 5,
                    "nanos": 490000000
                },
                "categories": ["kitchen"]
            },
            {
                "id": "6E92ZMYYFZ",
                "name": "Mug",
                "description": "A simple mug with a mustard interior.",
                "picture": "/static/img/products/mug.jpg",
                "priceUsd": {
                    "currencyCode": "USD",
                    "units": 8,
                    "nanos": 990000000
                },
                "categories": ["kitchen"]
            }
        ]

        # Step 3 – Tie it all together by augmenting our call to Gemma-3-4b-it with the description and relevant products
        llm = ChatOpenAI(
            openai_api_base=OPENAI_API_BASE,
            openai_api_key="no-api-key",
            model="google/gemma-3-4b-it",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,

        )
        design_prompt = (
            f" You are an interior designer that works for Online Boutique. You are tasked with providing recommendations to a customer on what they should add to a given room from our catalog. This is the description of the room: \n"
            f"{description_response} Here are a list of products that are relevant to it: {relevant_docs} Specifically, this is what the customer has asked for, see if you can accommodate it: {prompt} Start by repeating a brief description of the room's design to the customer, then provide your recommendations. Do your best to pick the most relevant item out of the list of products provided, but if none of them seem relevant, then say that instead of inventing a new product. At the end of the response, add a list of the IDs of the relevant products in the following format for the top 3 results: [<first product ID>], [<second product ID>], [<third product ID>] ")
        print("Final design prompt: ")
        print(design_prompt)
        design_response = llm.invoke(
            design_prompt
        )

        data = {'content': design_response.content}
        return data

    return app

if __name__ == "__main__":
    # Create an instance of flask server when called directly
    app = create_app()
    app.run(host='0.0.0.0', port=8080)
