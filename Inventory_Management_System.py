import json
from abc import ABC, abstractmethod
from datetime import datetime

#------------ Custom Exception ------------
class InsufficentStockError(Exception):
    pass

class DuplicateProductError(Exception):
    pass

class InvalidProductDataError(Exception):
    pass

#------------ Abstract Base Class ------------
class Product(ABC):
    def __init__(self, product_id, name, price, quantity_in_stock):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantitiy_in_stock = quantity_in_stock
        
    @abstractmethod
    def __str__(self):
        pass
    
    def restock(self, amount):
        self.quantity_in_stock += amount
        
    def sell(self, quantity):
        if quantity > self.quantity_in_stock:
            raise InsufficentStockError("Not enough stock availble.")
        self.quantitiy_in_stock -= quantity
            
    def get_total_value(self):
        return self.price * self.quantity_in_stock
    
    def to_dict(self):
        return{
            "type": self.__class__.__name__,
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity_in_stock": self.quantitiy_in_stock,
        }
        
# ------------ Subclasses ------------
class Electronics(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, warranty_years, brand):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.warranty_years = warranty_years
        self.brand = brand
        
    def __str__(self):
        return f"[Electronics] {self.name} ({self.brand}) - ${self.price}, Qty: {self.quantity_in_stock}, Warranty: {self.warranty_years} yrs"
    
    def to_dict(self):
        data = super().to_dict
        data.update({"warranty_years": self.warranty_years, "brand": self.brand})
        return data
    
class Grocery(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, expiry_date):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.expiry_date = expiry_date
    
    def is_expired(self):
        return datetime.strptime(self.expiry_date, "%Y-%m-%d") < datetime.now()

    def __str__(self):
        status = "Expired" if self.is_expired() else "Valid"
        return f"[Grocery] {self.name} - ${self.price}, Qty: {self.quantity_in_stock}, Exp: {self.expiry_date} ({status})"

    def to_dict(self):
        data = super().to_dict()
        data.update({"expiry_date": self.expiry_date})
        return data
    
class Clothing(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, size, material):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.size = size
        self.material = material
        
    def __str__(self):
        return f"[Clothing] {self.name} - ${self.price}, Qty: {self.quantity_in_stock}, Size: {self.size}, Material: {self.material}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"size": self.size, "material": self.material})
        return data
    
#------------ Inventory Class ------------
class Inventory:
    def __init__(self):
        self.products = {}
        
    def add_product(self, product):
        if product.product_id in self.products:
            raise DuplicateProductError("Product with this ID already exists.")
        self.products[product.product_id] = product
        
    def remove_product(self, product_id):
        if product_id in self.products:
            del self.products[product_id]

    def search_by_name(self, name):
        return [p for p in self.products.values() if name.lower() in p._name.lower()]

    def search_by_type(self, product_type):
        return [p for p in self.products.values() if p.__class__.__name__.lower() == product_type.lower()]

    def list_all_products(self):
        return list(self.products.values())

    def sell_product(self, product_id, quantity):
        if product_id in self.products:
            self.products[product_id].sell(quantity)

    def restock_product(self, product_id, quantity):
        if product_id in self.products:
            self.products[product_id].restock(quantity)

    def total_inventory_value(self):
        return sum(p.get_total_value() for p in self.products.values())

    def remove_expired_products(self):
        expired_ids = [pid for pid, p in self.products.items() if isinstance(p, Grocery) and p.is_expired()]
        for pid in expired_ids:
            del self.products[pid]

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump([p.to_dict() for p in self.products.values()], f, indent=2)

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            for item in data:
                ptype = item["type"]
                if ptype == "Electronics":
                    product = Electronics(item["product_id"], item["name"], item["price"], item["quantity_in_stock"], item["warranty_years"], item["brand"])
                elif ptype == "Grocery":
                    product = Grocery(item["product_id"], item["name"], item["price"], item["quantity_in_stock"], item["expiry_date"])
                elif ptype == "Clothing":
                    product = Clothing(item["product_id"], item["name"], item["price"], item["quantity_in_stock"], item["size"], item["material"])
                else:
                    raise InvalidProductDataError("Unknown product type in file.")

                self._products[product._product_id] = product

        except Exception as e:
            raise InvalidProductDataError(str(e))

#------------ CLI Menu -------------
def main():
    inventory = Inventory()

    while True:
        print("\nInventory Management System")
        print("1. Add Product")
        print("2. Sell Product")
        print("3. Search/View Product")
        print("4. Save Inventory")
        print("5. Load Inventory")
        print("6. List All Products")
        print("7. Remove Expired Groceries")
        print("8. Exit")

        choice = input("Choose an option: ")

        try:
            if choice == '1':
                ptype = input("Type (Electronics/Grocery/Clothing): ").strip()
                pid = input("Product ID: ")
                name = input("Name: ")
                price = float(input("Price: "))
                qty = int(input("Quantity: "))

                if ptype.lower() == "electronics":
                    brand = input("Brand: ")
                    warranty = int(input("Warranty (years): "))
                    product = Electronics(pid, name, price, qty, warranty, brand)

                elif ptype.lower() == "grocery":
                    expiry = input("Expiry Date (YYYY-MM-DD): ")
                    product = Grocery(pid, name, price, qty, expiry)

                elif ptype.lower() == "clothing":
                    size = input("Size: ")
                    material = input("Material: ")
                    product = Clothing(pid, name, price, qty, size, material)

                else:
                    print("Invalid product type.")
                    continue

                inventory.add_product(product)
                print("Product added.")

            elif choice == '2':
                pid = input("Product ID: ")
                qty = int(input("Quantity to sell: "))
                inventory.sell_product(pid, qty)
                print("Product sold.")

            elif choice == '3':
                name = input("Enter name to search: ")
                results = inventory.search_by_name(name)
                for r in results:
                    print(r)

            elif choice == '4':
                filename = input("Enter filename to save (e.g. inventory.json): ")
                inventory.save_to_file(filename)
                print("Inventory saved.")

            elif choice == '5':
                filename = input("Enter filename to load: ")
                inventory.load_from_file(filename)
                print("Inventory loaded.")

            elif choice == '6':
                for p in inventory.list_all_products():
                    print(p)

            elif choice == '7':
                inventory.remove_expired_products()
                print("Expired groceries removed.")

            elif choice == '8':
                print("Goodbye!")
                break

            else:
                print("Invalid choice.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

        
    