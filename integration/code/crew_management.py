class CrewManager:
    def __init__(self, registration=None):
        self.crew = {}
        self.registration = registration
        self.valid_roles = ["Driver", "Mechanic", "Strategist", "Engineer", "Lookout"]

    def assign_role(self, member_name, role):

        if self.registration:
            if member_name not in self.registration.view():
                raise ValueError(f"Member '{member_name}' not found in registration")
        
        if role not in self.valid_roles:
            raise ValueError(f"Invalid role: {role}. Valid roles: {self.valid_roles}")
        
        if member_name not in self.crew:
            self.crew[member_name] = {"role": None, "skill_level": 1}
        
        self.crew[member_name]["role"] = role

    def update_skill_level(self, member_name, new_level):
        if member_name not in self.crew:
            raise ValueError(f"Member '{member_name}' not found in crew")
        
        if not (1 <= new_level <= 10):
            raise ValueError("Skill level must be between 1 and 10")
        
        self.crew[member_name]["skill_level"] = new_level

    def has_role(self, member_name, role):
        if member_name not in self.crew:
            return False
        return self.crew[member_name]["role"] == role

    def get_members_by_role(self, role):
        return [name for name, info in self.crew.items() if info["role"] == role]

    def get_member_info(self, member_name):
        return self.crew.get(member_name, None)

    def view_crew(self):
        return self.crew.copy()
