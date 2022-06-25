from typing import Union, List

from models import Customer, Skus
from pydantic import ValidationError


class SkusManager:
    def ingest_sku_data(self, sku_data) -> tuple:
        token = sku_data.get('token')
        skus = sku_data.get('skus')
        customer = Customer.find(
            Customer.pk == token
        ).all()
        if not customer:
            return "Token: {} is invalid".format(token), 401
        if len(skus) > 30:
            return "Maximum limit for payload is 30 documents", 400
        for sku in skus:
            sku['token'] = token
            try:
                new_sku = Skus(**sku)
                new_sku.save()
            except ValidationError as e:
                print(e)
                return "Bad request.", 400
        return "All sku data added successfully", 200

    def get_sku_by_sku_id(self, token, sku_id) -> Union[List, tuple]:
        skus = Skus.find(
            (Skus.sku_id == sku_id) &
            (Skus.token == token)
        ).all()
        if skus:
            return skus
        return "No data found", 404

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

    def delete_sku_by_sku_id(self, token, sku_id):
        skus = Skus.find(
            (Skus.company == sku_id) &
            (Skus.token == token)
        ).all()
        if skus:
            for sku in skus:
                sku.delete(sku.pk)
        return "Deleted", 200
