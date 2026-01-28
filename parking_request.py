"""
ParkingRequest module - Manages parking requests with state machine
"""

from datetime import datetime
from enum import Enum

class RequestState(Enum):
    """Enumeration of parking request states"""
    REQUESTED = "REQUESTED"
    ALLOCATED = "ALLOCATED"
    OCCUPIED = "OCCUPIED"
    RELEASED = "RELEASED"
    CANCELLED = "CANCELLED"

class ParkingRequest:
    """Represents a parking request with lifecycle management"""
    
    # Define valid state transitions
    VALID_TRANSITIONS = {
        RequestState.REQUESTED: [RequestState.ALLOCATED, RequestState.CANCELLED],
        RequestState.ALLOCATED: [RequestState.OCCUPIED, RequestState.CANCELLED],
        RequestState.OCCUPIED: [RequestState.RELEASED],
        RequestState.RELEASED: [],
        RequestState.CANCELLED: []
    }
    
    def __init__(self, request_id, vehicle_id, requested_zone, request_time=None):
        """
        Initialize a parking request
        
        Args:
            request_id: Unique identifier for the request
            vehicle_id: ID of the vehicle making the request
            requested_zone: Zone ID where parking is requested
            request_time: Time of request (defaults to current time)
        """
        self.request_id = request_id
        self.vehicle_id = vehicle_id
        self.requested_zone = requested_zone
        self.request_time = request_time or datetime.now()
        self.state = RequestState.REQUESTED
        self.allocated_slot = None
        self.allocated_zone = None
        self.allocation_time = None
        self.occupation_time = None
        self.release_time = None
        self.cancellation_time = None
        self.is_cross_zone = False
        self.state_history = [(RequestState.REQUESTED, self.request_time)]
        
    def transition_to(self, new_state):
        """
        Transition request to a new state
        
        Args:
            new_state: Target state to transition to
            
        Raises:
            ValueError: If transition is invalid
        """
        if new_state not in self.VALID_TRANSITIONS[self.state]:
            raise ValueError(
                f"Invalid transition from {self.state.value} to {new_state.value}"
            )
        
        old_state = self.state
        self.state = new_state
        timestamp = datetime.now()
        self.state_history.append((new_state, timestamp))
        
        # Update relevant timestamps
        if new_state == RequestState.ALLOCATED:
            self.allocation_time = timestamp
        elif new_state == RequestState.OCCUPIED:
            self.occupation_time = timestamp
        elif new_state == RequestState.RELEASED:
            self.release_time = timestamp
        elif new_state == RequestState.CANCELLED:
            self.cancellation_time = timestamp
            
    def allocate_slot(self, slot, zone_id):
        """
        Allocate a parking slot to this request
        
        Args:
            slot: ParkingSlot object
            zone_id: ID of the zone where slot is allocated
        """
        self.allocated_slot = slot
        self.allocated_zone = zone_id
        self.is_cross_zone = (zone_id != self.requested_zone)
        self.transition_to(RequestState.ALLOCATED)
        
    def occupy(self):
        """Mark the slot as occupied"""
        self.transition_to(RequestState.OCCUPIED)
        
    def release(self):
        """Release the parking slot"""
        self.transition_to(RequestState.RELEASED)
        
    def cancel(self):
        """Cancel the parking request"""
        self.transition_to(RequestState.CANCELLED)
        
    def get_parking_duration(self):
        """Get parking duration in minutes"""
        if self.occupation_time and self.release_time:
            duration = (self.release_time - self.occupation_time).total_seconds() / 60
            return duration
        return None
    
    def __repr__(self):
        return (f"ParkingRequest({self.request_id}, Vehicle: {self.vehicle_id}, "
                f"State: {self.state.value}, Slot: {self.allocated_slot.slot_id if self.allocated_slot else 'None'})")