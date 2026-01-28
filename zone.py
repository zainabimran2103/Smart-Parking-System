"""
Zone module - Represents a parking zone in the city
"""

class Zone:
    """Represents a parking zone containing multiple parking areas"""
    
    def __init__(self, zone_id, zone_name):
        """
        Initialize a parking zone
        
        Args:
            zone_id: Unique identifier for the zone
            zone_name: Name of the zone
        """
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.parking_areas = []
        self.adjacent_zones = []
        
    def add_parking_area(self, parking_area):
        """Add a parking area to this zone"""
        self.parking_areas.append(parking_area)
        
    def add_adjacent_zone(self, zone):
        """Add an adjacent zone for cross-zone allocation"""
        if zone not in self.adjacent_zones:
            self.adjacent_zones.append(zone)
            
    def get_available_slots(self):
        """Get all available parking slots in this zone"""
        available_slots = []
        for area in self.parking_areas:
            available_slots.extend(area.get_available_slots())
        return available_slots
    
    def get_total_slots(self):
        """Get total number of slots in this zone"""
        return sum(area.get_total_slots() for area in self.parking_areas)
    
    def get_occupied_slots(self):
        """Get number of occupied slots in this zone"""
        return sum(area.get_occupied_slots() for area in self.parking_areas)
    
    def get_utilization_rate(self):
        """Calculate zone utilization rate"""
        total = self.get_total_slots()
        if total == 0:
            return 0.0
        return (self.get_occupied_slots() / total) * 100
    
    def __repr__(self):
        return f"Zone({self.zone_id}, {self.zone_name}, Areas: {len(self.parking_areas)})"