"""
ParkingSystem module - Main system integrating all components
"""

from zone import Zone
from parking_area import ParkingArea
from parking_slot import ParkingSlot
from vehicle import Vehicle
from parking_request import ParkingRequest, RequestState
from allocation_engine import AllocationEngine
from rollback_manager import RollbackManager
from datetime import datetime

class ParkingSystem:
    """Main parking management system"""
    
    def __init__(self):
        """Initialize the parking system"""
        self.zones = {}
        self.vehicles = {}
        self.requests = {}
        self.request_counter = 0
        self.allocation_engine = None
        self.rollback_manager = RollbackManager()
        self.trip_history = []
        
    def add_zone(self, zone_id, zone_name):
        """Add a zone to the system"""
        zone = Zone(zone_id, zone_name)
        self.zones[zone_id] = zone
        return zone
    
    def add_parking_area(self, zone_id, area_id, area_name, num_slots):
        """Add a parking area with slots to a zone"""
        if zone_id not in self.zones:
            raise ValueError(f"Zone {zone_id} does not exist")
            
        zone = self.zones[zone_id]
        area = ParkingArea(area_id, zone_id, area_name)
        
        # Create slots for this area
        for i in range(num_slots):
            slot_id = f"{area_id}-{i+1}"
            slot = ParkingSlot(slot_id, zone_id, area_id)
            area.add_slot(slot)
            
        zone.add_parking_area(area)
        return area
    
    def connect_zones(self, zone1_id, zone2_id):
        """Connect two zones as adjacent (bidirectional)"""
        if zone1_id in self.zones and zone2_id in self.zones:
            self.zones[zone1_id].add_adjacent_zone(self.zones[zone2_id])
            self.zones[zone2_id].add_adjacent_zone(self.zones[zone1_id])
            
    def initialize_allocation_engine(self):
        """Initialize the allocation engine with current zones"""
        self.allocation_engine = AllocationEngine(self.zones)
        
    def register_vehicle(self, vehicle_id, preferred_zone=None):
        """Register a vehicle in the system"""
        vehicle = Vehicle(vehicle_id, preferred_zone)
        self.vehicles[vehicle_id] = vehicle
        return vehicle
    
    def create_parking_request(self, vehicle_id, requested_zone):
        """Create a new parking request"""
        self.request_counter += 1
        request_id = f"REQ-{self.request_counter}"
        
        request = ParkingRequest(request_id, vehicle_id, requested_zone)
        self.requests[request_id] = request
        
        return request
    
    def process_request(self, request_id):
        """Process a parking request"""
        if request_id not in self.requests:
            return False, "Request not found"
            
        request = self.requests[request_id]
        
        if request.state != RequestState.REQUESTED:
            return False, f"Request is in {request.state.value} state"
        
        # Allocate parking
        success, slot, zone_id, message = self.allocation_engine.allocate(request)
        
        if success:
            # Record for rollback
            self.rollback_manager.record_allocation(request, slot)
            return True, message
        else:
            return False, message
    
    def occupy_slot(self, request_id):
        """Mark a parking slot as occupied"""
        if request_id not in self.requests:
            return False, "Request not found"
            
        request = self.requests[request_id]
        
        if request.state != RequestState.ALLOCATED:
            return False, f"Request is in {request.state.value} state"
        
        try:
            request.occupy()
            return True, "Slot occupied successfully"
        except ValueError as e:
            return False, str(e)
    
    def release_slot(self, request_id):
        """Release a parking slot"""
        if request_id not in self.requests:
            return False, "Request not found"
            
        request = self.requests[request_id]
        
        if request.state != RequestState.OCCUPIED:
            return False, f"Request is in {request.state.value} state"
        
        try:
            request.release()
            self.allocation_engine.deallocate(request)
            # Add to trip history
            self.trip_history.append(request)
            return True, "Slot released successfully"
        except ValueError as e:
            return False, str(e)
    
    def cancel_request(self, request_id):
        """Cancel a parking request"""
        if request_id not in self.requests:
            return False, "Request not found"
            
        request = self.requests[request_id]
        
        if request.state in [RequestState.RELEASED, RequestState.CANCELLED]:
            return False, f"Request is already {request.state.value}"
        
        try:
            # If allocated, deallocate first
            if request.state in [RequestState.ALLOCATED, RequestState.OCCUPIED]:
                self.allocation_engine.deallocate(request)
            
            request.cancel()
            self.trip_history.append(request)
            return True, "Request cancelled successfully"
        except ValueError as e:
            return False, str(e)
    
    def rollback_allocations(self, k):
        """Rollback last k allocations"""
        rolled_back = self.rollback_manager.rollback(k)
        return True, f"Rolled back {len(rolled_back)} allocations: {rolled_back}"
    
    def get_analytics(self):
        """Get comprehensive analytics"""
        analytics = {
            'total_requests': len(self.requests),
            'completed_requests': 0,
            'cancelled_requests': 0,
            'active_requests': 0,
            'average_parking_duration': 0,
            'zone_utilization': {},
            'peak_usage_zone': None,
            'cross_zone_allocations': 0
        }
        
        # Count request states
        for request in self.requests.values():
            if request.state == RequestState.RELEASED:
                analytics['completed_requests'] += 1
            elif request.state == RequestState.CANCELLED:
                analytics['cancelled_requests'] += 1
            elif request.state in [RequestState.ALLOCATED, RequestState.OCCUPIED]:
                analytics['active_requests'] += 1
        
        # Calculate average parking duration
        durations = [r.get_parking_duration() for r in self.trip_history 
                     if r.state == RequestState.RELEASED and r.get_parking_duration()]
        if durations:
            analytics['average_parking_duration'] = sum(durations) / len(durations)
        
        # Zone utilization
        max_utilization = 0
        peak_zone = None
        for zone_id, zone in self.zones.items():
            utilization = zone.get_utilization_rate()
            analytics['zone_utilization'][zone_id] = {
                'name': zone.zone_name,
                'utilization': utilization,
                'occupied': zone.get_occupied_slots(),
                'total': zone.get_total_slots()
            }
            if utilization > max_utilization:
                max_utilization = utilization
                peak_zone = zone_id
        
        analytics['peak_usage_zone'] = peak_zone
        
        # Cross-zone allocations
        analytics['cross_zone_allocations'] = sum(
            1 for r in self.requests.values() if r.is_cross_zone
        )
        
        return analytics
    
    def get_system_state(self):
        """Get current system state for display"""
        state = {
            'zones': [],
            'requests': [],
            'vehicles': len(self.vehicles)
        }
        
        # Zone information
        for zone_id, zone in self.zones.items():
            zone_data = {
                'zone_id': zone_id,
                'zone_name': zone.zone_name,
                'total_slots': zone.get_total_slots(),
                'available_slots': len(zone.get_available_slots()),
                'occupied_slots': zone.get_occupied_slots(),
                'utilization': zone.get_utilization_rate(),
                'areas': []
            }
            
            for area in zone.parking_areas:
                area_data = {
                    'area_id': area.area_id,
                    'area_name': area.area_name,
                    'total_slots': area.get_total_slots(),
                    'available_slots': len(area.get_available_slots())
                }
                zone_data['areas'].append(area_data)
            
            state['zones'].append(zone_data)
        
        # Request information
        for request_id, request in self.requests.items():
            request_data = {
                'request_id': request_id,
                'vehicle_id': request.vehicle_id,
                'requested_zone': request.requested_zone,
                'allocated_zone': request.allocated_zone,
                'state': request.state.value,
                'is_cross_zone': request.is_cross_zone,
                'slot_id': request.allocated_slot.slot_id if request.allocated_slot else None,
                'request_time': request.request_time.isoformat() if request.request_time else None
            }
            state['requests'].append(request_data)
        
        return state