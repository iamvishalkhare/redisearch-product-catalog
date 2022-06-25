from typing import List, Union

from models import Customer
from pydantic import ValidationError


class CustomerManager:

    def register_customer(self, register_client_payload: dict) -> Union[str, tuple]:
        customer = Customer.find(
            Customer.email == register_client_payload.get('email')
        ).all()
        if len(customer) > 0:
            return "A customer with email: {} already exist".format(register_client_payload.get('email')), 400
        try:
            new_client = Customer(**register_client_payload)
            new_client.save()
            return new_client.pk
        except ValidationError as e:
            print(e)
            return "Bad request.", 400

    def get_customer_details(self, token) -> Union[List, tuple]:
        customer = Customer.find(
            Customer.pk == token
        ).all()
        if customer:
            return customer
        return "No customer with token: {} found".format(token), 404
