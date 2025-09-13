"""
Configuration settings for the Digital Fraud Detection System
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Model paths
    MODEL_DIR = 'models'
    DATA_DIR = 'data'
    
    # Detection thresholds
    TEXT_SCAM_THRESHOLD = 0.7
    AUDIO_FAKE_THRESHOLD = 0.6
    VIDEO_FAKE_THRESHOLD = 0.5
    
    # Alert settings
    ALERT_COOLDOWN = 300  # 5 minutes in seconds
    
    # Supported file types
    SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.m4a', '.flac']
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv']
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp']
    
    # Scam keywords and patterns
    SCAM_KEYWORDS = [
        'arrest warrant', 'digital arrest', 'police', 'court', 'legal action',
        'immediate payment', 'urgent', 'verify identity', 'suspended account',
        'fraud alert', 'security breach', 'confirm details', 'OTP', 'verification code',
        'government official', 'tax department', 'banking security', 'freeze account',
        'criminal charges', 'warrant', 'bail', 'fine', 'penalty'
    ]
    
    URGENCY_KEYWORDS = [
        'immediately', 'urgent', 'asap', 'right now', 'within hours',
        'deadline', 'expires', 'last chance', 'final notice'
    ]
    
    THREAT_KEYWORDS = [
        'arrest', 'jail', 'prison', 'legal action', 'criminal charges',
        'warrant', 'court', 'police', 'authorities', 'investigation'
    ]