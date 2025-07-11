class AddOn:
    def __init__(self, id, food_id, name, price):
        self.id = id
        self.food_id = food_id
        self.name = name
        self.price = price

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            food_id = data.get("food_id"),
            price=data.get("price", 0.0),
            name = data.get("name", "")
        )
