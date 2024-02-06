# class Item:
#     def calculate_total_price(self, x ,y):
#         return x * y

# item1 = Item()
# item1.name = "Phone"
# item1.price = 100
# item1.quantity = 5
# print(item1.calculate_total_price(item1.price, item1.quantity))

class Dog:
    def __init__(self, dogBreed="German Sheep", dogEyeColor="Brown"):
        self.breed = dogBreed
        self.eyeColor = dogEyeColor

tomita = Dog()
print("This dog is a ", tomita.breed, tomita.eyeColor)
