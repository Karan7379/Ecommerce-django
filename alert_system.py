"""
Real-time alerting system for fraud detection
"""
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
except ImportError:
    # Fallback for Python 3.13 compatibility
    from email.mime.text import MIMEText as MimeText
    from email.mime.multipart import MIMEMultipart as MimeMultipart
import requests
from config import Config

class AlertLevel(Enum):
    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertType(Enum):
    TEXT_SCAM = "TEXT_SCAM"
    AUDIO_SCAM = "AUDIO_SCAM"
    VIDEO_SCAM = "VIDEO_SCAM"
    DEEPFAKE_AUDIO = "DEEPFAKE_AUDIO"
    DEEPFAKE_VIDEO = "DEEPFAKE_VIDEO"
    SUSPICIOUS_CALLER = "SUSPICIOUS_CALLER"
    MULTIPLE_ATTEMPTS = "MULTIPLE_ATTEMPTS"

@dataclass
class Alert:
    id: str
    timestamp: datetime
    alert_type: AlertType
    level: AlertLevel
    title: str
    message: str
    source: str
    channel: str
    scam_score: float
    is_scam: bool
    recommendations: List[str]
    metadata: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False

class AlertSystem:
    def __init__(self):
        self.config = Config()
        self.alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self.cooldown_tracker: Dict[str, datetime] = {}
        self.subscribers: List[Dict[str, Any]] = []
        self.running = False
        self.alert_thread = None
        
    def start_monitoring(self):
        """Start the alert monitoring system"""
        if not self.running:
            self.running = True
            self.alert_thread = threading.Thread(target=self._monitor_alerts, daemon=True)
            self.alert_thread.start()
            print("Alert system started")
    
    def stop_monitoring(self):
        """Stop the alert monitoring system"""
        self.running = False
        if self.alert_thread:
            self.alert_thread.join()
        print("Alert system stopped")
    
    def _monitor_alerts(self):
        """Background thread to monitor and process alerts"""
        while self.running:
            try:
                # Process pending alerts
                self._process_pending_alerts()
                
                # Clean up old alerts
                self._cleanup_old_alerts()
                
                # Check for escalation
                self._check_escalation()
                
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Alert monitoring error: {e}")
                time.sleep(5)
    
    def _process_pending_alerts(self):
        """Process alerts that need immediate attention"""
        for alert in self.alerts:
            if not alert.acknowledged and not alert.resolved:
                # Check if alert is in cooldown
                cooldown_key = f"{alert.source}_{alert.alert_type.value}"
                if cooldown_key in self.cooldown_tracker:
                    if datetime.now() - self.cooldown_tracker[cooldown_key] < timedelta(seconds=self.config.ALERT_COOLDOWN):
                        continue
                
                # Send alert
                self._send_alert(alert)
                
                # Update cooldown
                self.cooldown_tracker[cooldown_key] = datetime.now()
    
    def _cleanup_old_alerts(self):
        """Remove old alerts from memory"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]
        self.alert_history = [alert for alert in self.alert_history if alert.timestamp > cutoff_time]
    
    def _check_escalation(self):
        """Check for alerts that need escalation"""
        for alert in self.alerts:
            if not alert.acknowledged and not alert.resolved:
                # Check if alert is older than 5 minutes and still high risk
                if (datetime.now() - alert.timestamp > timedelta(minutes=5) and 
                    alert.level in [AlertLevel.HIGH, AlertLevel.CRITICAL]):
                    self._escalate_alert(alert)
    
    def _escalate_alert(self, alert: Alert):
        """Escalate an alert to higher priority"""
        if alert.level == AlertLevel.HIGH:
            alert.level = AlertLevel.CRITICAL
            alert.title = f"[ESCALATED] {alert.title}"
        elif alert.level == AlertLevel.MEDIUM:
            alert.level = AlertLevel.HIGH
            alert.title = f"[ESCALATED] {alert.title}"
        
        # Send escalated alert
        self._send_alert(alert, is_escalation=True)
    
    def create_alert(self, alert_type: AlertType, level: AlertLevel, title: str, 
                    message: str, source: str, channel: str, scam_score: float,
                    is_scam: bool, recommendations: List[str], 
                    metadata: Dict[str, Any] = None) -> Alert:
        """Create a new alert"""
        alert_id = f"{alert_type.value}_{int(time.time())}_{len(self.alerts)}"
        
        alert = Alert(
            id=alert_id,
            timestamp=datetime.now(),
            alert_type=alert_type,
            level=level,
            title=title,
            message=message,
            source=source,
            channel=channel,
            scam_score=scam_score,
            is_scam=is_scam,
            recommendations=recommendations,
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        self.alert_history.append(alert)
        
        print(f"Alert created: {alert.title} (Level: {alert.level.value})")
        return alert
    
    def _send_alert(self, alert: Alert, is_escalation: bool = False):
        """Send alert to all subscribers"""
        try:
            # Send to web interface (if available)
            self._send_web_alert(alert, is_escalation)
            
            # Send to email subscribers
            self._send_email_alert(alert, is_escalation)
            
            # Send to SMS subscribers (if configured)
            self._send_sms_alert(alert, is_escalation)
            
            # Log alert
            self._log_alert(alert, is_escalation)
            
        except Exception as e:
            print(f"Error sending alert: {e}")
    
    def _send_web_alert(self, alert: Alert, is_escalation: bool = False):
        """Send alert to web interface"""
        # This would typically send to a WebSocket or push notification service
        # For now, we'll just log it
        escalation_text = " [ESCALATED]" if is_escalation else ""
        print(f"WEB ALERT{escalation_text}: {alert.title} - {alert.message}")
    
    def _send_email_alert(self, alert: Alert, is_escalation: bool = False):
        """Send email alert to subscribers"""
        try:
            # This is a simplified email implementation
            # In production, you'd use a proper email service
            escalation_text = " [ESCALATED]" if is_escalation else ""
            
            subject = f"Fraud Alert{escalation_text}: {alert.title}"
            body = f"""
            Alert Type: {alert.alert_type.value}
            Level: {alert.level.value}
            Source: {alert.source}
            Channel: {alert.channel}
            Scam Score: {alert.scam_score:.3f}
            Timestamp: {alert.timestamp}
            
            Message: {alert.message}
            
            Recommendations:
            {chr(10).join(f"- {rec}" for rec in alert.recommendations)}
            
            Metadata: {json.dumps(alert.metadata, indent=2)}
            """
            
            # In production, you would send actual emails here
            print(f"EMAIL ALERT{escalation_text}: {subject}")
            print(f"Body: {body}")
            
        except Exception as e:
            print(f"Email alert error: {e}")
    
    def _send_sms_alert(self, alert: Alert, is_escalation: bool = False):
        """Send SMS alert to subscribers"""
        try:
            # This is a simplified SMS implementation
            # In production, you'd use a proper SMS service like Twilio
            escalation_text = " [ESCALATED]" if is_escalation else ""
            
            message = f"FRAUD ALERT{escalation_text}: {alert.title} - {alert.message[:100]}..."
            
            # In production, you would send actual SMS here
            print(f"SMS ALERT{escalation_text}: {message}")
            
        except Exception as e:
            print(f"SMS alert error: {e}")
    
    def _log_alert(self, alert: Alert, is_escalation: bool = False):
        """Log alert to file"""
        try:
            log_entry = {
                "timestamp": alert.timestamp.isoformat(),
                "alert_id": alert.id,
                "alert_type": alert.alert_type.value,
                "level": alert.level.value,
                "title": alert.title,
                "source": alert.source,
                "channel": alert.channel,
                "scam_score": alert.scam_score,
                "is_scam": alert.is_scam,
                "escalated": is_escalation
            }
            
            # In production, you'd write to a proper log file
            print(f"LOG: {json.dumps(log_entry)}")
            
        except Exception as e:
            print(f"Log error: {e}")
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                print(f"Alert {alert_id} acknowledged")
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                print(f"Alert {alert_id} resolved")
                return True
        return False
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (unresolved) alerts"""
        active_alerts = [alert for alert in self.alerts if not alert.resolved]
        return [asdict(alert) for alert in active_alerts]
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for the specified number of hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [alert for alert in self.alert_history if alert.timestamp > cutoff_time]
        return [asdict(alert) for alert in recent_alerts]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total_alerts = len(self.alert_history)
        active_alerts = len([alert for alert in self.alerts if not alert.resolved])
        acknowledged_alerts = len([alert for alert in self.alerts if alert.acknowledged])
        
        # Count by level
        level_counts = {}
        for level in AlertLevel:
            level_counts[level.value] = len([alert for alert in self.alert_history if alert.level == level])
        
        # Count by type
        type_counts = {}
        for alert_type in AlertType:
            type_counts[alert_type.value] = len([alert for alert in self.alert_history if alert.alert_type == alert_type])
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "acknowledged_alerts": acknowledged_alerts,
            "resolved_alerts": total_alerts - active_alerts,
            "level_distribution": level_counts,
            "type_distribution": type_counts,
            "system_uptime": "Running" if self.running else "Stopped"
        }
    
    def add_subscriber(self, subscriber_type: str, contact_info: str, 
                      alert_levels: List[AlertLevel] = None):
        """Add a new alert subscriber"""
        subscriber = {
            "type": subscriber_type,  # email, sms, webhook
            "contact": contact_info,
            "alert_levels": alert_levels or [AlertLevel.MEDIUM, AlertLevel.HIGH, AlertLevel.CRITICAL],
            "active": True,
            "created_at": datetime.now()
        }
        
        self.subscribers.append(subscriber)
        print(f"Subscriber added: {subscriber_type} - {contact_info}")
    
    def remove_subscriber(self, contact_info: str) -> bool:
        """Remove a subscriber"""
        for i, subscriber in enumerate(self.subscribers):
            if subscriber["contact"] == contact_info:
                del self.subscribers[i]
                print(f"Subscriber removed: {contact_info}")
                return True
        return False
    
    def create_text_scam_alert(self, text: str, sender: str, channel: str, 
                              analysis_result: Dict[str, Any]) -> Alert:
        """Create a text scam alert"""
        level = AlertLevel.HIGH if analysis_result['scam_score'] >= 0.8 else AlertLevel.MEDIUM
        title = f"Suspicious Text Message Detected"
        message = f"Scam score: {analysis_result['scam_score']:.3f}. {analysis_result['explanation']}"
        
        return self.create_alert(
            alert_type=AlertType.TEXT_SCAM,
            level=level,
            title=title,
            message=message,
            source=sender,
            channel=channel,
            scam_score=analysis_result['scam_score'],
            is_scam=analysis_result['is_scam'],
            recommendations=analysis_result['recommendations'],
            metadata={
                "text_content": text,
                "analysis_details": analysis_result
            }
        )
    
    def create_audio_scam_alert(self, caller_id: str, duration: float, 
                               analysis_result: Dict[str, Any]) -> Alert:
        """Create an audio scam alert"""
        level = AlertLevel.HIGH if analysis_result['scam_score'] >= 0.8 else AlertLevel.MEDIUM
        title = f"Suspicious Audio Call Detected"
        message = f"Scam score: {analysis_result['scam_score']:.3f}. Deepfake score: {analysis_result['deepfake_score']:.3f}"
        
        return self.create_alert(
            alert_type=AlertType.AUDIO_SCAM,
            level=level,
            title=title,
            message=message,
            source=caller_id,
            channel="audio",
            scam_score=analysis_result['scam_score'],
            is_scam=analysis_result['is_scam'],
            recommendations=analysis_result['recommendations'],
            metadata={
                "duration": duration,
                "transcript": analysis_result.get('transcript', ''),
                "analysis_details": analysis_result
            }
        )
    
    def create_video_scam_alert(self, caller_id: str, duration: float, 
                               analysis_result: Dict[str, Any]) -> Alert:
        """Create a video scam alert"""
        level = AlertLevel.HIGH if analysis_result['scam_score'] >= 0.8 else AlertLevel.MEDIUM
        title = f"Suspicious Video Call Detected"
        message = f"Scam score: {analysis_result['scam_score']:.3f}. Deepfake score: {analysis_result['deepfake_score']:.3f}"
        
        return self.create_alert(
            alert_type=AlertType.VIDEO_SCAM,
            level=level,
            title=title,
            message=message,
            source=caller_id,
            channel="video",
            scam_score=analysis_result['scam_score'],
            is_scam=analysis_result['is_scam'],
            recommendations=analysis_result['recommendations'],
            metadata={
                "duration": duration,
                "analysis_details": analysis_result
            }
        )

if __name__ == "__main__":
    # Test the alert system
    alert_system = AlertSystem()
    alert_system.start_monitoring()
    
    # Add some test subscribers
    alert_system.add_subscriber("email", "test@example.com")
    alert_system.add_subscriber("sms", "+1234567890")
    
    # Create test alerts
    test_alert = alert_system.create_alert(
        alert_type=AlertType.TEXT_SCAM,
        level=AlertLevel.HIGH,
        title="Test Scam Alert",
        message="This is a test scam alert",
        source="+1234567890",
        channel="sms",
        scam_score=0.85,
        is_scam=True,
        recommendations=["Do not respond", "Block the number"],
        metadata={"test": True}
    )
    
    # Wait a bit to see the alert processing
    time.sleep(2)
    
    # Get statistics
    stats = alert_system.get_alert_statistics()
    print(f"Alert Statistics: {json.dumps(stats, indent=2)}")
    
    # Stop the system
    alert_system.stop_monitoring()