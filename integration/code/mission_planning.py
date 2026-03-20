class MissionPlanner:
    def __init__(self, crew_manager=None, inventory=None):
        self.missions = {}
        self.mission_counter = 0
        self.crew_manager = crew_manager
        self.inventory = inventory
        self.valid_mission_types = [
            "Delivery", "Impound", "Repair", "Robbery", 
            "Escort", "Search", "Transport", "Escape"
        ]

    def create_mission(self, name, mission_type, required_roles, reward=0):
        if mission_type not in self.valid_mission_types:
            raise ValueError(f"Invalid mission type: {mission_type}")
        
        if not isinstance(required_roles, dict):
            raise ValueError("Required roles must be a dictionary")
        
        if reward < 0:
            raise ValueError("Reward cannot be negative")
        
        self.mission_counter += 1
        mission_id = self.mission_counter
        
        self.missions[mission_id] = {
            "name": name,
            "type": mission_type,
            "required_roles": required_roles.copy(),
            "assigned_crew": {},
            "reward": reward,
            "status": "Not Started",
            "requires_mechanic_for_repair": False
        }
        
        return mission_id

    def assign_crew(self, mission_id, crew_assignment):
        if mission_id not in self.missions:
            raise ValueError(f"Mission {mission_id} not found")
        
        mission = self.missions[mission_id]
        required_roles = mission["required_roles"]
        for required_role, required_count in required_roles.items():
            if required_role not in crew_assignment:
                raise ValueError(f"Missing assignment for role: {required_role}")
            
            assigned_crew = crew_assignment[required_role]
            if not isinstance(assigned_crew, list):
                assigned_crew = [assigned_crew]
            
            if len(assigned_crew) < required_count:
                raise ValueError(
                    f"Expected {required_count} {required_role}(s), "
                    f"got {len(assigned_crew)}"
                )
            if self.crew_manager:
                for member in assigned_crew:
                    if not self.crew_manager.has_role(member, required_role):
                        raise ValueError(
                            f"'{member}' does not have the {required_role} role"
                        )
            
            mission["assigned_crew"][required_role] = assigned_crew
        
        mission["status"] = "Assigned"

    def check_damaged_cars_require_mechanic(self):
        if not self.inventory:
            return False
        
        garage = self.inventory.view_garage()
        damaged_cars = [name for name, info in garage.items() if info["status"] == "Damaged"]
        has_repair_mission = any(
            mission.get("type") == "Repair" and "Mechanic" in mission.get("assigned_crew", {})
            for mission in self.missions.values()
            if mission.get("status") not in ["Completed", "Failed"]
        )
        
        return len(damaged_cars) > 0 and not has_repair_mission

    def complete_mission(self, mission_id, success=True):
        if mission_id not in self.missions:
            raise ValueError(f"Mission {mission_id} not found")
        
        mission = self.missions[mission_id]
        status = "Completed" if success else "Failed"
        mission["status"] = status
        if success and mission["type"] == "Repair" and self.inventory:
            garage = self.inventory.view_garage()
            damaged_cars = [name for name, info in garage.items() if info["status"] == "Damaged"]
            for car_name in damaged_cars:
                self.inventory.update_car_status(car_name, "Pristine")
        if success and self.inventory:
            self.inventory.add_cash(mission["reward"])

    def get_mission_info(self, mission_id):
        return self.missions.get(mission_id)

    def view_all_missions(self):
        return self.missions.copy()

    def get_active_missions(self):
        return {
            mid: mission for mid, mission in self.missions.items()
            if mission["status"] not in ["Completed", "Failed"]
        }

    def is_mission_fully_staffed(self, mission_id):
        if mission_id not in self.missions:
            return False
        
        mission = self.missions[mission_id]
        required_roles = mission["required_roles"]
        assigned_crew = mission["assigned_crew"]
        
        for role, count in required_roles.items():
            if role not in assigned_crew or len(assigned_crew[role]) < count:
                return False
        
        return True
