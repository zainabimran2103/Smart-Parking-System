"""
Vehicle module - Represents a vehicle in the parking system
"""

class Vehicle:
    """Represents a vehicle seeking parking"""
    
    def __init__(self, vehicle_id, preferred_zone=None):
        """
        Initialize a vehicle
        
        Args:
            vehicle_id: Unique identifier for the vehicle
            preferred_zone: Preferred zone for parking (optional)
        """
        self.vehicle_id = vehicle_id
        self.preferred_zone = preferred_zone
        
    def __repr__(self):
        return f"Vehicle({self.vehicle_id}, Preferred Zone: {self.preferred_zone})"