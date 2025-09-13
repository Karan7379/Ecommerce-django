"""
Mock data generator for creating realistic scam and legitimate communication datasets
"""
import random
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

class DataGenerator:
    def __init__(self):
        self.scam_templates = [
            {
                "type": "digital_arrest",
                "template": "This is {authority} calling. We have received a complaint against you for {crime}. You need to pay {amount} immediately to avoid digital arrest. Do not disconnect this call.",
                "authorities": ["Police Department", "Cyber Crime Unit", "Income Tax Department", "Banking Security"],
                "crimes": ["money laundering", "tax evasion", "fraudulent transactions", "identity theft"],
                "amounts": ["₹50,000", "₹1,00,000", "₹2,50,000", "₹5,00,000"]
            },
            {
                "type": "banking_fraud",
                "template": "Your bank account has been compromised. To secure your account, please share your OTP {otp} and verify your identity immediately.",
                "otps": ["123456", "789012", "456789", "987654"]
            },
            {
                "type": "government_official",
                "template": "This is {official} from {department}. Your PAN card has been suspended due to suspicious activities. Pay {amount} to reactivate it within 24 hours.",
                "officials": ["Rajesh Kumar", "Priya Sharma", "Amit Singh", "Sunita Patel"],
                "departments": ["Income Tax Department", "GST Department", "PAN Card Office"],
                "amounts": ["₹25,000", "₹50,000", "₹75,000"]
            }
        ]
        
        self.legitimate_templates = [
            "Your monthly bank statement is ready. Please check your registered email for details.",
            "Your credit card payment of ₹{amount} is due on {date}. Please pay to avoid late fees.",
            "Your insurance policy renewal is due. Please contact us at {phone} for assistance.",
            "Your loan application has been approved. Please visit our branch to complete the formalities.",
            "Your account balance is ₹{amount}. Thank you for banking with us."
        ]
        
        self.phone_numbers = [
            "+91-9876543210", "+91-8765432109", "+91-7654321098", "+91-6543210987",
            "+91-5432109876", "+91-4321098765", "+91-3210987654", "+91-2109876543"
        ]
        
        self.email_domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com"
        ]
        
        self.suspicious_domains = [
            "secure-bank-verification.com", "gov-india-security.net", 
            "police-department-cyber.in", "tax-department-urgent.org"
        ]

    def generate_text_data(self, num_scam: int = 100, num_legitimate: int = 100) -> pd.DataFrame:
        """Generate mock text communication data"""
        data = []
        
        # Generate scam messages
        for i in range(num_scam):
            template = random.choice(self.scam_templates)
            if template["type"] == "digital_arrest":
                message = template["template"].format(
                    authority=random.choice(template["authorities"]),
                    crime=random.choice(template["crimes"]),
                    amount=random.choice(template["amounts"])
                )
            elif template["type"] == "banking_fraud":
                message = template["template"].format(
                    otp=random.choice(template["otps"])
                )
            elif template["type"] == "government_official":
                message = template["template"].format(
                    official=random.choice(template["officials"]),
                    department=random.choice(template["departments"]),
                    amount=random.choice(template["amounts"])
                )
            
            data.append({
                "id": f"scam_{i+1}",
                "type": "text",
                "channel": random.choice(["sms", "email", "whatsapp"]),
                "content": message,
                "sender": random.choice(self.phone_numbers) if random.choice([True, False]) else f"noreply@{random.choice(self.suspicious_domains)}",
                "timestamp": datetime.now() - timedelta(hours=random.randint(1, 24)),
                "is_scam": True,
                "scam_type": template["type"],
                "urgency_score": random.uniform(0.7, 1.0),
                "threat_score": random.uniform(0.6, 1.0)
            })
        
        # Generate legitimate messages
        for i in range(num_legitimate):
            template = random.choice(self.legitimate_templates)
            if "{amount}" in template:
                template = template.replace("{amount}", f"₹{random.randint(1000, 50000)}")
            if "{date}" in template:
                template = template.replace("{date}", (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"))
            if "{phone}" in template:
                template = template.replace("{phone}", "+91-8000000000")
            
            data.append({
                "id": f"legit_{i+1}",
                "type": "text",
                "channel": random.choice(["sms", "email", "whatsapp"]),
                "content": template,
                "sender": random.choice(self.phone_numbers) if random.choice([True, False]) else f"support@{random.choice(self.email_domains)}",
                "timestamp": datetime.now() - timedelta(hours=random.randint(1, 24)),
                "is_scam": False,
                "scam_type": None,
                "urgency_score": random.uniform(0.0, 0.3),
                "threat_score": random.uniform(0.0, 0.2)
            })
        
        return pd.DataFrame(data)

    def generate_audio_metadata(self, num_scam: int = 50, num_legitimate: int = 50) -> pd.DataFrame:
        """Generate mock audio call metadata"""
        data = []
        
        # Generate scam calls
        for i in range(num_scam):
            data.append({
                "id": f"audio_scam_{i+1}",
                "type": "audio",
                "caller_id": random.choice(self.phone_numbers),
                "duration": random.randint(30, 600),  # 30 seconds to 10 minutes
                "timestamp": datetime.now() - timedelta(hours=random.randint(1, 24)),
                "is_scam": True,
                "scam_type": random.choice(["digital_arrest", "banking_fraud", "government_official"]),
                "voice_quality": random.choice(["poor", "fair", "good"]),
                "background_noise": random.uniform(0.3, 0.8),
                "speech_rate": random.uniform(1.2, 2.0),  # Faster than normal
                "pitch_variation": random.uniform(0.1, 0.4),  # Less variation (synthetic)
                "is_deepfake": random.choice([True, False])
            })
        
        # Generate legitimate calls
        for i in range(num_legitimate):
            data.append({
                "id": f"audio_legit_{i+1}",
                "type": "audio",
                "caller_id": random.choice(self.phone_numbers),
                "duration": random.randint(60, 300),  # 1-5 minutes
                "timestamp": datetime.now() - timedelta(hours=random.randint(1, 24)),
                "is_scam": False,
                "scam_type": None,
                "voice_quality": random.choice(["good", "excellent"]),
                "background_noise": random.uniform(0.0, 0.3),
                "speech_rate": random.uniform(0.8, 1.2),  # Normal rate
                "pitch_variation": random.uniform(0.4, 0.8),  # Natural variation
                "is_deepfake": False
            })
        
        return pd.DataFrame(data)

    def generate_video_metadata(self, num_scam: int = 30, num_legitimate: int = 30) -> pd.DataFrame:
        """Generate mock video call metadata"""
        data = []
        
        # Generate scam videos
        for i in range(num_scam):
            data.append({
                "id": f"video_scam_{i+1}",
                "type": "video",
                "caller_id": random.choice(self.phone_numbers),
                "duration": random.randint(60, 300),
                "timestamp": datetime.now() - timedelta(hours=random.randint(1, 24)),
                "is_scam": True,
                "scam_type": random.choice(["digital_arrest", "government_official"]),
                "video_quality": random.choice(["poor", "fair"]),
                "lighting_consistency": random.uniform(0.2, 0.6),  # Inconsistent lighting
                "blink_rate": random.uniform(0.1, 0.3),  # Unnatural blink rate
                "lip_sync_score": random.uniform(0.3, 0.7),  # Poor lip sync
                "face_consistency": random.uniform(0.4, 0.8),  # Face inconsistencies
                "is_deepfake": random.choice([True, False])
            })
        
        # Generate legitimate videos
        for i in range(num_legitimate):
            data.append({
                "id": f"video_legit_{i+1}",
                "type": "video",
                "caller_id": random.choice(self.phone_numbers),
                "duration": random.randint(120, 600),
                "timestamp": datetime.now() - timedelta(hours=random.randint(1, 24)),
                "is_scam": False,
                "scam_type": None,
                "video_quality": random.choice(["good", "excellent"]),
                "lighting_consistency": random.uniform(0.7, 1.0),  # Consistent lighting
                "blink_rate": random.uniform(0.3, 0.5),  # Natural blink rate
                "lip_sync_score": random.uniform(0.8, 1.0),  # Good lip sync
                "face_consistency": random.uniform(0.8, 1.0),  # Consistent face
                "is_deepfake": False
            })
        
        return pd.DataFrame(data)

    def save_datasets(self, output_dir: str = "data"):
        """Generate and save all datasets"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate datasets
        text_data = self.generate_text_data()
        audio_data = self.generate_audio_metadata()
        video_data = self.generate_video_metadata()
        
        # Save to CSV
        text_data.to_csv(f"{output_dir}/text_communications.csv", index=False)
        audio_data.to_csv(f"{output_dir}/audio_calls.csv", index=False)
        video_data.to_csv(f"{output_dir}/video_calls.csv", index=False)
        
        # Create combined dataset
        combined_data = pd.concat([text_data, audio_data, video_data], ignore_index=True)
        combined_data.to_csv(f"{output_dir}/combined_communications.csv", index=False)
        
        # Save metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "total_records": len(combined_data),
            "text_records": len(text_data),
            "audio_records": len(audio_data),
            "video_records": len(video_data),
            "scam_records": len(combined_data[combined_data['is_scam'] == True]),
            "legitimate_records": len(combined_data[combined_data['is_scam'] == False])
        }
        
        with open(f"{output_dir}/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Datasets generated successfully in {output_dir}/")
        print(f"Total records: {metadata['total_records']}")
        print(f"Scam records: {metadata['scam_records']}")
        print(f"Legitimate records: {metadata['legitimate_records']}")

if __name__ == "__main__":
    generator = DataGenerator()
    generator.save_datasets()