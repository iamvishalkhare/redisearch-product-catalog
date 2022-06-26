# Redis OM Python for Redisearch using Flask

A starter application for performing Redisearch operations with Redis OM Python ([GitHub](https://github.com/redis/redis-om-python), [Blog Post](https://redis.com/blog/introducing-redis-om-for-python/)), [Redis Stack](https://redis.io/docs/stack/) and the [Flask](https://flask.palletsprojects.com/) microframework.

## Overview

This is an application where customers/clients can register themselves to obtain a token and then using that token they can ingest their product catalog. They will then have some search APIs exposed to search through their product catalog records.
It is like a very basic version of [Algolia](https://algolia.com) if you familiar with it.
Idea is to basically demonstrated some critical Redisearch functionality using [redis-om](https://github.com/redis/redis-om-python)


This application deals with 2 entities/models-
1. `Customer` model, with the following JSON representation:

```json
{
    "name": "Name of the customer/company who wants to index their product catalog with us.",
    "description": "Description of customer/company",
    "email": "email of customer/company",
    "client_tags": ["tag1", "tag2", "tagN"]
}
```

2. `Skus` model, with the following JSON representation:
```json
[
  {
    "company": "name of company",
    "description": "description of sku",
    "image_url": "image url of sku",
    "price": {
      "currency": "currency",
      "discounted_price": "discounted price of sku (int)",
      "mrp": "MRP (Maximum retail price) of sku (int)"
    },
    "ratings": "Ratings of sku out of 5 (float)",
    "sku_id": "Sku ID of sku (int)",
    "sku_url": "sku url",
    "tags": [
      "tag1",
      "tag2",
      "tagN"
    ],
    "title": "Title/Name of sku"
  }
]
```


We'll let Redis OM handle generation of unique IDs, which it does using [ULIDs](https://github.com/ulid/spec).  Redis OM will also handle creation of unique Redis key names for us, as well as saving and retrieving entities from JSON documents stored in a Redis Stack database.

## Getting Started

Let's go...

### Requirements

To run this application you'll need:

* [git](https://git-scm.com/download) - to clone the repo to your machine. 
* [Python 3.7 or higher](https://www.python.org/downloads/).
* A [Redis Stack](https://redis.io) database, or Redis with the [RediSearch](https://redisearch.io) and [RedisJSON](https://redisjson.io) modules installed. You can also [sign up for a free 30Mb database with Redis Enterprise Cloud](https://redis.com/try-free/) - be sure to check the Redis Stack option when creating your cloud database.
* [curl](https://curl.se/), or [Postman](https://www.postman.com/) - to send HTTP requests to the application.  We'll provide examples using curl in this document.
* Optional: [RedisInsight](https://redis.com/redis-enterprise/redis-insight/), a free data visualization and database management tool for Redis.  When downloading RedisInsight, be sure to select version 2.x or use the version that comes with Redis Stack.

### Get the Source Code

Clone the repository from GitHub:

```bash
$ https://github.com/iamvishalkhare/redisearch-product-catalog.git
$ cd redisearch-product-catalog
```

### Start a Redis Stack Database, or Configure your Redis Enterprise Cloud Credentials

Next, we'll get a Redis Stack database up and running. You can setup your own redis cluster with Redisearch and RedisJSON modules installed
or if you're using Redis Enterprise Cloud, you'll need the hostname, port number, and password for your database.  Use these to set the `REDIS_OM_URL` environment variable like this:

```bash
$ export REDIS_OM_URL=redis://default:<password>@<host>:<port>
```

For example if your Redis Enterprise Cloud database is at port `9139` on host `enterprise.redis.com` and your password is `5uper53cret` then you'd set `REDIS_OM_URL` as follows:

```bash
$ export REDIS_OM_URL=redis://default:5uper53cret@enterprise.redis.com:9139
```

### Create a Python Virtual Environment and Install the Dependencies

Create a Python virtual environment, and install the project dependencies.

```bash
$ python3 -m venv venv
$ . ./venv/bin/activate
$ pip install -r requirements.txt
```

### Start the Flask Application

Let's start the Flask application in development mode, so that Flask will restart the server for you each time you save code changes in `app.py`:

```bash
$ export FLASK_ENV=development
$ flask run
```

If all goes well, you should see output similar to this:

```bash
$ flask run
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: XXX-XXX-XXX
```

You're now up and running, and ready to perform CRUD operations on data with Redis, RediSearch, RedisJSON and Redis OM for Python!  To make sure the server's running, point your browser at `http://127.0.0.1:5000/`, where you can expect to see the application's basic home page:

![screenshot](screenshots/homepage.png)

### Load the Sample Data

We've provided a small amount of sample data.
Customer data is in `data/customer_data` and sku (stock keeping unit) data is in `data/sku_data` 
There is an endpoint available to load this data in to redis. Use it like this-
```bash
curl --location --request POST 'http://127.0.0.1:5000/dataloader'
```

### Problems?
If you've set the `REDIS_OM_URL` environment variable, and the code errors with something like this on startup:

```python
raise ConnectionError(self._error_message(e))
redis.exceptions.ConnectionError: Error 8 connecting to enterprise.redis.com:9139. nodename nor servname provided, or not known.
```

then you'll need to check that you used the correct hostname, port, password and format when setting `REDIS_OM_URL`.

If the dataloader endpoint fails to post the sample data into the application, make sure that the Flask application is running **before** running the data loader.

## Understanding & Manipulating data

Let's create and manipulate some instances of our data models in Redis.  Here we'll look at how to call the Flask API with curl (you could also use Postman), how the code works, and how the data's stored in Redis.

### Building Customer & Skus Models with Redis OM

Redis OM allows us to model entities using Python classes. Our customer model is contained in the file `models/customer.py`.  Here's some notes about how it works:

* We declare a class `Customer` which extends a Redis OM class `JsonModel`.  This tells Redis OM that we want to store these entities in Redis as JSON documents.
* We then declare each field in our model, specifying the data type and whether or not we want to index on that field. Following is how `Customer` class looks like. `Optional` keyword tells Redis that this field can be non existent in some or all records.

```python
class Customer(JsonModel):
    name: str = Field(index=True)
    description: Optional[str] = Field(index=False)
    email: str = Field(index=True)
    client_tags: List[str] = Field(index=True)
```

Our Skus model is contained in the file `models/Skus.py`.  Here's some notes about how it works:

* We declare a class `Skus` which also have a nested object called `price`
* `Price` works differently from the other fields. Note that in our JSON representation of the model, price is an object rather than a string or numerical field. With Redis OM, this is modeled as another class, which extends the Redis OM `EmbeddedJsonModel` class.
* `EmbeddedJsonModel` can only be used within a class which extends `JsonModel`. Suppose class Skus extended `HashModel` instead of `JsonModel` then you couldn't have use `EmbeddedJsonModel` with it.
```python
class SkuPrice(EmbeddedJsonModel):
    currency: str
    discounted_price: int = Field(index=True)
    mrp: int = Field(index=True)


class Skus(JsonModel):
    company: str = Field(index=True)
    description: Optional[str] = Field(index=True, full_text_search=True)
    image_url: Optional[str] = Field(index=False)
    price: SkuPrice
    ratings: float = Field(index=True)
    sku_id: int = Field(index=True)
    sku_url: str
    tags: List[str] = Field(index=True)
    title: str = Field(index=True, full_text_search=True)
    token: str = Field(index=True)
```

* We can also store `lists` of values as is the case with `tags` field
```python
tags: List[str] = Field(index=True)
```

* For the `title` and `description` fields, we don't want to index on the field's value, as it's a free text sentence rather than a single word or digit. For this, we'll tell Redis OM that we want to be able to perform full text searches on the values:

```python
description: Optional[str] = Field(index=True, full_text_search=True)
title: str = Field(index=True, full_text_search=True)
```
* We store a field `token` with each SKU record. This token uniquely identifies the customer SKU record belong to.
```python
token: str = Field(index=True)
```

* We can also set a default value for a field. Let's say `title` should be "Test SKU" unless otherwise specified:

```python
title: str = Field(index=True, default="Test SKU")
```

### Adding New Customers

The function `register_customer` in `managers/customer_manager.py` handles the creation of a new Customer in Redis.  It expects a JSON object that adheres to our Customer model's schema.  The code to then create a new Customer object with that data and save it in Redis is simple:

```python
new_client = Customer(**register_client_payload)
new_client.save()
return new_client.pk
```
This function also ensures no 2 customers have same email ID.

When a new Customer instance is created, Redis OM assigns it a unique ULID primary key, which we can access as `.pk`.  We return that to the caller, so that they know the ID of the object they just created.

Persisting the object to Redis is then simply a matter of calling `.save()` on it.

Try it out... with the server running, add a new Customer using curl:

```bash
curl --location --request POST 'http://127.0.0.1:5000/customer/register' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "TATA 1mg",
    "description": "Stay Healthy with Tata 1mg: Your Favourite Online Pharmacy and Healthcare Platform",
    "email": "info@1mg.com",
    "client_tags": ["medicines", "lab tests", "consultation", "healthcare"]
}'
```

Running the above curl command will return the unique ULID ID assigned to the newly created customer. For example-
```bash
{"token": "01FX8SSSDN7PT9T3N0JZZA758G"}
```

We will now use this token to upload sku data of this customer.

### Adding SKU data
Use the token to upload sku data. Something like this-
```bash
curl --location --request POST 'http://127.0.0.1:5000/skus/ingest' \
--header 'Content-Type: application/json' \
--data-raw '{
    "token": "01G6EBDD2WGGBW16224NGXYPHF",
    "skus": [
  {
    "company": "TATA 1mg",
    "description": "He desires to paint you the dreamiest",
    "image_url": "http://www.rich.info/",
    "price": {
      "currency": "INR",
      "discounted_price": 131,
      "mrp": 433
    },
    "ratings": 4.63,
    "sku_id": 40625,
    "sku_url": "https://fraction.org/want/rem",
    "tags": [
      "gexvn",
      "ryqfe",
      "dfthb"
    ],
    "title": "Zon donfan"
  }
]
}'
```

### Examining the data in Redis

Let's take a look at what we just saved in Redis.  Using RedisInsight or redis-cli, connect to the database and look at the value stored at key `:models.skus.Skus:01G6GPP23TAFG5FJJ8TXG3E64R`.  This is stored as a JSON document in Redis, so if using redis-cli you'll need the following command:

```bash
$ redis-cli
127.0.0.1:6379> json.get :models.skus.Skus:01G6GPP23TAFG5FJJ8TXG3E64R
```

If you're using RedisInsight, the browser will render the key value for you when you click on the key name:

![Data in RedisInsight](screenshots/redisinsight.png)

When storing data as JSON in Redis, we can update and retrieve the whole document, or just parts of it.  For example, to retrieve only the sku's title and first tag, use the following command (RedisInsight users should use the built in redis-cli for this):

```bash
$ redis-cli
127.0.0.1:6379> json.get :models.skus.Skus:01G6GPP23TAFG5FJJ8TXG3E64R $.title $.tags[0]
"{\"$.tags[0]\":[\"gexvn\"],\"$.title\":[\"Zon donfan\"]}"
```

For more information on the JSON Path syntax used to query JSON documents in Redis, see the [RedisJSON documentation](https://oss.redis.com/redisjson/path/).

## Exploring more APIs and redis-om features

### Get customer details
A customer can view their details by passing their unique token as path variable. Something like this-

```bash
curl --location --request GET 'http://127.0.0.1:5000/customer/01G6D7H1W5TF3ZEH7NQ18J7217'
```

Following piece of code searches for `all` customers given a token

```bash
customer = Customer.find(
  Customer.pk == token
).all()
```
### Get SKU details by `sku_id`
A customer can request for a sku record previously ingested given their unique `token` and `sku_id` passed as path variables

```bash
curl --location --request GET 'http://127.0.0.1:5000/skus/01G6D7H1W5TF3ZEH7NQ18J7217/73072'
```
Notice how we `and` a condition where 'token' provided by client has to match what's their in the record. 
This will ensure some degree of security as a customer can view details of only those skus which belong to them.

```bash
skus = Skus.find(
    (Skus.sku_id == sku_id) &
    (Skus.token == token)
).all()
```

### Update SKU's discounted price
A customer can choose to update `discounted_price` field.
This is a PATCH endpoint and request payload should contain unique client `token`, `sku_id` whose `discounted_price` has to be update and new value of discounted_price

```bash
curl --location --request PATCH 'http://127.0.0.1:5000/skus/update_discounted_price' \
--header 'Content-Type: application/json' \
--data-raw '{
    "token": "01G6D7H1W5TF3ZEH7NQ18J7217",
    "sku_id": 67525,
    "discounted_price": 11
}'
```

Notice how we first get the pk (primary key) of record and then set new values.

```bash
    def update_skus_data(self, payload) -> tuple:
        token = payload.get('token')
        customer = Customer.find(
            Customer.pk == token
        ).all()
        if not customer:
            return "Token: {} is invalid".format(token), 401
        skus = Skus.find(
            Skus.sku_id == payload.get('sku_id')
        ).all()
        for sku in skus:
            sku.price.discounted_price = payload.get("discounted_price")
            sku.save()
        return "Updated", 200
```

### Full text search on `title` and `description` fields
Since for `title` and `description` fields `full_text_search=True` was set we can perform full text search against these fields.
Endpoint will accept token as path variable and search term as query parameter.

```bash
curl --location --request GET 'http://127.0.0.1:5000/search/fts/01G6E8X5Q0HYG8RXX0Q3HWVYBS?q=tell'
```
Notice how we used `OR` condition to search in 2 different fields i.e. in `title` and `description`.

```bash
skus = Skus.find(
    ((Skus.title % search_term) |
     (Skus.description % search_term)) &
    (Skus.token == token)
).all()
```

### Range search - Search for records having `discounted_price` value within a range
Customers can search for sku records having `discounted_price` within a range.
Endpoint accepts `token` as path variable and a `min` and `max` value of `discounted_price` as query params.
```bash
curl --location --request GET 'http://127.0.0.1:5000/search/discounted_price_range/01G6E8X5Q0HYG8RXX0Q3HWVYBS?min=50&max=200'
```
We use standard AND `&` operations to perform this action.

```bash
skus = Skus.find(
    (Skus.price.discounted_price >= min_price) &
    (Skus.price.discounted_price <= max_price) &
    (Skus.token == token)
).all()
```

### Slightly complicated range query
Return records either whose rating is more than min_rating or discounted_price is more than max_price.

```bash
curl --location --request GET 'http://127.0.0.1:5000/search/price_or_rating/01G6EBDD2WGGBW16224NGXYPHF?min_rating=4.0&max_price=200'
```
We use OR `|` in combination with AND `&` operation to perform this action.
We can also sort the response based on a field. (`ratings` in this case)

```bash
skus = Skus.find(
    ((Skus.ratings >= min_rating) |
     (Skus.price.discounted_price <= max_price)) &
    (Skus.token == token)
).sort_by("ratings").all()
```

### Search against a list in the record
Returns all records whose tags fields contains any tags passed as query param

```bash
curl --location -g --request GET 'http://127.0.0.1:5000/search/tags/01G6EBDD2WGGBW16224NGXYPHF?tag[]=oeffh&tag[]=soimn'
```
We can pass a list of tags and following piece of code will return all records having these values in their `tags` list

```bash
skus = Skus.find(
    (Skus.tags << tag) &
    (Skus.token == token)
).all()
```
The `<<` operator here is used to indicate "in" or "contains".

### Expire a record
Expires a records given its `sku_id` in ttl seconds
This endpoint accepts `sku_id` to be expired and `ttl_in_sec` (time after which record should expire)

```bash
curl --location --request POST 'http://127.0.0.1:5000/search/expire/01G6EBDD2WGGBW16224NGXYPHF' \
--header 'Content-Type: application/json' \
--data-raw '{
    "sku_id": 87381,
    "ttl_in_sec": 120
}'
```
We use `.expire()` function to expire records

```bash
def expire_sku_by_sku_id(self, token, payload):
    skus_to_expire = Skus.find(
        (Skus.sku_id == payload.get('sku_id')) &
        (Skus.token == token)
    ).all()
    if not skus_to_expire:
        return "No data found", 404
    for sku in skus_to_expire:
        Skus.db().expire(sku.key(), payload.get('ttl_in_sec'))
    return "sku_id={} will expire in {} seconds".format(payload.get('sku_id'), payload.get('ttl_in_sec')), 200
```

Using `redis-cli`, you can check that the sku now has a TTL set with the Redis `expire` command:

```bash
127.0.0.1:6379> ttl :models.skus.Skus:01G6GPP23TAFG5FJJ8TXG3E64R
(integer) 102
```

This shows that Redis will expire the key 102 seconds from now.

You can use the `.db()` function on your model class to get at the underlying redis-py connection whenever you want to run lower level Redis commands.  For more details, see the [redis-py documentation](https://redis-py.readthedocs.io/en/stable/).