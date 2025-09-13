"""
Flask web application for the Digital Fraud Detection System
"""
import os
import json
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
from fraud_detector import FraudDetector
from config import Config

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize fraud detector
fraud_detector = FraudDetector()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """Analyze text for scam patterns"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        sender = data.get('sender', '')
        channel = data.get('channel', 'text')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text content is required'
            }), 400
        
        result = fraud_detector.analyze_text(text, sender, channel)
        # Convert any non-serializable objects to strings
        result_str = json.dumps(result, default=str)
        return json.loads(result_str)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze/audio', methods=['POST'])
def analyze_audio():
    """Analyze audio for scam patterns"""
    try:
        data = request.get_json()
        caller_id = data.get('caller_id', '')
        duration = data.get('duration', 0)
        audio_file = data.get('audio_file')
        
        result = fraud_detector.analyze_audio(
            audio_file=audio_file,
            caller_id=caller_id,
            duration=duration
        )
        # Convert any non-serializable objects to strings
        result_str = json.dumps(result, default=str)
        return json.loads(result_str)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze/video', methods=['POST'])
def analyze_video():
    """Analyze video for scam patterns"""
    try:
        data = request.get_json()
        caller_id = data.get('caller_id', '')
        duration = data.get('duration', 0)
        video_file = data.get('video_file')
        
        result = fraud_detector.analyze_video(
            video_file=video_file,
            caller_id=caller_id,
            duration=duration
        )
        # Convert any non-serializable objects to strings
        result_str = json.dumps(result, default=str)
        return json.loads(result_str)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze/batch', methods=['POST'])
def analyze_batch():
    """Analyze batch of communications"""
    try:
        data = request.get_json()
        communications = data.get('communications', [])
        
        if not communications:
            return jsonify({
                'success': False,
                'error': 'No communications provided'
            }), 400
        
        results = []
        for comm in communications:
            result = fraud_detector.analyze_communication(comm)
            results.append(result)
        
        return jsonify({
            'success': True,
            'total_processed': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts')
def get_alerts():
    """Get all active alerts"""
    try:
        alerts = fraud_detector.get_active_alerts()
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/history')
def get_alert_history():
    """Get alert history"""
    try:
        hours = request.args.get('hours', 24, type=int)
        history = fraud_detector.alert_system.get_alert_history(hours)
        return jsonify({
            'success': True,
            'alerts': history,
            'count': len(history),
            'hours': hours
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        success = fraud_detector.acknowledge_alert(alert_id)
        return jsonify({
            'success': success,
            'message': 'Alert acknowledged' if success else 'Alert not found'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve an alert"""
    try:
        success = fraud_detector.resolve_alert(alert_id)
        return jsonify({
            'success': success,
            'message': 'Alert resolved' if success else 'Alert not found'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistics')
def get_statistics():
    """Get system statistics"""
    try:
        stats = fraud_detector.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/models/train', methods=['POST'])
def train_models():
    """Train all models"""
    try:
        data_dir = request.get_json().get('data_dir', 'data')
        results = fraud_detector.train_models(data_dir)
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/data/generate', methods=['POST'])
def generate_data():
    """Generate mock data"""
    try:
        from data_generator import DataGenerator
        generator = DataGenerator()
        generator.save_datasets()
        
        return jsonify({
            'success': True,
            'message': 'Mock data generated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/data/upload', methods=['POST'])
def upload_data():
    """Upload and analyze data file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Save uploaded file
        filename = f"uploaded_{int(time.time())}_{file.filename}"
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        
        # Analyze the file
        result = fraud_detector.batch_analyze(filepath)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': str(datetime.now() - fraud_detector.stats['start_time'])
    })

@app.route('/api/config')
def get_config():
    """Get system configuration"""
    return jsonify({
        'success': True,
        'config': {
            'text_scam_threshold': Config.TEXT_SCAM_THRESHOLD,
            'audio_fake_threshold': Config.AUDIO_FAKE_THRESHOLD,
            'video_fake_threshold': Config.VIDEO_FAKE_THRESHOLD,
            'alert_cooldown': Config.ALERT_COOLDOWN,
            'supported_formats': {
                'audio': Config.SUPPORTED_AUDIO_FORMATS,
                'video': Config.SUPPORTED_VIDEO_FORMATS,
                'image': Config.SUPPORTED_IMAGE_FORMATS
            }
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Generate mock data if it doesn't exist
    if not os.path.exists('data/text_communications.csv'):
        print("Generating mock data...")
        from data_generator import DataGenerator
        generator = DataGenerator()
        generator.save_datasets()
    
    # Train models if data exists
    if os.path.exists('data'):
        print("Training models...")
        train_results = fraud_detector.train_models()
        print(f"Training results: {train_results}")
    
    print("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)