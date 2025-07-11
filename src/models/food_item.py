class FoodItem:
    def __init__(self, id, name, description, price, image_url , available, category_id):
        self.id = id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.available = available
        self.price = price
        self.category_id = category_id

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            price=data.get("price"),
            category_id=data.get("category_id"),
            description=data.get("description", ""),
            image_url=data.get("image_url", ""),
            available=data.get("available", True)
        )
