class Result:
    def __init__(self, participants=None, ranks=None, inventory=None):
        self.participants = participants if participants is not None else []
        self.ranks = ranks if ranks is not None else []
        self.inventory = inventory
        self.race_results = {}
        self.result_counter = 0
        
        if participants and ranks:
            if not isinstance(self.participants, list) or not isinstance(self.ranks, list):
                raise ValueError("Invalid result: participants and ranks must be lists")
            if len(self.participants) != len(self.ranks):
                raise ValueError("Invalid result: participants and ranks must have the same length")

    def record_outcome(self, race_id, driver_name, car_name, finishing_position, prize_money=0):
        valid_positions = ["Win", "Loss", "2nd", "3rd", "4th", "5th", "DNF"]
        if finishing_position not in valid_positions:
            raise ValueError(f"Invalid position: {finishing_position}")
        
        if prize_money < 0:
            raise ValueError("Prize money cannot be negative")
        
        self.result_counter += 1
        result_id = self.result_counter
        
        self.race_results[result_id] = {
            "race_id": race_id,
            "driver": driver_name,
            "car": car_name,
            "position": finishing_position,
            "prize_money": prize_money,
            "processed": False
        }
        
        return result_id

    def process_payout(self, result_id):
        if result_id not in self.race_results:
            raise ValueError(f"Result {result_id} not found")
        
        result = self.race_results[result_id]
        if result["processed"]:
            raise ValueError(f"Result {result_id} already processed")
        
        if self.inventory:
            self.inventory.add_cash(result["prize_money"])
        
        result["processed"] = True

    def update_rankings(self, driver_name, position_change):
        pass

    def process_wear_and_tear(self, result_id, wear_chance=0.5):
        import random
        
        if result_id not in self.race_results:
            raise ValueError(f"Result {result_id} not found")
        
        result = self.race_results[result_id]
        car_name = result["car"]
        
        if random.random() < wear_chance:
            if self.inventory:
                self.inventory.update_car_status(car_name, "Damaged")

    def has_result_been_processed(self, result_id):
        if result_id not in self.race_results:
            return False
        return self.race_results[result_id]["processed"]

    def get_result_info(self, result_id):
        return self.race_results.get(result_id)

    def view_all_results(self):
        return self.race_results.copy()
