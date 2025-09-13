"""
Main fraud detection engine that coordinates all analyzers
"""
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import pandas as pd
from text_analyzer import TextAnalyzer
from audio_analyzer import AudioAnalyzer
from video_analyzer import VideoAnalyzer
from alert_system import AlertSystem, AlertLevel
from config import Config

class FraudDetector:
    def __init__(self):
        self.config = Config()
        self.text_analyzer = TextAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        self.video_analyzer = VideoAnalyzer()
        self.alert_system = AlertSystem()
        
        # Load pre-trained models if available
        self._load_models()
        
        # Start alert system
        self.alert_system.start_monitoring()
        
        # Statistics tracking
        self.stats = {
            "total_processed": 0,
            "scams_detected": 0,
            "false_positives": 0,
            "text_processed": 0,
            "audio_processed": 0,
            "video_processed": 0,
            "start_time": datetime.now()
        }
    
    def _load_models(self):
        """Load pre-trained models"""
        try:
            # Load text model
            if os.path.exists(f"{self.config.MODEL_DIR}/text_classifier.pkl"):
                self.text_analyzer.load_model()
                print("Text classifier loaded")
            
            # Load audio models
            if os.path.exists(f"{self.config.MODEL_DIR}/audio_scam_classifier.pkl"):
                with open(f"{self.config.MODEL_DIR}/audio_scam_classifier.pkl", 'rb') as f:
                    self.audio_analyzer.classifier = pickle.load(f)
                self.audio_analyzer.is_trained = True
                print("Audio scam classifier loaded")
            
            if os.path.exists(f"{self.config.MODEL_DIR}/audio_deepfake_classifier.pkl"):
                with open(f"{self.config.MODEL_DIR}/audio_deepfake_classifier.pkl", 'rb') as f:
                    self.audio_analyzer.deepfake_classifier = pickle.load(f)
                self.audio_analyzer.deepfake_trained = True
                print("Audio deepfake classifier loaded")
            
            # Load video models
            if os.path.exists(f"{self.config.MODEL_DIR}/video_scam_classifier.pkl"):
                with open(f"{self.config.MODEL_DIR}/video_scam_classifier.pkl", 'rb') as f:
                    self.video_analyzer.classifier = pickle.load(f)
                self.video_analyzer.is_trained = True
                print("Video scam classifier loaded")
            
            if os.path.exists(f"{self.config.MODEL_DIR}/video_deepfake_classifier.pkl"):
                with open(f"{self.config.MODEL_DIR}/video_deepfake_classifier.pkl", 'rb') as f:
                    self.video_analyzer.deepfake_classifier = pickle.load(f)
                self.video_analyzer.deepfake_trained = True
                print("Video deepfake classifier loaded")
                
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def analyze_text(self, text: str, sender: str = None, channel: str = "text") -> Dict[str, Any]:
        """Analyze text for scam patterns"""
        try:
            # Analyze text
            analysis_result = self.text_analyzer.analyze_text(text)
            
            # Update statistics
            self.stats["total_processed"] += 1
            self.stats["text_processed"] += 1
            if analysis_result["is_scam"]:
                self.stats["scams_detected"] += 1
            
            # Create alert if scam detected
            if analysis_result["is_scam"]:
                alert = self.alert_system.create_text_scam_alert(
                    text=text,
                    sender=sender or "unknown",
                    channel=channel,
                    analysis_result=analysis_result
                )
                analysis_result["alert_id"] = alert.id
            
            return {
                "success": True,
                "type": "text",
                "analysis": analysis_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "text",
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_audio(self, audio_file: str = None, audio_data: bytes = None,
                     caller_id: str = None, duration: float = None) -> Dict[str, Any]:
        """Analyze audio for scam patterns and deepfake detection"""
        try:
            # Convert bytes to numpy array if needed
            audio_np = None
            if audio_data:
                import numpy as np
                audio_np = np.frombuffer(audio_data, dtype=np.int16)
            
            # Analyze audio
            analysis_result = self.audio_analyzer.analyze_audio(
                audio_file=audio_file,
                audio_data=audio_np,
                caller_id=caller_id,
                duration=duration
            )
            
            # Update statistics
            self.stats["total_processed"] += 1
            self.stats["audio_processed"] += 1
            if analysis_result["is_scam"]:
                self.stats["scams_detected"] += 1
            
            # Create alert if scam detected
            if analysis_result["is_scam"]:
                alert = self.alert_system.create_audio_scam_alert(
                    caller_id=caller_id or "unknown",
                    duration=duration or 0,
                    analysis_result=analysis_result
                )
                analysis_result["alert_id"] = alert.id
            
            return {
                "success": True,
                "type": "audio",
                "analysis": analysis_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "audio",
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_video(self, video_file: str = None, video_data: bytes = None,
                     caller_id: str = None, duration: float = None) -> Dict[str, Any]:
        """Analyze video for scam patterns and deepfake detection"""
        try:
            # Convert bytes to frames if needed
            frames = None
            if video_data:
                import cv2
                import numpy as np
                # This is a simplified conversion - in production you'd use proper video decoding
                frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)]
            
            # Analyze video
            analysis_result = self.video_analyzer.analyze_video(
                video_file=video_file,
                frames=frames,
                caller_id=caller_id,
                duration=duration
            )
            
            # Update statistics
            self.stats["total_processed"] += 1
            self.stats["video_processed"] += 1
            if analysis_result["is_scam"]:
                self.stats["scams_detected"] += 1
            
            # Create alert if scam detected
            if analysis_result["is_scam"]:
                alert = self.alert_system.create_video_scam_alert(
                    caller_id=caller_id or "unknown",
                    duration=duration or 0,
                    analysis_result=analysis_result
                )
                analysis_result["alert_id"] = alert.id
            
            return {
                "success": True,
                "type": "video",
                "analysis": analysis_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "video",
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_communication(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze communication data (text, audio, or video)"""
        comm_type = data.get("type", "text")
        
        if comm_type == "text":
            return self.analyze_text(
                text=data.get("content", ""),
                sender=data.get("sender"),
                channel=data.get("channel", "text")
            )
        elif comm_type == "audio":
            return self.analyze_audio(
                audio_file=data.get("audio_file"),
                audio_data=data.get("audio_data"),
                caller_id=data.get("caller_id"),
                duration=data.get("duration")
            )
        elif comm_type == "video":
            return self.analyze_video(
                video_file=data.get("video_file"),
                video_data=data.get("video_data"),
                caller_id=data.get("caller_id"),
                duration=data.get("duration")
            )
        else:
            return {
                "success": False,
                "error": f"Unsupported communication type: {comm_type}",
                "timestamp": datetime.now().isoformat()
            }
    
    def batch_analyze(self, data_file: str) -> Dict[str, Any]:
        """Analyze a batch of communications from a CSV file"""
        try:
            if not os.path.exists(data_file):
                return {
                    "success": False,
                    "error": f"Data file not found: {data_file}",
                    "timestamp": datetime.now().isoformat()
                }
            
            df = pd.read_csv(data_file)
            results = []
            
            for _, row in df.iterrows():
                # Convert row to communication data format
                comm_data = {
                    "type": row.get("type", "text"),
                    "content": row.get("content", ""),
                    "sender": row.get("sender"),
                    "caller_id": row.get("caller_id"),
                    "channel": row.get("channel", "unknown"),
                    "duration": row.get("duration")
                }
                
                # Analyze communication
                result = self.analyze_communication(comm_data)
                results.append(result)
            
            return {
                "success": True,
                "total_processed": len(results),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        uptime = datetime.now() - self.stats["start_time"]
        
        return {
            "system_stats": self.stats,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_human": str(uptime),
            "alert_stats": self.alert_system.get_alert_statistics(),
            "model_status": {
                "text_trained": self.text_analyzer.is_trained,
                "audio_trained": self.audio_analyzer.is_trained,
                "audio_deepfake_trained": self.audio_analyzer.deepfake_trained,
                "video_trained": self.video_analyzer.is_trained,
                "video_deepfake_trained": self.video_analyzer.deepfake_trained
            }
        }
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return self.alert_system.get_active_alerts()
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        return self.alert_system.acknowledge_alert(alert_id)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        return self.alert_system.resolve_alert(alert_id)
    
    def train_models(self, data_dir: str = "data"):
        """Train all models on available data"""
        results = {}
        
        # Train text model
        text_file = f"{data_dir}/text_communications.csv"
        if os.path.exists(text_file):
            try:
                self.text_analyzer.train_model(text_file)
                results["text"] = "success"
            except Exception as e:
                results["text"] = f"error: {e}"
        else:
            results["text"] = "no data file"
        
        # Train audio models
        audio_file = f"{data_dir}/audio_calls.csv"
        if os.path.exists(audio_file):
            try:
                self.audio_analyzer.train_models(audio_file)
                results["audio"] = "success"
            except Exception as e:
                results["audio"] = f"error: {e}"
        else:
            results["audio"] = "no data file"
        
        # Train video models
        video_file = f"{data_dir}/video_calls.csv"
        if os.path.exists(video_file):
            try:
                self.video_analyzer.train_models(video_file)
                results["video"] = "success"
            except Exception as e:
                results["video"] = f"error: {e}"
        else:
            results["video"] = "no data file"
        
        return results
    
    def shutdown(self):
        """Shutdown the fraud detection system"""
        self.alert_system.stop_monitoring()
        print("Fraud detection system shutdown complete")

if __name__ == "__main__":
    # Initialize fraud detector
    detector = FraudDetector()
    
    # Train models if data exists
    if os.path.exists("data"):
        print("Training models...")
        train_results = detector.train_models()
        print(f"Training results: {train_results}")
    
    # Test with sample data
    print("\nTesting text analysis...")
    text_result = detector.analyze_text(
        "Your bank account has been compromised. Please share your OTP 123456 immediately to secure it.",
        sender="+1234567890",
        channel="sms"
    )
    print(f"Text analysis result: {json.dumps(text_result, indent=2, default=str)}")
    
    print("\nTesting audio analysis...")
    audio_result = detector.analyze_audio(
        caller_id="+1234567890",
        duration=120
    )
    print(f"Audio analysis result: {json.dumps(audio_result, indent=2, default=str)}")
    
    print("\nTesting video analysis...")
    video_result = detector.analyze_video(
        caller_id="+1234567890",
        duration=180
    )
    print(f"Video analysis result: {json.dumps(video_result, indent=2, default=str)}")
    
    # Get statistics
    print("\nSystem statistics:")
    stats = detector.get_statistics()
    print(json.dumps(stats, indent=2, default=str))
    
    # Get active alerts
    print("\nActive alerts:")
    alerts = detector.get_active_alerts()
    print(json.dumps(alerts, indent=2, default=str))
    
    # Shutdown
    detector.shutdown()