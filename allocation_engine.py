"""
AllocationEngine module - Handles parking slot allocation logic
"""

class AllocationEngine:
    """Manages parking slot allocation with zone preference"""
    
    CROSS_ZONE_PENALTY = 5.0  # Extra cost for cross-zone allocation
    
    def __init__(self, zones):
        """
        Initialize allocation engine
        
        Args:
            zones: Dictionary of zone_id -> Zone objects
        """
        self.zones = zones
        
    def allocate(self, request):
        """
        Allocate a parking slot for a request
        
        Args:
            request: ParkingRequest object
            
        Returns:
            tuple: (success, slot, zone_id, message)
        """
        requested_zone_id = request.requested_zone
        
        # Try same-zone allocation first
        slot = self._allocate_in_zone(requested_zone_id)
        if slot:
            request.allocate_slot(slot, requested_zone_id)
            slot.occupy(request.vehicle_id)
            return True, slot, requested_zone_id, "Allocated in requested zone"
        
        # Try cross-zone allocation in adjacent zones
        if requested_zone_id in self.zones:
            requested_zone = self.zones[requested_zone_id]
            for adjacent_zone in requested_zone.adjacent_zones:
                slot = self._allocate_in_zone(adjacent_zone.zone_id)
                if slot:
                    request.allocate_slot(slot, adjacent_zone.zone_id)
                    slot.occupy(request.vehicle_id)
                    return True, slot, adjacent_zone.zone_id, f"Cross-zone allocation (penalty: ${self.CROSS_ZONE_PENALTY})"
        
        # No slots available anywhere
        return False, None, None, "No parking slots available"
    
    def _allocate_in_zone(self, zone_id):
        """
        Find first available slot in a zone
        
        Args:
            zone_id: ID of the zone to search
            
        Returns:
            ParkingSlot or None
        """
        if zone_id not in self.zones:
            return None
            
        zone = self.zones[zone_id]
        available_slots = zone.get_available_slots()
        
        if available_slots:
            return available_slots[0]  # First-available strategy
        return None
    
    def deallocate(self, request):
        """
        Deallocate a parking slot
        
        Args:
            request: ParkingRequest object with allocated slot
        """
        if request.allocated_slot:
            request.allocated_slot.release()