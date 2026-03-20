class ChopShop:
    
    def __init__(self, inventory=None):
        self.inventory = inventory
        self.transactions = {}
        self.transaction_counter = 0

        self.shop_cars = {
            "Economy": {"tier": 1, "base_price": 5000},
            "Sedan": {"tier": 2, "base_price": 10000},
            "Sports": {"tier": 3, "base_price": 20000},
            "Supercar": {"tier": 4, "base_price": 40000},
            "Hypercar": {"tier": 5, "base_price": 75000}
        }
        self.shop_parts = {
            "Turbo Boost": 3000,
            "Racing Suspension": 2500,
            "Reinforced Frame": 4000,
            "Nitrous System": 5000,
            "Custom Engine": 8000
        }
    
    def buy_car(self, car_type, quantity=1):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if car_type not in self.shop_cars:
            raise ValueError(f"Car type '{car_type}' not available in shop")
        
        car_info = self.shop_cars[car_type]
        cost = car_info["base_price"] * quantity
        
        if not self.inventory:
            raise ValueError("No inventory management system available")
        
        if self.inventory.get_cash_balance() < cost:
            raise ValueError(f"Insufficient funds. Need ${cost}, have ${self.inventory.get_cash_balance()}")

        self.inventory.subtract_cash(cost)

        for i in range(quantity):
            car_name = f"{car_type}_{self.transaction_counter}_{i}"
            self.inventory.add_car(car_name, tier=car_info["tier"], status="Pristine")
        
        self.transaction_counter += 1
        transaction_id = self.transaction_counter
        
        self.transactions[transaction_id] = {
            "type": "Buy Car",
            "details": f"Purchased {quantity}x {car_type} for ${cost}",
            "amount": cost,
            "status": "Completed"
        }
        
        return transaction_id
    
    def sell_car(self, car_name, resale_percentage=0.5):
        if not (0 <= resale_percentage <= 1):
            raise ValueError("Resale percentage must be between 0 and 1")
        
        if not self.inventory:
            raise ValueError("No inventory management system available")
        
        garage = self.inventory.view_garage()
        if car_name not in garage:
            raise ValueError(f"Car '{car_name}' not found in inventory")

        car_info = garage[car_name]
        car_tier = car_info["tier"]

        tier_to_price = {1: 5000, 2: 10000, 3: 20000, 4: 40000, 5: 75000}
        original_value = tier_to_price.get(car_tier, 5000)
        resale_value = int(original_value * resale_percentage)

        self.inventory.remove_car(car_name)
        self.inventory.add_cash(resale_value)
        
        self.transaction_counter += 1
        transaction_id = self.transaction_counter
        
        self.transactions[transaction_id] = {
            "type": "Sell Car",
            "details": f"Sold {car_name} for ${resale_value}",
            "amount": resale_value,
            "status": "Completed"
        }
        
        return transaction_id
    
    def buy_part(self, part_name, quantity=1):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if part_name not in self.shop_parts:
            raise ValueError(f"Part '{part_name}' not available in shop")
        
        cost = self.shop_parts[part_name] * quantity
        
        if not self.inventory:
            raise ValueError("No inventory management system available")
        
        if self.inventory.get_cash_balance() < cost:
            raise ValueError(f"Insufficient funds. Need ${cost}, have ${self.inventory.get_cash_balance()}")

        self.inventory.subtract_cash(cost)

        for i in range(quantity):
            equipment_name = f"{part_name}_{self.transaction_counter}_{i}"
            self.inventory.add_equipment(equipment_name)
        
        self.transaction_counter += 1
        transaction_id = self.transaction_counter
        
        self.transactions[transaction_id] = {
            "type": "Buy Part",
            "details": f"Purchased {quantity}x {part_name} for ${cost}",
            "amount": cost,
            "status": "Completed"
        }
        
        return transaction_id
    
    def sell_part(self, part_name, resale_percentage=0.3):
        if not (0 <= resale_percentage <= 1):
            raise ValueError("Resale percentage must be between 0 and 1")
        
        if not self.inventory:
            raise ValueError("No inventory management system available")
        
        equipment = self.inventory.view_equipment()
        if part_name not in equipment:
            raise ValueError(f"Part '{part_name}' not found in inventory")
        
        original_price = self.shop_parts.get(part_name.split('_')[0], 1000)
        resale_value = int(original_price * resale_percentage)

        self.inventory.remove_equipment(part_name)
        self.inventory.add_cash(resale_value)
        
        self.transaction_counter += 1
        transaction_id = self.transaction_counter
        
        self.transactions[transaction_id] = {
            "type": "Sell Part",
            "details": f"Sold {part_name} for ${resale_value}",
            "amount": resale_value,
            "status": "Completed"
        }
        
        return transaction_id
    
    def view_shop_cars(self):
        return self.shop_cars.copy()
    
    def view_shop_parts(self):
        return self.shop_parts.copy()
    
    def view_transaction_history(self):
        return self.transactions.copy()
    
    def get_transaction(self, transaction_id):
        return self.transactions.get(transaction_id)
