"""
Test suite for Smart Parking System
Tests allocation, cross-zone, cancellation, rollback, and analytics
"""

from parking_system import ParkingSystem
from parking_request import RequestState

def setup_test_system():
    """Setup a test parking system with zones and slots"""
    system = ParkingSystem()
    
    # Create zones
    system.add_zone("Z1", "Downtown")
    system.add_zone("Z2", "Midtown")
    system.add_zone("Z3", "Uptown")
    
    # Add parking areas with slots
    system.add_parking_area("Z1", "Z1-A1", "Downtown Plaza", 3)
    system.add_parking_area("Z1", "Z1-A2", "Downtown Mall", 2)
    system.add_parking_area("Z2", "Z2-A1", "Midtown Center", 4)
    system.add_parking_area("Z3", "Z3-A1", "Uptown Square", 3)
    
    # Connect zones
    system.connect_zones("Z1", "Z2")
    system.connect_zones("Z2", "Z3")
    
    # Initialize allocation engine
    system.initialize_allocation_engine()
    
    return system

def test_1_slot_allocation_correctness():
    """Test 1: Basic slot allocation in requested zone"""
    print("\n=== Test 1: Basic Slot Allocation ===")
    system = setup_test_system()
    
    # Register vehicle and create request
    system.register_vehicle("V001", "Z1")
    request = system.create_parking_request("V001", "Z1")
    
    # Process request
    success, message = system.process_request(request.request_id)
    
    assert success == True, "Allocation should succeed"
    assert request.state == RequestState.ALLOCATED, "Request should be in ALLOCATED state"
    assert request.allocated_zone == "Z1", "Should allocate in requested zone"
    assert request.is_cross_zone == False, "Should not be cross-zone"
    print(f"✓ Test 1 PASSED: {message}")
    return True

def test_2_cross_zone_allocation():
    """Test 2: Cross-zone allocation when requested zone is full"""
    print("\n=== Test 2: Cross-Zone Allocation ===")
    system = setup_test_system()
    
    # Fill up Z1 (5 slots total)
    for i in range(5):
        system.register_vehicle(f"V{i:03d}", "Z1")
        request = system.create_parking_request(f"V{i:03d}", "Z1")
        system.process_request(request.request_id)
    
    # Try to allocate one more in Z1 - should go to Z2
    system.register_vehicle("V100", "Z1")
    request = system.create_parking_request("V100", "Z1")
    success, message = system.process_request(request.request_id)
    
    assert success == True, "Cross-zone allocation should succeed"
    assert request.allocated_zone == "Z2", "Should allocate in adjacent zone Z2"
    assert request.is_cross_zone == True, "Should be marked as cross-zone"
    print(f"✓ Test 2 PASSED: {message}")
    return True

def test_3_no_slots_available():
    """Test 3: Allocation failure when all zones are full"""
    print("\n=== Test 3: No Slots Available ===")
    system = setup_test_system()
    
    # Fill all slots (5 + 4 + 3 = 12 total)
    for i in range(12):
        system.register_vehicle(f"V{i:03d}", "Z1")
        zone = "Z1" if i < 5 else ("Z2" if i < 9 else "Z3")
        request = system.create_parking_request(f"V{i:03d}", zone)
        system.process_request(request.request_id)
    
    # Try to allocate when full
    system.register_vehicle("V999", "Z1")
    request = system.create_parking_request("V999", "Z1")
    success, message = system.process_request(request.request_id)
    
    assert success == False, "Should fail when no slots available"
    assert "No parking slots available" in message
    print(f"✓ Test 3 PASSED: {message}")
    return True

def test_4_request_lifecycle():
    """Test 4: Complete request lifecycle REQUESTED -> ALLOCATED -> OCCUPIED -> RELEASED"""
    print("\n=== Test 4: Request Lifecycle ===")
    system = setup_test_system()
    
    system.register_vehicle("V001", "Z1")
    request = system.create_parking_request("V001", "Z1")
    
    # REQUESTED -> ALLOCATED
    assert request.state == RequestState.REQUESTED
    success, _ = system.process_request(request.request_id)
    assert success and request.state == RequestState.ALLOCATED
    
    # ALLOCATED -> OCCUPIED
    success, _ = system.occupy_slot(request.request_id)
    assert success and request.state == RequestState.OCCUPIED
    
    # OCCUPIED -> RELEASED
    success, _ = system.release_slot(request.request_id)
    assert success and request.state == RequestState.RELEASED
    
    print("✓ Test 4 PASSED: Complete lifecycle successful")
    return True

def test_5_invalid_state_transitions():
    """Test 5: Invalid state transitions should be prevented"""
    print("\n=== Test 5: Invalid State Transitions ===")
    system = setup_test_system()
    
    system.register_vehicle("V001", "Z1")
    request = system.create_parking_request("V001", "Z1")
    system.process_request(request.request_id)
    
    # Try to occupy without being allocated (now it's allocated, try to release)
    success, message = system.release_slot(request.request_id)
    assert success == False, "Should not allow ALLOCATED -> RELEASED"
    
    # Try to process an already allocated request
    success, message = system.process_request(request.request_id)
    assert success == False, "Should not allow re-processing"
    
    print("✓ Test 5 PASSED: Invalid transitions prevented")
    return True

def test_6_cancellation_from_requested():
    """Test 6: Cancel request from REQUESTED state"""
    print("\n=== Test 6: Cancellation from REQUESTED ===")
    system = setup_test_system()
    
    system.register_vehicle("V001", "Z1")
    request = system.create_parking_request("V001", "Z1")
    
    success, message = system.cancel_request(request.request_id)
    assert success == True, "Should cancel successfully"
    assert request.state == RequestState.CANCELLED
    print("✓ Test 6 PASSED: Cancelled from REQUESTED state")
    return True

def test_7_cancellation_from_allocated():
    """Test 7: Cancel request from ALLOCATED state and verify slot is released"""
    print("\n=== Test 7: Cancellation from ALLOCATED ===")
    system = setup_test_system()
    
    system.register_vehicle("V001", "Z1")
    request = system.create_parking_request("V001", "Z1")
    system.process_request(request.request_id)
    
    slot = request.allocated_slot
    assert slot.is_available == False, "Slot should be occupied"
    
    success, message = system.cancel_request(request.request_id)
    assert success == True, "Should cancel successfully"
    assert request.state == RequestState.CANCELLED
    assert slot.is_available == True, "Slot should be released after cancellation"
    print("✓ Test 7 PASSED: Cancelled from ALLOCATED and slot released")
    return True

def test_8_rollback_single_allocation():
    """Test 8: Rollback last allocation"""
    print("\n=== Test 8: Rollback Single Allocation ===")
    system = setup_test_system()
    
    system.register_vehicle("V001", "Z1")
    request = system.create_parking_request("V001", "Z1")
    system.process_request(request.request_id)
    
    slot = request.allocated_slot
    assert slot.is_available == False
    
    # Rollback
    success, message = system.rollback_allocations(1)
    assert success == True
    assert slot.is_available == True, "Slot should be available after rollback"
    assert request.allocated_slot == None, "Request should have no allocated slot"
    print(f"✓ Test 8 PASSED: {message}")
    return True

def test_9_rollback_multiple_allocations():
    """Test 9: Rollback multiple allocations"""
    print("\n=== Test 9: Rollback Multiple Allocations ===")
    system = setup_test_system()
    
    # Create 3 allocations
    requests = []
    for i in range(3):
        system.register_vehicle(f"V{i:03d}", "Z1")
        request = system.create_parking_request(f"V{i:03d}", "Z1")
        system.process_request(request.request_id)
        requests.append(request)
    
    # Rollback 2
    success, message = system.rollback_allocations(2)
    assert success == True
    
    # Check that last 2 were rolled back
    assert requests[1].allocated_slot == None
    assert requests[2].allocated_slot == None
    assert requests[0].allocated_slot != None, "First allocation should remain"
    print(f"✓ Test 9 PASSED: {message}")
    return True

def test_10_analytics_after_operations():
    """Test 10: Analytics correctness after various operations"""
    print("\n=== Test 10: Analytics Correctness ===")
    system = setup_test_system()
    
    # Create some requests
    system.register_vehicle("V001", "Z1")
    req1 = system.create_parking_request("V001", "Z1")
    system.process_request(req1.request_id)
    system.occupy_slot(req1.request_id)
    system.release_slot(req1.request_id)
    
    # Create and cancel
    system.register_vehicle("V002", "Z2")
    req2 = system.create_parking_request("V002", "Z2")
    system.process_request(req2.request_id)
    system.cancel_request(req2.request_id)
    
    analytics = system.get_analytics()
    
    assert analytics['completed_requests'] == 1, "Should have 1 completed"
    assert analytics['cancelled_requests'] == 1, "Should have 1 cancelled"
    assert analytics['total_requests'] == 2, "Should have 2 total"
    print("✓ Test 10 PASSED: Analytics correct")
    print(f"  - Completed: {analytics['completed_requests']}")
    print(f"  - Cancelled: {analytics['cancelled_requests']}")
    return True

def test_11_zone_utilization():
    """Test 11: Zone utilization calculation"""
    print("\n=== Test 11: Zone Utilization ===")
    system = setup_test_system()
    
    # Occupy some slots in Z1
    for i in range(3):
        system.register_vehicle(f"V{i:03d}", "Z1")
        request = system.create_parking_request(f"V{i:03d}", "Z1")
        system.process_request(request.request_id)
    
    analytics = system.get_analytics()
    z1_util = analytics['zone_utilization']['Z1']['utilization']
    
    # Z1 has 5 slots, 3 occupied = 60%
    assert abs(z1_util - 60.0) < 0.1, f"Z1 utilization should be 60%, got {z1_util}"
    print(f"✓ Test 11 PASSED: Z1 utilization = {z1_util:.1f}%")
    return True

def test_12_peak_usage_zone():
    """Test 12: Peak usage zone identification"""
    print("\n=== Test 12: Peak Usage Zone ===")
    system = setup_test_system()
    
    # Fill Z2 more than others
    for i in range(4):
        system.register_vehicle(f"V{i:03d}", "Z2")
        request = system.create_parking_request(f"V{i:03d}", "Z2")
        system.process_request(request.request_id)
    
    analytics = system.get_analytics()
    assert analytics['peak_usage_zone'] == "Z2", "Z2 should be peak usage zone"
    print(f"✓ Test 12 PASSED: Peak zone = {analytics['peak_usage_zone']}")
    return True

def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("SMART PARKING SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_1_slot_allocation_correctness,
        test_2_cross_zone_allocation,
        test_3_no_slots_available,
        test_4_request_lifecycle,
        test_5_invalid_state_transitions,
        test_6_cancellation_from_requested,
        test_7_cancellation_from_allocated,
        test_8_rollback_single_allocation,
        test_9_rollback_multiple_allocations,
        test_10_analytics_after_operations,
        test_11_zone_utilization,
        test_12_peak_usage_zone
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)
    
    return passed == len(tests)

if __name__ == "__main__":
    run_all_tests()
    