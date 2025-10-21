#!/usr/bin/python
import os, sys
import logging

from urllib.parse import unquote
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from flask import Flask, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_PATH = os.curdir
VECTOR_DIR = os.path.join(BASE_PATH, "vector")
vector_path = os.path.join(VECTOR_DIR, 'products')
model_path = os.path.join(VECTOR_DIR, "models")

products_json = [
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

def create_vectordb():
    if (not os.path.exists(vector_path)):
        logger.info("Creating vector store at %s", vector_path)

        embedding = HuggingFaceEmbeddings(model_name="thenlper/gte-base", cache_folder=model_path)
        vectorstore = FAISS.from_texts(texts=[str(p) for p in products_json], embedding=embedding)
        vectorstore.save_local(vector_path)

def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)

    OPENAI_API_BASE = os.environ["OPENAI_API_BASE"]
    logger.info("Using OpenAI API Base: %s", OPENAI_API_BASE)

    def chat(prompt):
        logger.info("Beginning Chat call")
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
            f" You are an interior designer that works for Online Boutique. You are tasked with providing recommendations to a customer on what they should add to a given room from our catalog.\n"
            f"Here are a list of products that are availablegi: {products_json} Specifically, this is what the customer has asked for, see if you can accommodate it: {prompt} Do your best to pick the most relevant item out of the list of products provided, but if none of them seem relevant, then say that instead of inventing a new product. At the end of the response, add a list of the IDs of the relevant products in the following format for the top 3 results: [<first product ID>], [<second product ID>], [<third product ID>] ")
        logger.info("Final design prompt: ")
        logger.info("%s", design_prompt)
        design_response = llm.invoke(
            design_prompt
        )

        data = {'content': design_response.content}
        return data

    def rag_chat(prompt, image_url):
        logger.info("Beginning RAG call")
        logger.info("Image_URL: " + image_url)
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
                    "text": "You are a professional interior designer, give me a detailed description of the style of the room in this image",
                },
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        )
        response = llm_vision.invoke([message])
        logger.info("Description step:")
        logger.info("%s", response)
        description_response = response.content

        # Step 2 – Similarity search with the description & user prompt
        vector_search_prompt = f""" This is the user's request: {prompt} Find the most relevant items for that prompt, while matching style of the room described here: {description_response} """
        logger.info("%s", vector_search_prompt)

        embedding = HuggingFaceEmbeddings(model_name="thenlper/gte-base")
        vectorstore = FAISS.load_local(vector_path, embedding, allow_dangerous_deserialization=True)
        docs = vectorstore.similarity_search(vector_search_prompt)
        logger.info("Vector search: %s", description_response)
        logger.info("Retrieved documents: %d", len(docs))
        relevant_docs = ""
        for doc in docs:
            doc_details = doc.page_content
            logger.info("Adding relevant document to prompt context: %s", doc_details)
            relevant_docs += str(doc_details) + ", "

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
        logger.info("Final design prompt: ")
        logger.info("%s", design_prompt)
        design_response = llm.invoke(
            design_prompt
        )

        data = {'content': design_response.content}
        return data
    
    @app.route("/", methods=['POST'])
    def talkToGemma():
        logger.info(request.json)
        prompt = request.json['message']
        prompt = unquote(prompt)

        # Check for an image url, call RAG only if found
        image = request.json.get('image', None)
        image_url = None

        if isinstance(image, str):
            image_url = image.strip()
        elif isinstance(image, dict) and "url" in image and isinstance(image["url"], str):
            image_url = image["url"].strip()

        # Ensure image_url is a string or set a default value
        if not isinstance(image_url, str):
            image_url = ""

        if (image_url != ""):
            return rag_chat(prompt, image_url)
        else:
            return chat(prompt)

    return app

if __name__ == "__main__":
    if ("--mkvectorstore" in sys.argv):
        create_vectordb()
        exit()
    app = create_app()
    app.run(host='0.0.0.0', port=8080)
