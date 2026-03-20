class Registration:

    def __init__(self, participants=None):
        self.participants = participants if participants is not None else []

        if not isinstance(self.participants, list):
            raise ValueError("Invalid registration: participants must be a list")
        
    def register(self, participant):
        if participant in self.participants:
            raise ValueError("Participant already registered")
        self.participants.append(participant)

    def view(self):
        return self.participants.copy()

    def unregister(self, participant):
        if participant not in self.participants:
            raise ValueError(f"Participant '{participant}' not registered")
        self.participants.remove(participant)

    def is_registered(self, participant):
        return participant in self.participants
