"""
Demo script showing programmatic usage of the Smart Parking System
"""

from parking_system import ParkingSystem
from parking_request import RequestState
import time

def print_separator():
    print("\n" + "="*60 + "\n")

def demo():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  🚗 Smart Parking System - Interactive Demo               ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # Initialize system
    print("\n📦 Initializing parking system...")
    system = ParkingSystem()
    
    # Create zones
    print("🏙️  Creating zones...")
    system.add_zone("Z1", "Downtown")
    system.add_zone("Z2", "Midtown")
    system.add_zone("Z3", "Uptown")
    
    # Add parking areas
    print("🅿️  Adding parking areas...")
    system.add_parking_area("Z1", "Z1-A1", "City Center", 3)
    system.add_parking_area("Z2", "Z2-A1", "Business District", 5)
    system.add_parking_area("Z3", "Z3-A1", "Residential", 4)
    
    # Connect zones
    print("🔗 Connecting zones...")
    system.connect_zones("Z1", "Z2")
    system.connect_zones("Z2", "Z3")
    
    # Initialize allocation engine
    system.initialize_allocation_engine()
    print("✅ System initialized!")
    
    print_separator()
    
    # Demo 1: Normal allocation
    print("📋 Demo 1: Normal Parking Request")
    print("-" * 60)
    
    system.register_vehicle("CAR-001", "Z1")
    req1 = system.create_parking_request("CAR-001", "Z1")
    print(f"✓ Created request: {req1.request_id}")
    print(f"  Vehicle: {req1.vehicle_id}")
    print(f"  Requested Zone: {req1.requested_zone}")
    print(f"  State: {req1.state.value}")
    
    success, message = system.process_request(req1.request_id)
    print(f"\n✓ Allocation: {message}")
    print(f"  Allocated Slot: {req1.allocated_slot.slot_id}")
    print(f"  Allocated Zone: {req1.allocated_zone}")
    print(f"  State: {req1.state.value}")
    
    success, message = system.occupy_slot(req1.request_id)
    print(f"\n✓ Occupation: {message}")
    print(f"  State: {req1.state.value}")
    
    print_separator()
    
    # Demo 2: Cross-zone allocation
    print("📋 Demo 2: Cross-Zone Allocation")
    print("-" * 60)
    
    # Fill up Z1
    for i in range(2):  # Fill remaining slots in Z1
        system.register_vehicle(f"CAR-{100+i}", "Z1")
        req = system.create_parking_request(f"CAR-{100+i}", "Z1")
        system.process_request(req.request_id)
    
    print("✓ Zone Z1 is now full (3/3 slots occupied)")
    
    # Try to allocate in Z1, should go to Z2
    system.register_vehicle("CAR-002", "Z1")
    req2 = system.create_parking_request("CAR-002", "Z1")
    print(f"\n✓ Created request: {req2.request_id}")
    print(f"  Requested Zone: Z1 (FULL)")
    
    success, message = system.process_request(req2.request_id)
    print(f"\n✓ Allocation: {message}")
    print(f"  Allocated Zone: {req2.allocated_zone}")
    print(f"  Cross-Zone: {req2.is_cross_zone} ⚠️")
    
    print_separator()
    
    # Demo 3: Rollback
    print("📋 Demo 3: Rollback Mechanism")
    print("-" * 60)
    
    # Create two more allocations
    for i in range(2):
        system.register_vehicle(f"CAR-{200+i}", "Z2")
        req = system.create_parking_request(f"CAR-{200+i}", "Z2")
        system.process_request(req.request_id)
        print(f"✓ Allocated: CAR-{200+i} → {req.allocated_slot.slot_id}")
    
    print(f"\n📊 Current allocations: {system.rollback_manager.get_stack_size()}")
    
    # Rollback last 2 allocations
    print("\n🔄 Rolling back last 2 allocations...")
    success, message = system.rollback_allocations(2)
    print(f"✓ {message}")
    print(f"📊 Remaining allocations: {system.rollback_manager.get_stack_size()}")
    
    print_separator()
    
    # Demo 4: Request cancellation
    print("📋 Demo 4: Request Cancellation")
    print("-" * 60)
    
    system.register_vehicle("CAR-003", "Z3")
    req3 = system.create_parking_request("CAR-003", "Z3")
    system.process_request(req3.request_id)
    
    print(f"✓ Created and allocated: {req3.request_id}")
    print(f"  State: {req3.state.value}")
    print(f"  Slot: {req3.allocated_slot.slot_id}")
    
    success, message = system.cancel_request(req3.request_id)
    print(f"\n✓ Cancellation: {message}")
    print(f"  State: {req3.state.value}")
    print(f"  Slot available: {req3.allocated_slot.is_available}")
    
    print_separator()
    
    # Demo 5: Analytics
    print("📋 Demo 5: System Analytics")
    print("-" * 60)
    
    # Release a vehicle to have completed requests
    success, message = system.release_slot(req1.request_id)
    
    analytics = system.get_analytics()
    
    print(f"📊 Total Requests: {analytics['total_requests']}")
    print(f"✅ Completed: {analytics['completed_requests']}")
    print(f"❌ Cancelled: {analytics['cancelled_requests']}")
    print(f"🔄 Active: {analytics['active_requests']}")
    print(f"🔀 Cross-Zone: {analytics['cross_zone_allocations']}")
    print(f"🏆 Peak Zone: {analytics['peak_usage_zone']}")
    
    print("\n🗺️  Zone Utilization:")
    for zone_id, data in analytics['zone_utilization'].items():
        print(f"   {zone_id} ({data['name']}): {data['utilization']:.1f}% "
              f"({data['occupied']}/{data['total']} slots)")
    
    print_separator()
    
    # Demo 6: Invalid operations
    print("📋 Demo 6: State Machine Validation")
    print("-" * 60)
    
    system.register_vehicle("CAR-004", "Z1")
    req4 = system.create_parking_request("CAR-004", "Z1")
    
    print(f"✓ Created request: {req4.request_id}")
    print(f"  Current State: {req4.state.value}")
    
    # Try to release without allocating (invalid)
    success, message = system.release_slot(req4.request_id)
    print(f"\n❌ Attempted invalid transition (REQUESTED → RELEASED)")
    print(f"  Result: {message}")
    print(f"  State remains: {req4.state.value}")
    
    print_separator()
    
    print("✅ Demo completed successfully!")
    print("\n📝 Key Features Demonstrated:")
    print("   ✓ Zone-based allocation")
    print("   ✓ Cross-zone allocation with penalty")
    print("   ✓ State machine enforcement")
    print("   ✓ Rollback mechanism")
    print("   ✓ Request cancellation")
    print("   ✓ Real-time analytics")
    print("   ✓ Invalid operation prevention")
    
    print("\n🚀 To run the web interface:")
    print("   python app.py")
    print("   Then open: http://localhost:5000")

if __name__ == "__main__":
    demo()