import json
import requests


class Dataloader:

    def dataloader(self):
        # Add more customers by adding name of customer to this list.
        # Then add file {customer_name}.json to directory data/customer_data &
        # file sku_{customer_name}.json to directory data/sku_data
        customers = ["tata1mg", "paytm", "cred"]
        for customer in customers:
            with open('./data/customer_data/{}.json'.format(customer), encoding='utf-8') as f:
                customer_data = json.loads(f.read())
                customer_response = requests.post('http://127.0.0.1:5000/customer/register', json=customer_data)
                with open('./data/sku_data/sku_{}.json'.format(customer), encoding='utf-8') as g:
                    sku_data = json.loads(g.read())
                    payload = {
                        'token': customer_response.json().get('token'),
                        'skus': sku_data
                    }
                    response = requests.post('http://127.0.0.1:5000/skus/ingest', json=payload)
                    print(response.text)

