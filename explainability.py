"""
Explainability module for providing detailed explanations of fraud detection decisions
"""
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from config import Config

class ExplainabilityEngine:
    def __init__(self):
        self.config = Config()
        
    def explain_text_analysis(self, text: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed explanation for text analysis"""
        explanation = {
            "overview": {
                "text_length": len(text),
                "word_count": len(text.split()),
                "scam_score": analysis_result.get("scam_score", 0),
                "risk_level": analysis_result.get("risk_level", "MINIMAL"),
                "is_scam": analysis_result.get("is_scam", False)
            },
            "feature_analysis": {},
            "keyword_analysis": {},
            "sentiment_analysis": {},
            "pattern_analysis": {},
            "recommendations": analysis_result.get("recommendations", []),
            "confidence_metrics": {},
            "visualizations": {}
        }
        
        features = analysis_result.get("features", {})
        
        # Feature analysis
        explanation["feature_analysis"] = {
            "text_characteristics": {
                "length": features.get("length", 0),
                "word_count": features.get("word_count", 0),
                "sentence_count": features.get("sentence_count", 0),
                "avg_word_length": features.get("avg_word_length", 0),
                "uppercase_ratio": features.get("uppercase_ratio", 0)
            },
            "punctuation_analysis": {
                "exclamation_count": features.get("exclamation_count", 0),
                "question_count": features.get("question_count", 0),
                "exclamation_ratio": features.get("exclamation_ratio", 0)
            },
            "content_indicators": {
                "has_phone": features.get("has_phone", 0),
                "has_email": features.get("has_email", 0),
                "has_url": features.get("has_url", 0),
                "has_currency": features.get("has_currency", 0)
            }
        }
        
        # Keyword analysis
        explanation["keyword_analysis"] = {
            "scam_keywords": {
                "found": features.get("found_scam_keywords", []),
                "count": features.get("scam_keyword_count", 0),
                "ratio": features.get("scam_keyword_ratio", 0)
            },
            "urgency_keywords": {
                "found": features.get("found_urgency_keywords", []),
                "count": features.get("urgency_keyword_count", 0)
            },
            "threat_keywords": {
                "found": features.get("found_threat_keywords", []),
                "count": features.get("threat_keyword_count", 0)
            }
        }
        
        # Sentiment analysis
        explanation["sentiment_analysis"] = {
            "compound_score": features.get("sentiment_compound", 0),
            "negative_score": features.get("sentiment_negative", 0),
            "neutral_score": features.get("sentiment_neutral", 0),
            "positive_score": features.get("sentiment_positive", 0),
            "interpretation": self._interpret_sentiment(features.get("sentiment_compound", 0))
        }
        
        # Pattern analysis
        explanation["pattern_analysis"] = {
            "repetition_score": features.get("repetition_score", 0),
            "suspicious_patterns": self._identify_suspicious_patterns(text, features),
            "linguistic_anomalies": self._identify_linguistic_anomalies(text, features)
        }
        
        # Confidence metrics
        explanation["confidence_metrics"] = {
            "feature_confidence": self._calculate_feature_confidence(features),
            "model_confidence": self._calculate_model_confidence(analysis_result),
            "overall_confidence": self._calculate_overall_confidence(analysis_result)
        }
        
        # Generate visualizations
        explanation["visualizations"] = self._generate_text_visualizations(text, features, analysis_result)
        
        return explanation
    
    def explain_audio_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed explanation for audio analysis"""
        explanation = {
            "overview": {
                "scam_score": analysis_result.get("scam_score", 0),
                "deepfake_score": analysis_result.get("deepfake_score", 0),
                "risk_level": analysis_result.get("risk_level", "MINIMAL"),
                "is_scam": analysis_result.get("is_scam", False),
                "is_deepfake": analysis_result.get("is_deepfake", False)
            },
            "audio_features": {},
            "deepfake_indicators": {},
            "content_analysis": {},
            "quality_metrics": {},
            "confidence_metrics": {},
            "visualizations": {}
        }
        
        features = analysis_result.get("audio_features", {})
        content_analysis = analysis_result.get("content_analysis", {})
        
        # Audio features
        explanation["audio_features"] = {
            "duration": features.get("duration", 0),
            "voice_quality": {
                "score": features.get("voice_quality_score", 0),
                "interpretation": self._interpret_voice_quality(features.get("voice_quality_score", 0))
            },
            "speech_characteristics": {
                "rate": features.get("speech_rate", 0),
                "pitch_mean": features.get("pitch_mean", 0),
                "pitch_variation": features.get("pitch_variation", 0)
            },
            "acoustic_properties": {
                "spectral_centroid": features.get("spectral_centroid_mean", 0),
                "zero_crossing_rate": features.get("zcr_mean", 0),
                "spectral_flatness": features.get("spectral_flatness", 0)
            }
        }
        
        # Deepfake indicators
        explanation["deepfake_indicators"] = {
            "indicators": analysis_result.get("deepfake_indicators", []),
            "synthetic_characteristics": self._analyze_synthetic_characteristics(features),
            "natural_vs_synthetic": self._compare_natural_vs_synthetic(features)
        }
        
        # Content analysis (if transcript available)
        if content_analysis:
            explanation["content_analysis"] = {
                "transcript": content_analysis.get("transcript", ""),
                "scam_score": content_analysis.get("scam_score", 0),
                "explanation": content_analysis.get("explanation", ""),
                "found_keywords": content_analysis.get("features", {}).get("found_scam_keywords", [])
            }
        
        # Quality metrics
        explanation["quality_metrics"] = {
            "background_noise": features.get("background_noise_level", 0),
            "signal_quality": self._assess_signal_quality(features),
            "clarity_score": self._calculate_clarity_score(features)
        }
        
        # Confidence metrics
        explanation["confidence_metrics"] = {
            "audio_confidence": self._calculate_audio_confidence(features),
            "deepfake_confidence": self._calculate_deepfake_confidence(analysis_result),
            "overall_confidence": self._calculate_overall_confidence(analysis_result)
        }
        
        # Generate visualizations
        explanation["visualizations"] = self._generate_audio_visualizations(features, analysis_result)
        
        return explanation
    
    def explain_video_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed explanation for video analysis"""
        explanation = {
            "overview": {
                "scam_score": analysis_result.get("scam_score", 0),
                "deepfake_score": analysis_result.get("deepfake_score", 0),
                "risk_level": analysis_result.get("risk_level", "MINIMAL"),
                "is_scam": analysis_result.get("is_scam", False),
                "is_deepfake": analysis_result.get("is_deepfake", False)
            },
            "video_features": {},
            "deepfake_indicators": {},
            "quality_metrics": {},
            "temporal_analysis": {},
            "confidence_metrics": {},
            "visualizations": {}
        }
        
        features = analysis_result.get("video_features", {})
        
        # Video features
        explanation["video_features"] = {
            "basic_properties": {
                "frame_count": features.get("frame_count", 0),
                "duration": features.get("duration", 0),
                "video_quality": features.get("video_quality", 0)
            },
            "face_analysis": {
                "consistency_mean": features.get("face_consistency_mean", 0),
                "consistency_std": features.get("face_consistency_std", 0),
                "detection_confidence": features.get("face_detection_confidence", 0)
            },
            "behavioral_analysis": {
                "blink_rate": features.get("blink_rate_mean", 0),
                "lip_sync_score": features.get("lip_sync_mean", 0),
                "interpretation": self._interpret_behavioral_indicators(features)
            }
        }
        
        # Deepfake indicators
        explanation["deepfake_indicators"] = {
            "indicators": analysis_result.get("deepfake_indicators", []),
            "manipulation_signs": self._identify_manipulation_signs(features),
            "synthetic_characteristics": self._analyze_video_synthetic_characteristics(features)
        }
        
        # Quality metrics
        explanation["quality_metrics"] = {
            "lighting_consistency": features.get("lighting_consistency_mean", 0),
            "motion_consistency": features.get("motion_consistency", 0),
            "color_consistency": features.get("color_consistency", 0),
            "overall_quality": self._assess_video_quality(features)
        }
        
        # Temporal analysis
        explanation["temporal_analysis"] = {
            "consistency_over_time": self._analyze_temporal_consistency(features),
            "anomaly_detection": self._detect_temporal_anomalies(features),
            "stability_metrics": self._calculate_stability_metrics(features)
        }
        
        # Confidence metrics
        explanation["confidence_metrics"] = {
            "video_confidence": self._calculate_video_confidence(features),
            "deepfake_confidence": self._calculate_deepfake_confidence(analysis_result),
            "overall_confidence": self._calculate_overall_confidence(analysis_result)
        }
        
        # Generate visualizations
        explanation["visualizations"] = self._generate_video_visualizations(features, analysis_result)
        
        return explanation
    
    def _interpret_sentiment(self, compound_score: float) -> str:
        """Interpret sentiment compound score"""
        if compound_score >= 0.05:
            return "Positive sentiment"
        elif compound_score <= -0.05:
            return "Negative sentiment (suspicious for scams)"
        else:
            return "Neutral sentiment"
    
    def _interpret_voice_quality(self, quality_score: float) -> str:
        """Interpret voice quality score"""
        if quality_score >= 0.8:
            return "High quality, natural voice"
        elif quality_score >= 0.6:
            return "Good quality voice"
        elif quality_score >= 0.4:
            return "Fair quality, some distortion"
        else:
            return "Poor quality, possible synthetic or heavily processed"
    
    def _interpret_behavioral_indicators(self, features: Dict[str, Any]) -> Dict[str, str]:
        """Interpret behavioral indicators in video"""
        blink_rate = features.get("blink_rate_mean", 0.3)
        lip_sync = features.get("lip_sync_mean", 0.8)
        
        interpretations = {}
        
        if blink_rate < 0.2:
            interpretations["blink_rate"] = "Unnaturally low blink rate (synthetic characteristic)"
        elif blink_rate > 0.6:
            interpretations["blink_rate"] = "Unnaturally high blink rate (possible manipulation)"
        else:
            interpretations["blink_rate"] = "Normal blink rate"
        
        if lip_sync < 0.6:
            interpretations["lip_sync"] = "Poor lip synchronization (deepfake indicator)"
        elif lip_sync < 0.8:
            interpretations["lip_sync"] = "Moderate lip synchronization"
        else:
            interpretations["lip_sync"] = "Good lip synchronization"
        
        return interpretations
    
    def _identify_suspicious_patterns(self, text: str, features: Dict[str, Any]) -> List[str]:
        """Identify suspicious patterns in text"""
        patterns = []
        
        # Check for excessive punctuation
        if features.get("exclamation_ratio", 0) > 0.1:
            patterns.append("Excessive use of exclamation marks (urgency indicator)")
        
        # Check for repetition
        if features.get("repetition_score", 0) > 0.3:
            patterns.append("High word repetition (possible template message)")
        
        # Check for uppercase usage
        if features.get("uppercase_ratio", 0) > 0.3:
            patterns.append("Excessive use of uppercase letters (shouting/urgency)")
        
        # Check for phone/email in suspicious context
        if features.get("has_phone", 0) and features.get("scam_keyword_count", 0) > 0:
            patterns.append("Phone number mentioned with scam keywords")
        
        if features.get("has_currency", 0) and features.get("urgency_keyword_count", 0) > 0:
            patterns.append("Currency amount with urgency indicators")
        
        return patterns
    
    def _identify_linguistic_anomalies(self, text: str, features: Dict[str, Any]) -> List[str]:
        """Identify linguistic anomalies"""
        anomalies = []
        
        # Check for unusual sentence structure
        if features.get("sentence_count", 0) > 0:
            avg_words_per_sentence = features.get("word_count", 0) / features.get("sentence_count", 1)
            if avg_words_per_sentence > 25:
                anomalies.append("Unusually long sentences (possible template)")
            elif avg_words_per_sentence < 3:
                anomalies.append("Unusually short sentences (possible urgency)")
        
        # Check for unusual word length
        if features.get("avg_word_length", 0) > 8:
            anomalies.append("Unusually long words (possible obfuscation)")
        
        return anomalies
    
    def _analyze_synthetic_characteristics(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze characteristics that suggest synthetic audio"""
        characteristics = {}
        
        # Pitch variation
        pitch_variation = features.get("pitch_variation", 0)
        if pitch_variation < 0.2:
            characteristics["pitch_variation"] = "Low pitch variation (synthetic characteristic)"
        elif pitch_variation > 0.8:
            characteristics["pitch_variation"] = "High pitch variation (natural characteristic)"
        else:
            characteristics["pitch_variation"] = "Normal pitch variation"
        
        # Speech rate
        speech_rate = features.get("speech_rate", 1.0)
        if speech_rate > 1.8:
            characteristics["speech_rate"] = "Unnaturally fast speech (suspicious)"
        elif speech_rate < 0.6:
            characteristics["speech_rate"] = "Unnaturally slow speech (suspicious)"
        else:
            characteristics["speech_rate"] = "Normal speech rate"
        
        # Spectral characteristics
        spectral_flatness = features.get("spectral_flatness", 0)
        if spectral_flatness > 0.05:
            characteristics["spectral_flatness"] = "High spectral flatness (synthetic indicator)"
        else:
            characteristics["spectral_flatness"] = "Normal spectral characteristics"
        
        return characteristics
    
    def _compare_natural_vs_synthetic(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Compare features against natural vs synthetic baselines"""
        comparison = {
            "natural_indicators": [],
            "synthetic_indicators": [],
            "score": 0.0
        }
        
        # Natural indicators
        if 0.3 <= features.get("blink_rate", 0) <= 0.5:
            comparison["natural_indicators"].append("Normal blink rate")
        if 0.4 <= features.get("pitch_variation", 0) <= 0.8:
            comparison["natural_indicators"].append("Natural pitch variation")
        if 0.8 <= features.get("speech_rate", 0) <= 1.2:
            comparison["natural_indicators"].append("Natural speech rate")
        
        # Synthetic indicators
        if features.get("pitch_variation", 0) < 0.2:
            comparison["synthetic_indicators"].append("Low pitch variation")
        if features.get("spectral_flatness", 0) > 0.05:
            comparison["synthetic_indicators"].append("High spectral flatness")
        if features.get("voice_quality_score", 0) < 0.4:
            comparison["synthetic_indicators"].append("Poor voice quality")
        
        # Calculate score (positive = more natural, negative = more synthetic)
        natural_score = len(comparison["natural_indicators"])
        synthetic_score = len(comparison["synthetic_indicators"])
        comparison["score"] = (natural_score - synthetic_score) / (natural_score + synthetic_score + 1)
        
        return comparison
    
    def _assess_signal_quality(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall signal quality"""
        quality_metrics = {
            "background_noise": features.get("background_noise_level", 0),
            "voice_quality": features.get("voice_quality_score", 0),
            "overall_score": 0.0,
            "interpretation": ""
        }
        
        # Calculate overall quality score
        noise_penalty = quality_metrics["background_noise"] * 0.3
        quality_metrics["overall_score"] = quality_metrics["voice_quality"] - noise_penalty
        
        # Interpret quality
        if quality_metrics["overall_score"] >= 0.8:
            quality_metrics["interpretation"] = "High quality audio"
        elif quality_metrics["overall_score"] >= 0.6:
            quality_metrics["interpretation"] = "Good quality audio"
        elif quality_metrics["overall_score"] >= 0.4:
            quality_metrics["interpretation"] = "Fair quality audio"
        else:
            quality_metrics["interpretation"] = "Poor quality audio"
        
        return quality_metrics
    
    def _calculate_clarity_score(self, features: Dict[str, Any]) -> float:
        """Calculate audio clarity score"""
        # Combine multiple factors
        voice_quality = features.get("voice_quality_score", 0)
        noise_level = features.get("background_noise_level", 0)
        zcr = features.get("zcr_mean", 0)
        
        # Normalize and combine
        clarity = voice_quality * (1 - noise_level) * (1 - min(zcr * 10, 1))
        return min(clarity, 1.0)
    
    def _identify_manipulation_signs(self, features: Dict[str, Any]) -> List[str]:
        """Identify signs of video manipulation"""
        signs = []
        
        # Face consistency
        if features.get("face_consistency_mean", 0) < 0.6:
            signs.append("Inconsistent face appearance across frames")
        
        if features.get("face_consistency_std", 0) > 0.2:
            signs.append("High variation in face consistency")
        
        # Lighting
        if features.get("lighting_consistency_mean", 0) < 0.5:
            signs.append("Inconsistent lighting patterns")
        
        # Motion
        if features.get("motion_consistency", 0) < 0.5:
            signs.append("Inconsistent motion patterns")
        
        # Quality
        if features.get("video_quality", 0) < 0.4:
            signs.append("Poor video quality (possible compression artifacts)")
        
        return signs
    
    def _analyze_video_synthetic_characteristics(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze video characteristics that suggest synthetic content"""
        characteristics = {}
        
        # Blink analysis
        blink_rate = features.get("blink_rate_mean", 0.3)
        if blink_rate < 0.2:
            characteristics["blink_rate"] = "Unnaturally low blink rate (deepfake indicator)"
        elif blink_rate > 0.6:
            characteristics["blink_rate"] = "Unnaturally high blink rate"
        else:
            characteristics["blink_rate"] = "Normal blink rate"
        
        # Lip sync analysis
        lip_sync = features.get("lip_sync_mean", 0.8)
        if lip_sync < 0.6:
            characteristics["lip_sync"] = "Poor lip synchronization (deepfake indicator)"
        elif lip_sync < 0.8:
            characteristics["lip_sync"] = "Moderate lip synchronization"
        else:
            characteristics["lip_sync"] = "Good lip synchronization"
        
        return characteristics
    
    def _assess_video_quality(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall video quality"""
        quality_metrics = {
            "video_quality": features.get("video_quality", 0),
            "lighting_consistency": features.get("lighting_consistency_mean", 0),
            "motion_consistency": features.get("motion_consistency", 0),
            "color_consistency": features.get("color_consistency", 0),
            "overall_score": 0.0,
            "interpretation": ""
        }
        
        # Calculate overall quality
        quality_metrics["overall_score"] = (
            quality_metrics["video_quality"] * 0.3 +
            quality_metrics["lighting_consistency"] * 0.25 +
            quality_metrics["motion_consistency"] * 0.25 +
            quality_metrics["color_consistency"] * 0.2
        )
        
        # Interpret quality
        if quality_metrics["overall_score"] >= 0.8:
            quality_metrics["interpretation"] = "High quality video"
        elif quality_metrics["overall_score"] >= 0.6:
            quality_metrics["interpretation"] = "Good quality video"
        elif quality_metrics["overall_score"] >= 0.4:
            quality_metrics["interpretation"] = "Fair quality video"
        else:
            quality_metrics["interpretation"] = "Poor quality video"
        
        return quality_metrics
    
    def _analyze_temporal_consistency(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal consistency in video"""
        consistency = {
            "face_consistency_std": features.get("face_consistency_std", 0),
            "lighting_consistency_std": features.get("lighting_consistency_std", 0),
            "blink_rate_std": features.get("blink_rate_std", 0),
            "overall_consistency": 0.0,
            "interpretation": ""
        }
        
        # Calculate overall consistency (lower std = more consistent)
        consistency["overall_consistency"] = 1 - (
            consistency["face_consistency_std"] * 0.4 +
            consistency["lighting_consistency_std"] * 0.3 +
            consistency["blink_rate_std"] * 0.3
        )
        
        # Interpret consistency
        if consistency["overall_consistency"] >= 0.8:
            consistency["interpretation"] = "Highly consistent over time"
        elif consistency["overall_consistency"] >= 0.6:
            consistency["interpretation"] = "Moderately consistent"
        elif consistency["overall_consistency"] >= 0.4:
            consistency["interpretation"] = "Some inconsistencies detected"
        else:
            consistency["interpretation"] = "High temporal inconsistencies (manipulation indicator)"
        
        return consistency
    
    def _detect_temporal_anomalies(self, features: Dict[str, Any]) -> List[str]:
        """Detect temporal anomalies in video"""
        anomalies = []
        
        # High standard deviations indicate anomalies
        if features.get("face_consistency_std", 0) > 0.3:
            anomalies.append("High face consistency variation")
        
        if features.get("lighting_consistency_std", 0) > 0.4:
            anomalies.append("High lighting variation")
        
        if features.get("blink_rate_std", 0) > 0.2:
            anomalies.append("Inconsistent blink patterns")
        
        return anomalies
    
    def _calculate_stability_metrics(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Calculate stability metrics for video"""
        return {
            "face_stability": 1 - features.get("face_consistency_std", 0),
            "lighting_stability": 1 - features.get("lighting_consistency_std", 0),
            "motion_stability": features.get("motion_consistency", 0),
            "overall_stability": 0.0
        }
    
    def _calculate_feature_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate confidence in feature extraction"""
        # Simple heuristic based on feature completeness and values
        confidence = 0.5  # Base confidence
        
        # Check for reasonable values
        if 0 < features.get("word_count", 0) < 1000:
            confidence += 0.1
        if 0 < features.get("sentiment_compound", 0) < 1:
            confidence += 0.1
        if features.get("scam_keyword_count", 0) >= 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_model_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate confidence in model predictions"""
        scam_score = analysis_result.get("scam_score", 0)
        
        # Higher confidence for extreme scores
        if scam_score < 0.2 or scam_score > 0.8:
            return 0.9
        elif scam_score < 0.4 or scam_score > 0.6:
            return 0.7
        else:
            return 0.5
    
    def _calculate_audio_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate confidence in audio analysis"""
        confidence = 0.5
        
        # Check for reasonable audio features
        if features.get("duration", 0) > 10:  # At least 10 seconds
            confidence += 0.2
        if features.get("voice_quality_score", 0) > 0.3:
            confidence += 0.2
        if features.get("sample_rate", 0) >= 16000:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_deepfake_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate confidence in deepfake detection"""
        deepfake_score = analysis_result.get("deepfake_score", 0)
        
        # Higher confidence for extreme scores
        if deepfake_score < 0.2 or deepfake_score > 0.8:
            return 0.9
        elif deepfake_score < 0.4 or deepfake_score > 0.6:
            return 0.7
        else:
            return 0.5
    
    def _calculate_video_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate confidence in video analysis"""
        confidence = 0.5
        
        # Check for reasonable video features
        if features.get("frame_count", 0) > 30:  # At least 1 second at 30fps
            confidence += 0.2
        if features.get("face_detection_confidence", 0) > 0.6:
            confidence += 0.2
        if features.get("video_quality", 0) > 0.3:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_overall_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall confidence in the analysis"""
        # Combine different confidence measures
        model_conf = self._calculate_model_confidence(analysis_result)
        
        # Add specific confidence based on analysis type
        if "audio_features" in analysis_result:
            audio_conf = self._calculate_audio_confidence(analysis_result["audio_features"])
            return (model_conf + audio_conf) / 2
        elif "video_features" in analysis_result:
            video_conf = self._calculate_video_confidence(analysis_result["video_features"])
            return (model_conf + video_conf) / 2
        else:
            return model_conf
    
    def _generate_text_visualizations(self, text: str, features: Dict[str, Any], 
                                    analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualizations for text analysis"""
        visualizations = {}
        
        # Feature importance chart
        feature_importance = {
            "Scam Keywords": features.get("scam_keyword_count", 0) * 0.3,
            "Urgency Keywords": features.get("urgency_keyword_count", 0) * 0.2,
            "Threat Keywords": features.get("threat_keyword_count", 0) * 0.25,
            "Exclamation Ratio": features.get("exclamation_ratio", 0) * 0.1,
            "Negative Sentiment": features.get("sentiment_negative", 0) * 0.1,
            "Uppercase Ratio": features.get("uppercase_ratio", 0) * 0.05
        }
        
        visualizations["feature_importance"] = feature_importance
        
        # Sentiment breakdown
        sentiment_breakdown = {
            "Positive": features.get("sentiment_positive", 0),
            "Neutral": features.get("sentiment_neutral", 0),
            "Negative": features.get("sentiment_negative", 0)
        }
        
        visualizations["sentiment_breakdown"] = sentiment_breakdown
        
        return visualizations
    
    def _generate_audio_visualizations(self, features: Dict[str, Any], 
                                     analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualizations for audio analysis"""
        visualizations = {}
        
        # Audio quality metrics
        quality_metrics = {
            "Voice Quality": features.get("voice_quality_score", 0),
            "Background Noise": 1 - features.get("background_noise_level", 0),
            "Signal Clarity": self._calculate_clarity_score(features)
        }
        
        visualizations["quality_metrics"] = quality_metrics
        
        # Deepfake indicators
        deepfake_indicators = {
            "Pitch Variation": features.get("pitch_variation", 0),
            "Speech Rate": min(features.get("speech_rate", 1.0) / 2, 1.0),
            "Spectral Flatness": min(features.get("spectral_flatness", 0) * 20, 1.0)
        }
        
        visualizations["deepfake_indicators"] = deepfake_indicators
        
        return visualizations
    
    def _generate_video_visualizations(self, features: Dict[str, Any], 
                                     analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualizations for video analysis"""
        visualizations = {}
        
        # Video quality metrics
        quality_metrics = {
            "Video Quality": features.get("video_quality", 0),
            "Lighting Consistency": features.get("lighting_consistency_mean", 0),
            "Motion Consistency": features.get("motion_consistency", 0),
            "Color Consistency": features.get("color_consistency", 0)
        }
        
        visualizations["quality_metrics"] = quality_metrics
        
        # Deepfake indicators
        deepfake_indicators = {
            "Face Consistency": features.get("face_consistency_mean", 0),
            "Blink Rate": min(features.get("blink_rate_mean", 0.3) * 2, 1.0),
            "Lip Sync": features.get("lip_sync_mean", 0.8)
        }
        
        visualizations["deepfake_indicators"] = deepfake_indicators
        
        return visualizations
    
    def generate_explanation_report(self, analysis_type: str, analysis_result: Dict[str, Any], 
                                  text: str = None) -> Dict[str, Any]:
        """Generate a comprehensive explanation report"""
        if analysis_type == "text":
            explanation = self.explain_text_analysis(text or "", analysis_result)
        elif analysis_type == "audio":
            explanation = self.explain_audio_analysis(analysis_result)
        elif analysis_type == "video":
            explanation = self.explain_video_analysis(analysis_result)
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
        
        # Add metadata
        explanation["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "analysis_type": analysis_type,
            "explanation_version": "1.0"
        }
        
        return explanation

if __name__ == "__main__":
    # Test the explainability engine
    engine = ExplainabilityEngine()
    
    # Test text explanation
    test_text = "Your bank account has been compromised. Please share your OTP 123456 immediately to secure it."
    test_analysis = {
        "scam_score": 0.85,
        "risk_level": "HIGH",
        "is_scam": True,
        "features": {
            "scam_keyword_count": 2,
            "urgency_keyword_count": 1,
            "exclamation_ratio": 0.0,
            "sentiment_negative": 0.3,
            "found_scam_keywords": ["bank account", "compromised"]
        },
        "recommendations": ["Do not share OTP", "Contact bank directly"]
    }
    
    explanation = engine.generate_explanation_report("text", test_analysis, test_text)
    print("Text explanation generated successfully")
    print(f"Overview: {explanation['overview']}")
    print(f"Feature analysis: {explanation['feature_analysis']}")
    print(f"Keyword analysis: {explanation['keyword_analysis']}")