"""
ParkingArea module - Represents a parking area within a zone
"""

class ParkingArea:
    """Represents a parking area containing multiple parking slots"""
    
    def __init__(self, area_id, zone_id, area_name):
        """
        Initialize a parking area
        
        Args:
            area_id: Unique identifier for the area
            zone_id: ID of the zone this area belongs to
            area_name: Name of the parking area
        """
        self.area_id = area_id
        self.zone_id = zone_id
        self.area_name = area_name
        self.slots = []
        
    def add_slot(self, slot):
        """Add a parking slot to this area"""
        self.slots.append(slot)
        
    def get_available_slots(self):
        """Get all available slots in this area"""
        return [slot for slot in self.slots if slot.is_available]
    
    def get_total_slots(self):
        """Get total number of slots in this area"""
        return len(self.slots)
    
    def get_occupied_slots(self):
        """Get number of occupied slots in this area"""
        return sum(1 for slot in self.slots if not slot.is_available)
    
    def __repr__(self):
        return f"ParkingArea({self.area_id}, Zone: {self.zone_id}, Slots: {len(self.slots)})"