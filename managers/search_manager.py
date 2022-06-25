from models import Skus


class SearchManager:
    def search_by_term(self, token, search_term):
        skus = Skus.find(
            ((Skus.title % search_term) |
             (Skus.description % search_term)) &
            (Skus.token == token)
        ).all()
        if skus:
            return skus
        return "No data found", 404

    def search_by_price_range(self, token, min_price, max_price):
        skus = Skus.find(
            (Skus.price.discounted_price >= min_price) &
            (Skus.price.discounted_price <= max_price) &
            (Skus.token == token)
        ).all()
        if skus:
            return skus
        return "No data found", 404

    def search_by_price_lt_or_rating_gt(self, token, min_rating, max_price):
        skus = Skus.find(
            ((Skus.ratings >= min_rating) |
             (Skus.price.discounted_price <= max_price)) &
            (Skus.token == token)
        ).sort_by("ratings").all()
        if skus:
            return skus
        return "No data found", 404

    def search_by_tag(self, token, tag):
        skus = Skus.find(
            (Skus.tags << tag) &
            (Skus.token == token)
        ).all()
        if skus:
            return skus
        return "No data found", 404

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

