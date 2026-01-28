"""
Flask Backend API for Smart Parking System
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from parking_system import ParkingSystem
from datetime import datetime
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize parking system
parking_system = ParkingSystem()

# Setup initial city zones and parking areas
def initialize_system():
    """Initialize the parking system with zones and slots"""
    global parking_system
    parking_system = ParkingSystem()
    
    # Create zones
    parking_system.add_zone("Z1", "Downtown")
    parking_system.add_zone("Z2", "Midtown")
    parking_system.add_zone("Z3", "Uptown")
    parking_system.add_zone("Z4", "Suburbs")
    
    # Add parking areas
    parking_system.add_parking_area("Z1", "Z1-A1", "City Center Plaza", 10)
    parking_system.add_parking_area("Z1", "Z1-A2", "Downtown Mall", 8)
    parking_system.add_parking_area("Z2", "Z2-A1", "Midtown Square", 12)
    parking_system.add_parking_area("Z2", "Z2-A2", "Business District", 10)
    parking_system.add_parking_area("Z3", "Z3-A1", "Uptown Center", 8)
    parking_system.add_parking_area("Z3", "Z3-A2", "Residential Complex", 6)
    parking_system.add_parking_area("Z4", "Z4-A1", "Suburban Mall", 15)
    
    # Connect zones
    parking_system.connect_zones("Z1", "Z2")
    parking_system.connect_zones("Z2", "Z3")
    parking_system.connect_zones("Z3", "Z4")
    parking_system.connect_zones("Z1", "Z4")
    
    # Initialize allocation engine
    parking_system.initialize_allocation_engine()

# Initialize on startup
initialize_system()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/system/state', methods=['GET'])
def get_system_state():
    """Get current system state"""
    try:
        state = parking_system.get_system_state()
        return jsonify({
            'success': True,
            'data': state
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/analytics', methods=['GET'])
def get_analytics():
    """Get system analytics"""
    try:
        analytics = parking_system.get_analytics()
        return jsonify({
            'success': True,
            'data': analytics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/vehicle/register', methods=['POST'])
def register_vehicle():
    """Register a new vehicle"""
    try:
        data = request.json
        vehicle_id = data.get('vehicle_id')
        preferred_zone = data.get('preferred_zone')
        
        if not vehicle_id:
            return jsonify({
                'success': False,
                'error': 'Vehicle ID is required'
            }), 400
        
        vehicle = parking_system.register_vehicle(vehicle_id, preferred_zone)
        return jsonify({
            'success': True,
            'message': f'Vehicle {vehicle_id} registered successfully',
            'data': {
                'vehicle_id': vehicle.vehicle_id,
                'preferred_zone': vehicle.preferred_zone
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/request/create', methods=['POST'])
def create_request():
    """Create a parking request"""
    try:
        data = request.json
        vehicle_id = data.get('vehicle_id')
        requested_zone = data.get('requested_zone')
        
        if not vehicle_id or not requested_zone:
            return jsonify({
                'success': False,
                'error': 'Vehicle ID and requested zone are required'
            }), 400
        
        # Register vehicle if not exists
        if vehicle_id not in parking_system.vehicles:
            parking_system.register_vehicle(vehicle_id, requested_zone)
        
        parking_request = parking_system.create_parking_request(vehicle_id, requested_zone)
        
        return jsonify({
            'success': True,
            'message': 'Parking request created',
            'data': {
                'request_id': parking_request.request_id,
                'vehicle_id': parking_request.vehicle_id,
                'requested_zone': parking_request.requested_zone,
                'state': parking_request.state.value
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/request/process/<request_id>', methods=['POST'])
def process_request(request_id):
    """Process a parking request (allocate slot)"""
    try:
        success, message = parking_system.process_request(request_id)
        
        if success:
            req = parking_system.requests[request_id]
            return jsonify({
                'success': True,
                'message': message,
                'data': {
                    'request_id': req.request_id,
                    'state': req.state.value,
                    'allocated_slot': req.allocated_slot.slot_id if req.allocated_slot else None,
                    'allocated_zone': req.allocated_zone,
                    'is_cross_zone': req.is_cross_zone
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/request/occupy/<request_id>', methods=['POST'])
def occupy_slot(request_id):
    """Mark slot as occupied"""
    try:
        success, message = parking_system.occupy_slot(request_id)
        
        if success:
            req = parking_system.requests[request_id]
            return jsonify({
                'success': True,
                'message': message,
                'data': {
                    'request_id': req.request_id,
                    'state': req.state.value
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/request/release/<request_id>', methods=['POST'])
def release_slot(request_id):
    """Release a parking slot"""
    try:
        success, message = parking_system.release_slot(request_id)
        
        if success:
            req = parking_system.requests[request_id]
            return jsonify({
                'success': True,
                'message': message,
                'data': {
                    'request_id': req.request_id,
                    'state': req.state.value,
                    'parking_duration': req.get_parking_duration()
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/request/cancel/<request_id>', methods=['POST'])
def cancel_request(request_id):
    """Cancel a parking request"""
    try:
        success, message = parking_system.cancel_request(request_id)
        
        if success:
            req = parking_system.requests[request_id]
            return jsonify({
                'success': True,
                'message': message,
                'data': {
                    'request_id': req.request_id,
                    'state': req.state.value
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rollback', methods=['POST'])
def rollback():
    """Rollback last k allocations"""
    try:
        data = request.json
        k = data.get('k', 1)
        
        success, message = parking_system.rollback_allocations(k)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    """Reset the entire system"""
    try:
        initialize_system()
        return jsonify({
            'success': True,
            'message': 'System reset successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Smart Parking System Backend...")
    print("Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)