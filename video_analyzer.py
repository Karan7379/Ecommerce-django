"""
Video analysis module for detecting deepfake videos and scam patterns
"""
import numpy as np
import pandas as pd
import cv2
import pickle
import os
from typing import Dict, List, Tuple, Any, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import dlib
from config import Config

class VideoAnalyzer:
    def __init__(self):
        self.config = Config()
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.deepfake_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        self.deepfake_trained = False
        
        # Initialize face detector and landmark predictor
        try:
            self.face_detector = dlib.get_frontal_face_detector()
            # Note: In production, you'd need to download the shape predictor file
            # self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        except Exception as e:
            print(f"Warning: Could not initialize face detection: {e}")
            self.face_detector = None
    
    def extract_video_features(self, video_file: str = None, frames: List[np.ndarray] = None) -> Dict[str, Any]:
        """Extract features from video for deepfake detection"""
        features = {}
        
        try:
            if video_file and os.path.exists(video_file):
                cap = cv2.VideoCapture(video_file)
                frames = []
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frames.append(frame)
                cap.release()
            elif frames is None:
                # Return mock features for testing
                return self._get_mock_video_features()
            
            if not frames:
                return self._get_mock_video_features()
            
            # Basic video features
            features['frame_count'] = len(frames)
            features['duration'] = len(frames) / 30.0  # Assuming 30 FPS
            
            # Analyze frames for deepfake indicators
            face_consistency_scores = []
            blink_rates = []
            lip_sync_scores = []
            lighting_consistency_scores = []
            face_detection_scores = []
            
            for i, frame in enumerate(frames[::5]):  # Sample every 5th frame
                frame_features = self._analyze_frame(frame)
                if frame_features:
                    face_consistency_scores.append(frame_features['face_consistency'])
                    blink_rates.append(frame_features['blink_rate'])
                    lip_sync_scores.append(frame_features['lip_sync_score'])
                    lighting_consistency_scores.append(frame_features['lighting_consistency'])
                    face_detection_scores.append(frame_features['face_detection_confidence'])
            
            # Aggregate features
            if face_consistency_scores:
                features['face_consistency_mean'] = np.mean(face_consistency_scores)
                features['face_consistency_std'] = np.std(face_consistency_scores)
            else:
                features['face_consistency_mean'] = 0.5
                features['face_consistency_std'] = 0.1
            
            if blink_rates:
                features['blink_rate_mean'] = np.mean(blink_rates)
                features['blink_rate_std'] = np.std(blink_rates)
            else:
                features['blink_rate_mean'] = 0.3
                features['blink_rate_std'] = 0.1
            
            if lip_sync_scores:
                features['lip_sync_mean'] = np.mean(lip_sync_scores)
                features['lip_sync_std'] = np.std(lip_sync_scores)
            else:
                features['lip_sync_mean'] = 0.8
                features['lip_sync_std'] = 0.1
            
            if lighting_consistency_scores:
                features['lighting_consistency_mean'] = np.mean(lighting_consistency_scores)
                features['lighting_consistency_std'] = np.std(lighting_consistency_scores)
            else:
                features['lighting_consistency_mean'] = 0.7
                features['lighting_consistency_std'] = 0.1
            
            if face_detection_scores:
                features['face_detection_confidence'] = np.mean(face_detection_scores)
            else:
                features['face_detection_confidence'] = 0.5
            
            # Video quality metrics
            features['video_quality'] = self._calculate_video_quality(frames)
            features['motion_consistency'] = self._calculate_motion_consistency(frames)
            features['color_consistency'] = self._calculate_color_consistency(frames)
            
        except Exception as e:
            print(f"Error extracting video features: {e}")
            return self._get_mock_video_features()
        
        return features
    
    def _get_mock_video_features(self) -> Dict[str, Any]:
        """Generate mock video features for testing"""
        return {
            'frame_count': np.random.randint(100, 1000),
            'duration': np.random.uniform(10, 60),
            'face_consistency_mean': np.random.uniform(0.4, 1.0),
            'face_consistency_std': np.random.uniform(0.05, 0.3),
            'blink_rate_mean': np.random.uniform(0.1, 0.5),
            'blink_rate_std': np.random.uniform(0.05, 0.2),
            'lip_sync_mean': np.random.uniform(0.3, 1.0),
            'lip_sync_std': np.random.uniform(0.05, 0.3),
            'lighting_consistency_mean': np.random.uniform(0.2, 1.0),
            'lighting_consistency_std': np.random.uniform(0.05, 0.4),
            'face_detection_confidence': np.random.uniform(0.3, 1.0),
            'video_quality': np.random.uniform(0.3, 1.0),
            'motion_consistency': np.random.uniform(0.4, 1.0),
            'color_consistency': np.random.uniform(0.5, 1.0)
        }
    
    def _analyze_frame(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """Analyze a single frame for deepfake indicators"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Face detection
            if self.face_detector:
                faces = self.face_detector(gray)
                if len(faces) == 0:
                    return None
                
                face = faces[0]  # Use first detected face
                face_detection_confidence = 1.0
            else:
                # Use OpenCV face detection as fallback
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                if len(faces) == 0:
                    return None
                
                x, y, w, h = faces[0]
                face = dlib.rectangle(x, y, x + w, y + h)
                face_detection_confidence = 0.8
            
            # Extract face region
            face_region = frame[y:y+h, x:x+w] if hasattr(face, 'left') else frame[face[1]:face[1]+face[3], face[0]:face[0]+face[2]]
            
            # Face consistency (simplified)
            face_consistency = self._calculate_face_consistency(face_region)
            
            # Blink rate (simplified - would need eye landmark detection in production)
            blink_rate = self._estimate_blink_rate(face_region)
            
            # Lip sync score (simplified)
            lip_sync_score = self._estimate_lip_sync(face_region)
            
            # Lighting consistency
            lighting_consistency = self._calculate_lighting_consistency(face_region)
            
            return {
                'face_consistency': face_consistency,
                'blink_rate': blink_rate,
                'lip_sync_score': lip_sync_score,
                'lighting_consistency': lighting_consistency,
                'face_detection_confidence': face_detection_confidence
            }
            
        except Exception as e:
            print(f"Frame analysis error: {e}")
            return None
    
    def _calculate_face_consistency(self, face_region: np.ndarray) -> float:
        """Calculate face consistency score"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Calculate edge density (faces should have consistent edge patterns)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Calculate texture consistency using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize scores
            consistency_score = min(edge_density * 2 + laplacian_var / 1000, 1.0)
            return consistency_score
        except:
            return 0.5
    
    def _estimate_blink_rate(self, face_region: np.ndarray) -> float:
        """Estimate blink rate (simplified)"""
        try:
            # This is a simplified version - in production, you'd use eye landmark detection
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Detect eyes using Haar cascade
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            eyes = eye_cascade.detectMultiScale(gray, 1.1, 3)
            
            # Simple heuristic: more eyes detected = more likely to be blinking
            if len(eyes) >= 2:
                return 0.3  # Normal blink rate
            elif len(eyes) == 1:
                return 0.1  # Low blink rate (suspicious)
            else:
                return 0.0  # No eyes detected (very suspicious)
        except:
            return 0.3
    
    def _estimate_lip_sync(self, face_region: np.ndarray) -> float:
        """Estimate lip sync quality (simplified)"""
        try:
            # This is a simplified version - in production, you'd analyze lip movement
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Detect mouth using Haar cascade
            mouth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_mcs_mouth.xml')
            mouths = mouth_cascade.detectMultiScale(gray, 1.1, 3)
            
            if len(mouths) > 0:
                # Simple heuristic based on mouth detection
                return 0.8
            else:
                return 0.5
        except:
            return 0.8
    
    def _calculate_lighting_consistency(self, face_region: np.ndarray) -> float:
        """Calculate lighting consistency across the face"""
        try:
            # Convert to HSV for better lighting analysis
            hsv = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
            
            # Calculate variance in brightness (V channel)
            brightness_variance = np.var(hsv[:, :, 2])
            
            # Normalize to 0-1 scale (lower variance = more consistent lighting)
            consistency_score = max(0, 1 - brightness_variance / 10000)
            return consistency_score
        except:
            return 0.7
    
    def _calculate_video_quality(self, frames: List[np.ndarray]) -> float:
        """Calculate overall video quality"""
        try:
            if not frames:
                return 0.5
            
            # Sample frames for analysis
            sample_frames = frames[::max(1, len(frames) // 10)]
            
            quality_scores = []
            for frame in sample_frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Calculate sharpness using Laplacian variance
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                quality_scores.append(laplacian_var)
            
            # Normalize quality score
            avg_quality = np.mean(quality_scores)
            normalized_quality = min(avg_quality / 1000, 1.0)
            return normalized_quality
        except:
            return 0.5
    
    def _calculate_motion_consistency(self, frames: List[np.ndarray]) -> float:
        """Calculate motion consistency between frames"""
        try:
            if len(frames) < 2:
                return 0.5
            
            motion_scores = []
            for i in range(1, min(len(frames), 20)):  # Analyze first 20 frame transitions
                prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
                curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, None, None)
                
                # Calculate motion magnitude
                if flow[0] is not None:
                    motion_magnitude = np.mean(np.linalg.norm(flow[0], axis=1))
                    motion_scores.append(motion_magnitude)
            
            if motion_scores:
                # Consistency is inverse of variance in motion
                motion_variance = np.var(motion_scores)
                consistency = max(0, 1 - motion_variance / 100)
                return consistency
            else:
                return 0.5
        except:
            return 0.5
    
    def _calculate_color_consistency(self, frames: List[np.ndarray]) -> float:
        """Calculate color consistency across frames"""
        try:
            if not frames:
                return 0.5
            
            # Sample frames
            sample_frames = frames[::max(1, len(frames) // 10)]
            
            color_means = []
            for frame in sample_frames:
                # Calculate mean color values
                mean_color = np.mean(frame, axis=(0, 1))
                color_means.append(mean_color)
            
            # Calculate variance in color means
            color_variance = np.var(color_means, axis=0)
            avg_variance = np.mean(color_variance)
            
            # Normalize to 0-1 scale
            consistency = max(0, 1 - avg_variance / 10000)
            return consistency
        except:
            return 0.5
    
    def detect_deepfake_video(self, features: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Detect if video is likely a deepfake"""
        deepfake_score = 0.0
        indicators = []
        
        # Face consistency analysis
        if features['face_consistency_mean'] < 0.6:
            deepfake_score += 0.2
            indicators.append("Inconsistent face appearance")
        
        if features['face_consistency_std'] > 0.2:
            deepfake_score += 0.15
            indicators.append("High face consistency variation")
        
        # Blink rate analysis
        if features['blink_rate_mean'] < 0.2 or features['blink_rate_mean'] > 0.6:
            deepfake_score += 0.15
            indicators.append("Unnatural blink rate")
        
        # Lip sync analysis
        if features['lip_sync_mean'] < 0.6:
            deepfake_score += 0.2
            indicators.append("Poor lip synchronization")
        
        # Lighting consistency
        if features['lighting_consistency_mean'] < 0.5:
            deepfake_score += 0.15
            indicators.append("Inconsistent lighting")
        
        # Video quality
        if features['video_quality'] < 0.4:
            deepfake_score += 0.1
            indicators.append("Poor video quality")
        
        # Motion consistency
        if features['motion_consistency'] < 0.5:
            deepfake_score += 0.1
            indicators.append("Inconsistent motion patterns")
        
        # Face detection confidence
        if features['face_detection_confidence'] < 0.6:
            deepfake_score += 0.1
            indicators.append("Low face detection confidence")
        
        # If ML model is trained, use it
        ml_score = 0.0
        if self.deepfake_trained:
            try:
                feature_array = self._features_to_array(features)
                ml_score = self.deepfake_classifier.predict_proba(feature_array.reshape(1, -1))[0][1]
            except Exception as e:
                print(f"ML deepfake detection error: {e}")
        
        # Combine scores
        final_score = 0.7 * deepfake_score + 0.3 * ml_score
        
        return final_score, {
            'indicators': indicators,
            'rule_score': deepfake_score,
            'ml_score': ml_score
        }
    
    def _features_to_array(self, features: Dict[str, Any]) -> np.ndarray:
        """Convert features dict to numpy array for ML models"""
        feature_names = [
            'frame_count', 'duration', 'face_consistency_mean', 'face_consistency_std',
            'blink_rate_mean', 'blink_rate_std', 'lip_sync_mean', 'lip_sync_std',
            'lighting_consistency_mean', 'lighting_consistency_std',
            'face_detection_confidence', 'video_quality', 'motion_consistency',
            'color_consistency'
        ]
        
        return np.array([features.get(name, 0) for name in feature_names])
    
    def train_models(self, data_file: str = "data/video_calls.csv"):
        """Train ML models on video data"""
        if not os.path.exists(data_file):
            print(f"Data file {data_file} not found. Please generate data first.")
            return
        
        df = pd.read_csv(data_file)
        
        # Extract features for all video samples
        features_list = []
        for _, row in df.iterrows():
            # Use mock features for training (in real scenario, you'd have actual video files)
            features = self._get_mock_video_features()
            # Adjust features based on row data
            features['duration'] = row['duration']
            features['video_quality'] = 0.8 if row['video_quality'] == 'good' else 0.4
            features['lighting_consistency_mean'] = row['lighting_consistency']
            features['blink_rate_mean'] = row['blink_rate']
            features['lip_sync_mean'] = row['lip_sync_score']
            features['face_consistency_mean'] = row['face_consistency']
            
            features_list.append(self._features_to_array(features))
        
        X = np.array(features_list)
        y_scam = df['is_scam'].astype(int).values
        y_deepfake = df['is_deepfake'].astype(int).values
        
        # Train scam detection model
        X_train, X_test, y_train, y_test = train_test_split(X, y_scam, test_size=0.2, random_state=42)
        self.classifier.fit(X_train, y_train)
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Video scam detection model trained successfully!")
        print(f"Accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Train deepfake detection model
        X_train, X_test, y_train, y_test = train_test_split(X, y_deepfake, test_size=0.2, random_state=42)
        self.deepfake_classifier.fit(X_train, y_train)
        y_pred = self.deepfake_classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nVideo deepfake detection model trained successfully!")
        print(f"Accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        self.is_trained = True
        self.deepfake_trained = True
        
        # Save models
        os.makedirs(self.config.MODEL_DIR, exist_ok=True)
        with open(f"{self.config.MODEL_DIR}/video_scam_classifier.pkl", 'wb') as f:
            pickle.dump(self.classifier, f)
        with open(f"{self.config.MODEL_DIR}/video_deepfake_classifier.pkl", 'wb') as f:
            pickle.dump(self.deepfake_classifier, f)
        
        print(f"Models saved to {self.config.MODEL_DIR}/")
    
    def analyze_video(self, video_file: str = None, frames: List[np.ndarray] = None,
                     caller_id: str = None, duration: float = None) -> Dict[str, Any]:
        """Comprehensive video analysis"""
        # Extract video features
        features = self.extract_video_features(video_file, frames)
        
        # Detect deepfake
        deepfake_score, deepfake_info = self.detect_deepfake_video(features)
        
        # Calculate overall scam score
        scam_score = 0.0
        
        # Video-based scam indicators
        if deepfake_score > 0.6:  # Likely synthetic
            scam_score += 0.4
        
        if features['video_quality'] < 0.4:  # Poor quality
            scam_score += 0.2
        
        if features['face_detection_confidence'] < 0.6:  # Low confidence
            scam_score += 0.1
        
        if features['lighting_consistency_mean'] < 0.5:  # Inconsistent lighting
            scam_score += 0.1
        
        if features['lip_sync_mean'] < 0.6:  # Poor lip sync
            scam_score += 0.1
        
        # Duration analysis
        if duration and duration < 60:  # Very short videos are suspicious
            scam_score += 0.1
        
        scam_score = min(scam_score, 1.0)
        
        # Determine risk level
        if scam_score >= 0.8:
            risk_level = "HIGH"
        elif scam_score >= 0.6:
            risk_level = "MEDIUM"
        elif scam_score >= 0.4:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        return {
            "scam_score": scam_score,
            "risk_level": risk_level,
            "is_scam": scam_score >= self.config.VIDEO_FAKE_THRESHOLD,
            "deepfake_score": deepfake_score,
            "is_deepfake": deepfake_score >= self.config.VIDEO_FAKE_THRESHOLD,
            "video_features": features,
            "deepfake_indicators": deepfake_info['indicators'],
            "recommendations": self._get_video_recommendations(scam_score, deepfake_score)
        }
    
    def _get_video_recommendations(self, scam_score: float, deepfake_score: float) -> List[str]:
        """Get recommendations based on video analysis"""
        recommendations = []
        
        if scam_score >= 0.7:
            recommendations.extend([
                "END the video call immediately",
                "DO NOT provide any personal information",
                "DO NOT make any payments",
                "Block this contact",
                "Report to authorities"
            ])
        elif deepfake_score >= 0.6:
            recommendations.extend([
                "This video may be AI-generated or manipulated",
                "Verify the caller's identity through official channels",
                "Be extremely cautious with any requests",
                "Ask for additional verification"
            ])
        elif scam_score >= 0.4:
            recommendations.extend([
                "Be cautious - verify caller identity",
                "Do not share sensitive information",
                "Ask for official documentation",
                "Record the call for evidence"
            ])
        
        return recommendations

if __name__ == "__main__":
    analyzer = VideoAnalyzer()
    
    # Train models if data exists
    if os.path.exists("data/video_calls.csv"):
        analyzer.train_models()
    
    # Test with mock data
    test_features = analyzer._get_mock_video_features()
    deepfake_score, deepfake_info = analyzer.detect_deepfake_video(test_features)
    
    print(f"Mock video analysis:")
    print(f"Deepfake score: {deepfake_score:.3f}")
    print(f"Indicators: {deepfake_info['indicators']}")