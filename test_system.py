#!/usr/bin/env python3
"""
Test script for the Digital Fraud Detection System
"""
import os
import sys
import json
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import numpy as np
        import pandas as pd
        import sklearn
        import nltk
        import flask
        import librosa
        import cv2
        print("✓ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_data_generation():
    """Test data generation"""
    print("\nTesting data generation...")
    try:
        from data_generator import DataGenerator
        generator = DataGenerator()
        
        # Generate small test dataset
        text_data = generator.generate_text_data(num_scam=5, num_legitimate=5)
        audio_data = generator.generate_audio_metadata(num_scam=3, num_legitimate=3)
        video_data = generator.generate_video_metadata(num_scam=2, num_legitimate=2)
        
        print(f"✓ Generated {len(text_data)} text samples")
        print(f"✓ Generated {len(audio_data)} audio samples")
        print(f"✓ Generated {len(video_data)} video samples")
        return True
    except Exception as e:
        print(f"✗ Data generation error: {e}")
        return False

def test_text_analyzer():
    """Test text analysis"""
    print("\nTesting text analyzer...")
    try:
        from text_analyzer import TextAnalyzer
        analyzer = TextAnalyzer()
        
        # Test with scam text
        scam_text = "Your bank account has been compromised. Please share your OTP 123456 immediately to secure it."
        result = analyzer.analyze_text(scam_text)
        
        print(f"✓ Scam text analysis: Score={result['scam_score']:.3f}, Risk={result['risk_level']}")
        
        # Test with legitimate text
        legit_text = "Your monthly bank statement is ready. Please check your registered email for details."
        result = analyzer.analyze_text(legit_text)
        
        print(f"✓ Legitimate text analysis: Score={result['scam_score']:.3f}, Risk={result['risk_level']}")
        return True
    except Exception as e:
        print(f"✗ Text analyzer error: {e}")
        return False

def test_audio_analyzer():
    """Test audio analysis"""
    print("\nTesting audio analyzer...")
    try:
        from audio_analyzer import AudioAnalyzer
        analyzer = AudioAnalyzer()
        
        # Test with mock audio data
        result = analyzer.analyze_audio(caller_id="+1234567890", duration=120)
        
        print(f"✓ Audio analysis: Score={result['scam_score']:.3f}, Risk={result['risk_level']}")
        print(f"✓ Deepfake score: {result['deepfake_score']:.3f}")
        return True
    except Exception as e:
        print(f"✗ Audio analyzer error: {e}")
        return False

def test_video_analyzer():
    """Test video analysis"""
    print("\nTesting video analyzer...")
    try:
        from video_analyzer import VideoAnalyzer
        analyzer = VideoAnalyzer()
        
        # Test with mock video data
        result = analyzer.analyze_video(caller_id="+1234567890", duration=180)
        
        print(f"✓ Video analysis: Score={result['scam_score']:.3f}, Risk={result['risk_level']}")
        print(f"✓ Deepfake score: {result['deepfake_score']:.3f}")
        return True
    except Exception as e:
        print(f"✗ Video analyzer error: {e}")
        return False

def test_alert_system():
    """Test alert system"""
    print("\nTesting alert system...")
    try:
        from alert_system import AlertSystem, AlertType, AlertLevel
        alert_system = AlertSystem()
        
        # Create test alert
        alert = alert_system.create_alert(
            alert_type=AlertType.TEXT_SCAM,
            level=AlertLevel.HIGH,
            title="Test Scam Alert",
            message="This is a test scam alert",
            source="+1234567890",
            channel="sms",
            scam_score=0.85,
            is_scam=True,
            recommendations=["Do not respond", "Block the number"]
        )
        
        print(f"✓ Alert created: {alert.id}")
        
        # Test statistics
        stats = alert_system.get_alert_statistics()
        print(f"✓ Alert statistics: {stats['total_alerts']} total alerts")
        
        alert_system.stop_monitoring()
        return True
    except Exception as e:
        print(f"✗ Alert system error: {e}")
        return False

def test_fraud_detector():
    """Test main fraud detector"""
    print("\nTesting fraud detector...")
    try:
        from fraud_detector import FraudDetector
        detector = FraudDetector()
        
        # Test text analysis
        text_result = detector.analyze_text(
            "Your bank account has been compromised. Please share your OTP 123456 immediately.",
            sender="+1234567890",
            channel="sms"
        )
        
        print(f"✓ Text analysis: Success={text_result['success']}")
        
        # Test audio analysis
        audio_result = detector.analyze_audio(
            caller_id="+1234567890",
            duration=120
        )
        
        print(f"✓ Audio analysis: Success={audio_result['success']}")
        
        # Test video analysis
        video_result = detector.analyze_video(
            caller_id="+1234567890",
            duration=180
        )
        
        print(f"✓ Video analysis: Success={video_result['success']}")
        
        # Test statistics
        stats = detector.get_statistics()
        print(f"✓ System statistics: {stats['system_stats']['total_processed']} processed")
        
        detector.shutdown()
        return True
    except Exception as e:
        print(f"✗ Fraud detector error: {e}")
        return False

def test_explainability():
    """Test explainability engine"""
    print("\nTesting explainability engine...")
    try:
        from explainability import ExplainabilityEngine
        engine = ExplainabilityEngine()
        
        # Test text explanation
        test_analysis = {
            "scam_score": 0.85,
            "risk_level": "HIGH",
            "is_scam": True,
            "features": {
                "scam_keyword_count": 2,
                "urgency_keyword_count": 1,
                "sentiment_negative": 0.3,
                "found_scam_keywords": ["bank account", "compromised"]
            },
            "recommendations": ["Do not share OTP", "Contact bank directly"]
        }
        
        explanation = engine.generate_explanation_report("text", test_analysis, "Test text")
        
        print(f"✓ Text explanation generated")
        print(f"  - Overview: {explanation['overview']['scam_score']:.3f} score")
        print(f"  - Keywords: {len(explanation['keyword_analysis']['scam_keywords']['found'])} found")
        print(f"  - Confidence: {explanation['confidence_metrics']['overall_confidence']:.3f}")
        
        return True
    except Exception as e:
        print(f"✗ Explainability engine error: {e}")
        return False

def test_web_app():
    """Test web application"""
    print("\nTesting web application...")
    try:
        from app import app
        
        # Test app creation
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✓ Health endpoint working")
            else:
                print(f"✗ Health endpoint failed: {response.status_code}")
                return False
            
            # Test statistics endpoint
            response = client.get('/api/statistics')
            if response.status_code == 200:
                print("✓ Statistics endpoint working")
            else:
                print(f"✗ Statistics endpoint failed: {response.status_code}")
                return False
            
            # Test text analysis endpoint
            response = client.post('/api/analyze/text', 
                                 json={'text': 'Test message', 'sender': '+1234567890', 'channel': 'sms'})
            if response.status_code == 200:
                print("✓ Text analysis endpoint working")
            else:
                print(f"✗ Text analysis endpoint failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Web application error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Digital Fraud Detection System - Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_data_generation,
        test_text_analyzer,
        test_audio_analyzer,
        test_video_analyzer,
        test_alert_system,
        test_fraud_detector,
        test_explainability,
        test_web_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nTo start the system:")
        print("1. Generate data: python data_generator.py")
        print("2. Train models: python -c \"from fraud_detector import FraudDetector; FraudDetector().train_models()\"")
        print("3. Start web app: python app.py")
        print("4. Open browser: http://localhost:5000")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())