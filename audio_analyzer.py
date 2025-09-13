"""
Audio analysis module for detecting scam patterns and deepfake audio
"""
import numpy as np
import pandas as pd
import librosa
import pickle
import os
from typing import Dict, List, Tuple, Any, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import speech_recognition as sr
from config import Config

class AudioAnalyzer:
    def __init__(self):
        self.config = Config()
        self.recognizer = sr.Recognizer()
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.deepfake_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        self.deepfake_trained = False
        
    def extract_audio_features(self, audio_file: str = None, audio_data: np.ndarray = None, 
                             sample_rate: int = 22050) -> Dict[str, Any]:
        """Extract features from audio for scam and deepfake detection"""
        features = {}
        
        try:
            # Load audio if file path provided
            if audio_file and os.path.exists(audio_file):
                y, sr = librosa.load(audio_file, sr=sample_rate)
            elif audio_data is not None:
                y = audio_data
                sr = sample_rate
            else:
                # Return default features for mock data
                return self._get_mock_audio_features()
            
            # Basic audio features
            features['duration'] = len(y) / sr
            features['sample_rate'] = sr
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
                features[f'mfcc_{i}_std'] = np.std(mfccs[i])
            
            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            features['rolloff_mean'] = np.mean(rolloff)
            features['rolloff_std'] = np.std(rolloff)
            
            # Spectral bandwidth
            bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            features['bandwidth_mean'] = np.mean(bandwidth)
            features['bandwidth_std'] = np.std(bandwidth)
            
            # RMS energy
            rms = librosa.feature.rms(y=y)[0]
            features['rms_mean'] = np.mean(rms)
            features['rms_std'] = np.std(rms)
            
            # Pitch features (using librosa's pitch tracking)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                features['pitch_mean'] = np.mean(pitch_values)
                features['pitch_std'] = np.std(pitch_values)
                features['pitch_range'] = np.max(pitch_values) - np.min(pitch_values)
            else:
                features['pitch_mean'] = 0
                features['pitch_std'] = 0
                features['pitch_range'] = 0
            
            # Voice quality indicators
            features['voice_quality_score'] = self._calculate_voice_quality(y, sr)
            features['background_noise_level'] = self._estimate_background_noise(y)
            features['speech_rate'] = self._estimate_speech_rate(y, sr)
            features['pitch_variation'] = features['pitch_std'] / features['pitch_mean'] if features['pitch_mean'] > 0 else 0
            
            # Deepfake indicators
            features['spectral_flatness'] = np.mean(librosa.feature.spectral_flatness(y=y)[0])
            features['tonnetz'] = np.mean(librosa.feature.tonnetz(y=y, sr=sr), axis=1)
            
            # Convert tonnetz to individual features
            for i in range(6):
                features[f'tonnetz_{i}'] = features['tonnetz'][i]
            del features['tonnetz']
            
        except Exception as e:
            print(f"Error extracting audio features: {e}")
            return self._get_mock_audio_features()
        
        return features
    
    def _get_mock_audio_features(self) -> Dict[str, Any]:
        """Generate mock audio features for testing"""
        return {
            'duration': np.random.uniform(30, 600),
            'sample_rate': 22050,
            'spectral_centroid_mean': np.random.uniform(1000, 4000),
            'spectral_centroid_std': np.random.uniform(100, 500),
            'zcr_mean': np.random.uniform(0.01, 0.1),
            'zcr_std': np.random.uniform(0.005, 0.05),
            'rolloff_mean': np.random.uniform(2000, 8000),
            'rolloff_std': np.random.uniform(200, 1000),
            'bandwidth_mean': np.random.uniform(500, 2000),
            'bandwidth_std': np.random.uniform(50, 300),
            'rms_mean': np.random.uniform(0.01, 0.3),
            'rms_std': np.random.uniform(0.005, 0.1),
            'pitch_mean': np.random.uniform(100, 300),
            'pitch_std': np.random.uniform(10, 50),
            'pitch_range': np.random.uniform(50, 200),
            'voice_quality_score': np.random.uniform(0.3, 1.0),
            'background_noise_level': np.random.uniform(0.0, 0.8),
            'speech_rate': np.random.uniform(0.8, 2.0),
            'pitch_variation': np.random.uniform(0.1, 0.8),
            'spectral_flatness': np.random.uniform(0.01, 0.1),
            **{f'mfcc_{i}_mean': np.random.uniform(-20, 20) for i in range(13)},
            **{f'mfcc_{i}_std': np.random.uniform(0, 10) for i in range(13)},
            **{f'tonnetz_{i}': np.random.uniform(-1, 1) for i in range(6)}
        }
    
    def _calculate_voice_quality(self, y: np.ndarray, sr: int) -> float:
        """Calculate voice quality score"""
        try:
            # Calculate signal-to-noise ratio
            rms = librosa.feature.rms(y=y)[0]
            noise_floor = np.percentile(rms, 10)
            signal_level = np.percentile(rms, 90)
            snr = signal_level / (noise_floor + 1e-10)
            
            # Normalize to 0-1 scale
            quality_score = min(snr / 10, 1.0)
            return quality_score
        except:
            return 0.5
    
    def _estimate_background_noise(self, y: np.ndarray) -> float:
        """Estimate background noise level"""
        try:
            # Use RMS energy in quiet segments
            rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
            noise_level = np.percentile(rms, 25)  # Bottom 25% as noise estimate
            return float(noise_level)
        except:
            return 0.1
    
    def _estimate_speech_rate(self, y: np.ndarray, sr: int) -> float:
        """Estimate speech rate (words per minute)"""
        try:
            # Simple estimation based on energy peaks
            rms = librosa.feature.rms(y=y)[0]
            threshold = np.mean(rms) + 0.5 * np.std(rms)
            speech_segments = np.sum(rms > threshold)
            duration_minutes = len(y) / sr / 60
            return speech_segments / duration_minutes if duration_minutes > 0 else 1.0
        except:
            return 1.0
    
    def speech_to_text(self, audio_file: str = None, audio_data: np.ndarray = None) -> str:
        """Convert speech to text using speech recognition"""
        try:
            if audio_file and os.path.exists(audio_file):
                with sr.AudioFile(audio_file) as source:
                    audio = self.recognizer.record(source)
            elif audio_data is not None:
                # Convert numpy array to audio data
                audio = sr.AudioData(audio_data.tobytes(), 22050, 2)
            else:
                return ""
            
            # Try Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                return ""
        except Exception as e:
            print(f"Speech-to-text error: {e}")
            return ""
    
    def analyze_audio_content(self, text: str) -> Dict[str, Any]:
        """Analyze transcribed text content for scam patterns"""
        from text_analyzer import TextAnalyzer
        
        text_analyzer = TextAnalyzer()
        return text_analyzer.analyze_text(text)
    
    def detect_deepfake_audio(self, features: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Detect if audio is likely a deepfake/synthetic"""
        # Rule-based deepfake detection
        deepfake_score = 0.0
        indicators = []
        
        # Unnatural pitch variation
        if features['pitch_variation'] < 0.2:
            deepfake_score += 0.2
            indicators.append("Low pitch variation (synthetic characteristic)")
        
        # Unnatural spectral characteristics
        if features['spectral_flatness'] > 0.05:
            deepfake_score += 0.15
            indicators.append("High spectral flatness")
        
        # Poor voice quality
        if features['voice_quality_score'] < 0.4:
            deepfake_score += 0.2
            indicators.append("Poor voice quality")
        
        # Unnatural speech rate
        if features['speech_rate'] > 1.8 or features['speech_rate'] < 0.6:
            deepfake_score += 0.15
            indicators.append("Unnatural speech rate")
        
        # High background noise (common in synthetic audio)
        if features['background_noise_level'] > 0.5:
            deepfake_score += 0.1
            indicators.append("High background noise")
        
        # Unnatural MFCC patterns
        mfcc_means = [features[f'mfcc_{i}_mean'] for i in range(13)]
        mfcc_std = np.std(mfcc_means)
        if mfcc_std < 5:  # Too uniform
            deepfake_score += 0.1
            indicators.append("Unnatural MFCC patterns")
        
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
            'duration', 'spectral_centroid_mean', 'spectral_centroid_std',
            'zcr_mean', 'zcr_std', 'rolloff_mean', 'rolloff_std',
            'bandwidth_mean', 'bandwidth_std', 'rms_mean', 'rms_std',
            'pitch_mean', 'pitch_std', 'pitch_range', 'voice_quality_score',
            'background_noise_level', 'speech_rate', 'pitch_variation',
            'spectral_flatness'
        ]
        
        # Add MFCC features
        feature_names.extend([f'mfcc_{i}_mean' for i in range(13)])
        feature_names.extend([f'mfcc_{i}_std' for i in range(13)])
        feature_names.extend([f'tonnetz_{i}' for i in range(6)])
        
        return np.array([features.get(name, 0) for name in feature_names])
    
    def train_models(self, data_file: str = "data/audio_calls.csv"):
        """Train ML models on audio data"""
        if not os.path.exists(data_file):
            print(f"Data file {data_file} not found. Please generate data first.")
            return
        
        df = pd.read_csv(data_file)
        
        # Extract features for all audio samples
        features_list = []
        for _, row in df.iterrows():
            # Use mock features for training (in real scenario, you'd have actual audio files)
            features = self._get_mock_audio_features()
            # Adjust features based on row data
            features['duration'] = row['duration']
            features['voice_quality_score'] = 0.8 if row['voice_quality'] == 'good' else 0.4
            features['background_noise_level'] = row['background_noise']
            features['speech_rate'] = row['speech_rate']
            features['pitch_variation'] = row['pitch_variation']
            
            features_list.append(self._features_to_array(features))
        
        X = np.array(features_list)
        y_scam = df['is_scam'].astype(int).values
        y_deepfake = df['is_deepfake'].astype(int).values
        
        # Train scam detection model
        X_train, X_test, y_train, y_test = train_test_split(X, y_scam, test_size=0.2, random_state=42)
        self.classifier.fit(X_train, y_train)
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Scam detection model trained successfully!")
        print(f"Accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Train deepfake detection model
        X_train, X_test, y_train, y_test = train_test_split(X, y_deepfake, test_size=0.2, random_state=42)
        self.deepfake_classifier.fit(X_train, y_train)
        y_pred = self.deepfake_classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nDeepfake detection model trained successfully!")
        print(f"Accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        self.is_trained = True
        self.deepfake_trained = True
        
        # Save models
        os.makedirs(self.config.MODEL_DIR, exist_ok=True)
        with open(f"{self.config.MODEL_DIR}/audio_scam_classifier.pkl", 'wb') as f:
            pickle.dump(self.classifier, f)
        with open(f"{self.config.MODEL_DIR}/audio_deepfake_classifier.pkl", 'wb') as f:
            pickle.dump(self.deepfake_classifier, f)
        
        print(f"Models saved to {self.config.MODEL_DIR}/")
    
    def analyze_audio(self, audio_file: str = None, audio_data: np.ndarray = None, 
                     caller_id: str = None, duration: float = None) -> Dict[str, Any]:
        """Comprehensive audio analysis"""
        # Extract audio features
        features = self.extract_audio_features(audio_file, audio_data)
        
        # Speech-to-text
        transcript = self.speech_to_text(audio_file, audio_data)
        
        # Analyze content if transcript available
        content_analysis = {}
        if transcript:
            content_analysis = self.analyze_audio_content(transcript)
        
        # Detect deepfake
        deepfake_score, deepfake_info = self.detect_deepfake_audio(features)
        
        # Calculate overall scam score
        scam_score = 0.0
        
        # Audio-based scam indicators
        if features['speech_rate'] > 1.5:  # Fast speech (urgency)
            scam_score += 0.2
        if features['voice_quality_score'] < 0.5:  # Poor quality (suspicious)
            scam_score += 0.1
        if deepfake_score > 0.5:  # Likely synthetic
            scam_score += 0.3
        
        # Content-based score
        if content_analysis:
            scam_score += 0.4 * content_analysis['scam_score']
        
        # Caller ID analysis
        caller_risk = self._analyze_caller_id(caller_id) if caller_id else 0.0
        scam_score += 0.1 * caller_risk
        
        # Duration analysis
        if duration and duration < 30:  # Very short calls are suspicious
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
            "is_scam": scam_score >= self.config.AUDIO_FAKE_THRESHOLD,
            "deepfake_score": deepfake_score,
            "is_deepfake": deepfake_score >= self.config.AUDIO_FAKE_THRESHOLD,
            "transcript": transcript,
            "content_analysis": content_analysis,
            "audio_features": features,
            "deepfake_indicators": deepfake_info['indicators'],
            "recommendations": self._get_audio_recommendations(scam_score, deepfake_score, content_analysis)
        }
    
    def _analyze_caller_id(self, caller_id: str) -> float:
        """Analyze caller ID for suspicious patterns"""
        if not caller_id:
            return 0.0
        
        risk = 0.0
        
        # Check for spoofed numbers
        if caller_id.startswith('+1') and len(caller_id) > 12:
            risk += 0.3
        
        # Check for suspicious patterns
        if '000' in caller_id or '111' in caller_id:
            risk += 0.2
        
        # Check for international numbers in local context
        if caller_id.startswith('+') and not caller_id.startswith('+91'):
            risk += 0.1
        
        return min(risk, 1.0)
    
    def _get_audio_recommendations(self, scam_score: float, deepfake_score: float, 
                                 content_analysis: Dict[str, Any]) -> List[str]:
        """Get recommendations based on audio analysis"""
        recommendations = []
        
        if scam_score >= 0.7:
            recommendations.extend([
                "HANG UP immediately",
                "DO NOT provide any personal information",
                "DO NOT make any payments",
                "Block this number",
                "Report to authorities"
            ])
        elif deepfake_score >= 0.6:
            recommendations.extend([
                "This audio may be AI-generated",
                "Verify the caller's identity through official channels",
                "Be extremely cautious with any requests"
            ])
        elif scam_score >= 0.4:
            recommendations.extend([
                "Be cautious - verify caller identity",
                "Do not share sensitive information",
                "Ask for official documentation"
            ])
        
        if content_analysis and content_analysis.get('recommendations'):
            recommendations.extend(content_analysis['recommendations'])
        
        return list(set(recommendations))  # Remove duplicates

if __name__ == "__main__":
    analyzer = AudioAnalyzer()
    
    # Train models if data exists
    if os.path.exists("data/audio_calls.csv"):
        analyzer.train_models()
    
    # Test with mock data
    test_features = analyzer._get_mock_audio_features()
    deepfake_score, deepfake_info = analyzer.detect_deepfake_audio(test_features)
    
    print(f"Mock audio analysis:")
    print(f"Deepfake score: {deepfake_score:.3f}")
    print(f"Indicators: {deepfake_info['indicators']}")