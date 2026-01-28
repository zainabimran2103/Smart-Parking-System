"""
ParkingSlot module - Represents an individual parking slot
"""

class ParkingSlot:
    """Represents a single parking slot"""
    
    def __init__(self, slot_id, zone_id, area_id):
        """
        Initialize a parking slot
        
        Args:
            slot_id: Unique identifier for the slot
            zone_id: ID of the zone this slot belongs to
            area_id: ID of the area this slot belongs to
        """
        self.slot_id = slot_id
        self.zone_id = zone_id
        self.area_id = area_id
        self.is_available = True
        self.current_vehicle = None
        
    def occupy(self, vehicle_id):
        """Occupy this slot with a vehicle"""
        if not self.is_available:
            raise ValueError(f"Slot {self.slot_id} is already occupied")
        self.is_available = False
        self.current_vehicle = vehicle_id
        
    def release(self):
        """Release this slot"""
        if self.is_available:
            raise ValueError(f"Slot {self.slot_id} is already available")
        self.is_available = True
        self.current_vehicle = None
        
    def __repr__(self):
        status = "Available" if self.is_available else f"Occupied by {self.current_vehicle}"
        return f"Slot({self.slot_id}, Zone: {self.zone_id}, {status})"