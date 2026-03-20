class Inventory:

    def __init__(self, items=None, cash=0):
        self.items = items if items is not None else []
        if not isinstance(self.items, list):
            raise ValueError("Invalid inventory: items must be a list")
        
        self.cars = {}
        self.equipment = []
        self.cash = cash
        
        if cash < 0:
            raise ValueError("Invalid inventory: cash cannot be negative")

    def add_car(self, car_name, tier=1, status="Pristine"):
        if car_name in self.cars:
            raise ValueError(f"Car '{car_name}' already exists in garage")
        
        valid_statuses = ["Pristine", "Damaged", "In-Repair"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Valid: {valid_statuses}")
        
        if not (1 <= tier <= 5):
            raise ValueError("Car tier must be between 1 and 5")
        
        self.cars[car_name] = {"status": status, "tier": tier}

    def remove_car(self, car_name):
        if car_name not in self.cars:
            raise ValueError(f"Car '{car_name}' not found in garage")
        
        del self.cars[car_name]

    def get_car_status(self, car_name):
        if car_name not in self.cars:
            return None
        return self.cars[car_name]["status"]

    def update_car_status(self, car_name, status):
        if car_name not in self.cars:
            raise ValueError(f"Car '{car_name}' not found in garage")
        
        valid_statuses = ["Pristine", "Damaged", "In-Repair"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Valid: {valid_statuses}")
        
        self.cars[car_name]["status"] = status

    def add_equipment(self, equipment_name):
        self.equipment.append(equipment_name)

    def remove_equipment(self, equipment_name):
        if equipment_name not in self.equipment:
            raise ValueError(f"Equipment '{equipment_name}' not found")
        self.equipment.remove(equipment_name)

    def add_cash(self, amount):
        if amount < 0:
            raise ValueError("Cannot add negative amount")
        self.cash += amount

    def subtract_cash(self, amount):
        if amount < 0:
            raise ValueError("Cannot subtract negative amount")
        if self.cash - amount < 0:
            raise ValueError("Insufficient cash balance")
        self.cash -= amount

    def get_cash_balance(self):
        return self.cash

    def is_car_available(self, car_name):
        if car_name not in self.cars:
            return False
        return self.cars[car_name]["status"] == "Pristine"

    def get_available_cars(self):
        return [name for name, info in self.cars.items() if info["status"] == "Pristine"]

    def view_garage(self):
        return self.cars.copy()

    def view_equipment(self):
        return self.equipment.copy()
