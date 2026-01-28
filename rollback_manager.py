"""
RollbackManager module - Manages rollback operations for parking allocations
"""

class RollbackManager:
    """Manages rollback of parking allocations using a stack"""
    
    def __init__(self):
        """Initialize rollback manager with an empty operation stack"""
        self.operation_stack = []
        
    def record_allocation(self, request, slot):
        """
        Record an allocation operation for potential rollback
        
        Args:
            request: ParkingRequest object
            slot: ParkingSlot that was allocated
        """
        operation = {
            'type': 'allocation',
            'request': request,
            'slot': slot,
            'previous_state': request.state,
            'vehicle_id': request.vehicle_id
        }
        self.operation_stack.append(operation)
        
    def rollback(self, k=1):
        """
        Rollback the last k allocation operations
        
        Args:
            k: Number of operations to rollback
            
        Returns:
            list: List of rolled back request IDs
        """
        if k > len(self.operation_stack):
            k = len(self.operation_stack)
            
        rolled_back = []
        
        for _ in range(k):
            if not self.operation_stack:
                break
                
            operation = self.operation_stack.pop()
            
            if operation['type'] == 'allocation':
                request = operation['request']
                slot = operation['slot']
                
                # Restore slot availability
                if not slot.is_available:
                    slot.release()
                
                # Restore request state
                request.state = operation['previous_state']
                request.allocated_slot = None
                request.allocated_zone = None
                
                rolled_back.append(request.request_id)
                
        return rolled_back
    
    def clear(self):
        """Clear the operation stack"""
        self.operation_stack.clear()
        
    def get_stack_size(self):
        """Get the current size of the operation stack"""
        return len(self.operation_stack)
    