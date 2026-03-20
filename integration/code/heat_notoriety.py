class HeatNotoriety:
    
    def __init__(self, race_manager=None, mission_planner=None):
        self.current_heat = 0
        self.max_heat = 100
        self.heat_threshold_medium = 30
        self.heat_threshold_high = 60
        self.heat_threshold_critical = 85
        
        self.race_manager = race_manager
        self.mission_planner = mission_planner
        
        self.heat_events = {}
        self.event_counter = 0
        
        self.blocked_races = set()
    
    def add_heat(self, amount, source=""):
        if amount < 0:
            raise ValueError("Heat amount cannot be negative")
        
        previous_heat = self.current_heat
        self.current_heat = min(self.current_heat + amount, self.max_heat)
        
        self.event_counter += 1
        event_id = self.event_counter
        
        self.heat_events[event_id] = {
            "type": "Heat Added",
            "source": source,
            "amount": amount,
            "previous_heat": previous_heat,
            "new_heat": self.current_heat
        }
        
        return event_id, self.current_heat
    
    def reduce_heat(self, amount, method=""):
        if amount < 0:
            raise ValueError("Heat reduction amount cannot be negative")
        
        if amount > self.current_heat:
            raise ValueError(f"Cannot reduce heat by {amount} when only {self.current_heat} is present")
        
        previous_heat = self.current_heat
        self.current_heat -= amount
        
        self.event_counter += 1
        event_id = self.event_counter
        
        self.heat_events[event_id] = {
            "type": "Heat Reduced",
            "method": method,
            "amount": amount,
            "previous_heat": previous_heat,
            "new_heat": self.current_heat
        }
        
        return event_id, self.current_heat
    
    def get_heat_level(self):
        return self.current_heat
    
    def get_heat_status(self):
        if self.current_heat < self.heat_threshold_medium:
            return "Low"
        elif self.current_heat < self.heat_threshold_high:
            return "Medium"
        elif self.current_heat < self.heat_threshold_critical:
            return "High"
        else:
            return "Critical"
    
    def is_race_blocked(self, race_difficulty):
        difficulty_levels = {"Easy": 0, "Medium": 1, "Hard": 2, "Extreme": 3}
        difficulty_value = difficulty_levels.get(race_difficulty, 0)

        if self.current_heat >= self.heat_threshold_critical:

            return True
        elif self.current_heat >= self.heat_threshold_high:

            return difficulty_value >= 1
        elif self.current_heat >= self.heat_threshold_medium:

            return difficulty_value >= 2
        
        return False
    
    def get_blocked_races(self):
        return list(self.blocked_races).copy()
    
    def generate_evasion_mission(self):
        if self.current_heat < self.heat_threshold_critical:
            raise ValueError(
                f"Evasion mission only available at critical heat "
                f"({self.heat_threshold_critical}+). Current: {self.current_heat}"
            )
        
        if not self.mission_planner:
            raise ValueError("No mission planning system available")

        mission_id = self.mission_planner.create_mission(
            name="URGENT: Evade the Cops",
            mission_type="Escape",
            required_roles={"Driver": 1, "Strategist": 1},
            reward=15000
        )
        
        return mission_id
    
    def get_race_multiplication_factor(self, race_difficulty):
        difficulty_levels = {"Easy": 1.0, "Medium": 1.5, "Hard": 2.0, "Extreme": 3.0}
        base_multiplier = difficulty_levels.get(race_difficulty, 1.0)

        if self.current_heat >= self.heat_threshold_critical:
            heat_multiplier = 3.0
        elif self.current_heat >= self.heat_threshold_high:
            heat_multiplier = 2.0
        elif self.current_heat >= self.heat_threshold_medium:
            heat_multiplier = 1.5
        else:
            heat_multiplier = 1.0
        
        return base_multiplier * heat_multiplier
    
    def process_race_heat(self, race_difficulty, won=True):
        if not won:

            return None, 0, self.current_heat

        difficulty_levels = {"Easy": 5, "Medium": 10, "Hard": 20, "Extreme": 35}
        base_heat = difficulty_levels.get(race_difficulty, 5)

        multiplier = self.get_race_multiplication_factor(race_difficulty)
        heat_to_add = int(base_heat * multiplier)
        
        event_id, new_heat = self.add_heat(heat_to_add, f"Won {race_difficulty} race")
        
        return event_id, heat_to_add, new_heat
    
    def view_heat_events(self):
        return self.heat_events.copy()
    
    def reset_heat(self):
        previous_heat = self.current_heat
        self.current_heat = 0
        
        self.event_counter += 1
        event_id = self.event_counter
        
        self.heat_events[event_id] = {
            "type": "Heat Reset",
            "source": "Safe house access",
            "previous_heat": previous_heat,
            "new_heat": 0
        }
        
        return event_id
