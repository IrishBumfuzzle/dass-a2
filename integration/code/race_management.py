class RaceManager:
    def __init__(self, crew_manager=None, inventory=None):
        self.races = {}
        self.race_counter = 0
        self.crew_manager = crew_manager
        self.inventory = inventory
        self.difficulty_levels = ["Easy", "Medium", "Hard", "Extreme"]
        self.tier_requirements = {1: "D", 2: "C", 3: "B", 4: "A", 5: "S"}

    def create_event(self, name, location, difficulty, required_car_tier):
        if difficulty not in self.difficulty_levels:
            raise ValueError(f"Invalid difficulty: {difficulty}")
        
        if not (1 <= required_car_tier <= 5):
            raise ValueError("Car tier must be between 1 and 5")
        
        self.race_counter += 1
        race_id = self.race_counter
        
        self.races[race_id] = {
            "name": name,
            "location": location,
            "difficulty": difficulty,
            "required_tier": required_car_tier,
            "driver": None,
            "car": None,
            "status": "Not Started"
        }
        
        return race_id

    def assign_lineup(self, race_id, driver_name, car_name):
        if race_id not in self.races:
            raise ValueError(f"Race {race_id} not found")
        if self.crew_manager:
            if not self.crew_manager.has_role(driver_name, "Driver"):
                raise ValueError(f"'{driver_name}' does not have the Driver role")
        if self.inventory:
            if not self.inventory.is_car_available(car_name):
                car_status = self.inventory.get_car_status(car_name)
                if car_status is None:
                    raise ValueError(f"Car '{car_name}' not found in inventory")
                else:
                    raise ValueError(f"Car '{car_name}' is {car_status} and not available")
            car_info = self.inventory.view_garage().get(car_name)
            if car_info["tier"] < self.races[race_id]["required_tier"]:
                raise ValueError(f"Car tier {car_info['tier']} below required tier {self.races[race_id]['required_tier']}")
        
        self.races[race_id]["driver"] = driver_name
        self.races[race_id]["car"] = car_name
        self.races[race_id]["status"] = "Ready"

    def get_race_info(self, race_id):
        return self.races.get(race_id)

    def view_all_races(self):
        return self.races.copy()

    def is_race_ready(self, race_id):
        if race_id not in self.races:
            return False
        race = self.races[race_id]
        return race["driver"] is not None and race["car"] is not None
