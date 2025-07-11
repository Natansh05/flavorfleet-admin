class FoodItem:
    def __init__(self, id, name, price, category_id):
        self.id = id
        self.name = name
        self.price = price
        self.category_id = category_id

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            price=data.get("price"),
            category_id=data.get("category_id"),
        )
