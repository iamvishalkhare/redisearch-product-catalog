from flask import Flask, request
from redis_om import Migrator
from managers import CustomerManager, SkusManager, SearchManager, Dataloader

app = Flask(__name__)


# Utility function to format list of objects as
# a result dictionary, for easy conversion to JSON in
# API responses.
def build_results(response):
    if isinstance(response, tuple):
        response = {"results": response[0]}
    else:
        result = []
        for customer in response:
            result.append(customer.dict())
        response = {"results": result}
    return response


# Data loader endpoint to load sample data.
@app.route("/dataloader", methods=["POST"])
def dataloader():
    Dataloader().dataloader()
    return "Data ingested. See logs."


# Register a new customer.
@app.route("/customer/register", methods=["POST"])
def register_client():
    result = CustomerManager().register_customer(request.json)
    return {"token": result}


# Get customer details given customer's token
@app.route("/customer/<token>", methods=["GET"])
def get_customer(token):
    result = CustomerManager().get_customer_details(token)
    return build_results(result)


# Ingest customer's SKU data
@app.route("/skus/ingest", methods=["POST"])
def ingest_data():
    result = SkusManager().ingest_sku_data(request.json)
    return build_results(result)


# Get SKU data of a customer.
@app.route("/skus/<token>/<int:sku_id>", methods=["GET"])
def get_sku_by_sku_id(token, sku_id):
    result = SkusManager().get_sku_by_sku_id(token, sku_id)
    return build_results(result)


# Update SKU's discounted price
@app.route("/skus/update_discounted_price", methods=["PATCH"])
def update_sku_data():
    result = SkusManager().update_skus_data(request.json)
    return build_results(result)


# Delete a SKU given customer's token
@app.route("/skus/<token>/<int:sku_id>", methods=["DELETE"])
def delete_sku_by_sku_id(token, sku_id):
    result = SkusManager().delete_sku_by_sku_id(token, sku_id)
    return build_results(result)


# Searches for a search term over fields which are marked True for full text search. (title & description)
@app.route("/search/fts/<token>", methods=["GET"])
def search_by_term(token):
    result = SearchManager().search_by_term(token, request.args.get('q'))
    return build_results(result)


# Return records whose discounted_price is in a given range
@app.route("/search/discounted_price_range/<token>", methods=["GET"])
def search_by_price_range(token):
    result = SearchManager().search_by_price_range(token, request.args.get('min'), request.args.get('max'))
    return build_results(result)


# Return records either whose rating is more than min_rating or discounted_price is more than max_price.
@app.route("/search/price_or_rating/<token>", methods=["GET"])
def search_by_price_lt_or_rating_gt(token):
    result = SearchManager().search_by_price_lt_or_rating_gt(token, request.args.get('min_rating'),
                                                             request.args.get('max_price'))
    return build_results(result)


# Returns all records whose tags fields contains any tags passed as query param
@app.route("/search/tags/<token>", methods=["GET"])
def search_by_tag(token):
    result = SearchManager().search_by_tag(token, request.args.to_dict(flat=False).get('tag[]'))
    return build_results(result)


# Expires a records given its sku_id in ttl seconds
@app.route("/search/expire/<token>", methods=["POST"])
def expire_sku_by_sku_id(token):
    result = SearchManager().expire_sku_by_sku_id(token, request.json)
    return build_results(result)


@app.route("/", methods=["GET"])
def home_page():
    return """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Redis OM Python for Redisearch using Flask</title>
            </head>
            <body>
                <h1>Redis OM Python for Redisearch using Flask</h1>
                <p><a href="https://github.com/iamvishalkhare/redisearch-product-catalog">Read the documentation on GitHub</a>.</p>
            </body>
        </html>
    """


# Create RediSearch indices for instances of the Customer & Skus models.
Migrator().run()
