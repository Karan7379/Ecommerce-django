"""
Text analysis module for detecting scam patterns in text communications
"""
import re
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pickle
import os
from config import Config

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextAnalyzer:
    def __init__(self):
        self.config = Config()
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract various features from text for scam detection"""
        features = {}
        
        # Basic text features
        features['length'] = len(text)
        features['word_count'] = len(text.split())
        features['sentence_count'] = len(re.split(r'[.!?]+', text))
        features['avg_word_length'] = np.mean([len(word) for word in text.split()]) if text.split() else 0
        
        # Uppercase ratio
        features['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Exclamation and question marks
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['exclamation_ratio'] = features['exclamation_count'] / features['word_count'] if features['word_count'] > 0 else 0
        
        # Phone number pattern
        phone_pattern = r'\+?[\d\s\-\(\)]{10,}'
        features['has_phone'] = 1 if re.search(phone_pattern, text) else 0
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        features['has_email'] = 1 if re.search(email_pattern, text) else 0
        
        # URL pattern
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        features['has_url'] = 1 if re.search(url_pattern, text) else 0
        
        # Currency pattern
        currency_pattern = r'₹\s*\d+[,\d]*|\$\s*\d+[,\d]*|USD\s*\d+[,\d]*'
        features['has_currency'] = 1 if re.search(currency_pattern, text) else 0
        
        # Scam keyword analysis
        scam_keywords_found = []
        urgency_keywords_found = []
        threat_keywords_found = []
        
        text_lower = text.lower()
        for keyword in self.config.SCAM_KEYWORDS:
            if keyword.lower() in text_lower:
                scam_keywords_found.append(keyword)
        
        for keyword in self.config.URGENCY_KEYWORDS:
            if keyword.lower() in text_lower:
                urgency_keywords_found.append(keyword)
        
        for keyword in self.config.THREAT_KEYWORDS:
            if keyword.lower() in text_lower:
                threat_keywords_found.append(keyword)
        
        features['scam_keyword_count'] = len(scam_keywords_found)
        features['urgency_keyword_count'] = len(urgency_keywords_found)
        features['threat_keyword_count'] = len(threat_keywords_found)
        features['scam_keyword_ratio'] = features['scam_keyword_count'] / features['word_count'] if features['word_count'] > 0 else 0
        
        # Sentiment analysis
        sentiment_scores = self.sia.polarity_scores(text)
        features['sentiment_compound'] = sentiment_scores['compound']
        features['sentiment_negative'] = sentiment_scores['neg']
        features['sentiment_neutral'] = sentiment_scores['neu']
        features['sentiment_positive'] = sentiment_scores['pos']
        
        # Repetition analysis
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if word not in self.stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        features['repetition_score'] = max(word_freq.values()) / len(words) if words else 0
        
        # Store found keywords for explainability
        features['found_scam_keywords'] = scam_keywords_found
        features['found_urgency_keywords'] = urgency_keywords_found
        features['found_threat_keywords'] = threat_keywords_found
        
        return features
    
    def calculate_scam_score(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Calculate overall scam probability score"""
        features = self.extract_text_features(text)
        
        # Rule-based scoring
        rule_score = 0.0
        
        # Scam keyword presence
        if features['scam_keyword_count'] > 0:
            rule_score += 0.3 * min(features['scam_keyword_count'] / 5, 1.0)
        
        # Urgency indicators
        if features['urgency_keyword_count'] > 0:
            rule_score += 0.2 * min(features['urgency_keyword_count'] / 3, 1.0)
        
        # Threat indicators
        if features['threat_keyword_count'] > 0:
            rule_score += 0.25 * min(features['threat_keyword_count'] / 3, 1.0)
        
        # Excessive punctuation
        if features['exclamation_ratio'] > 0.1:
            rule_score += 0.1
        
        # Negative sentiment
        if features['sentiment_negative'] > 0.5:
            rule_score += 0.1
        
        # Uppercase ratio (shouting)
        if features['uppercase_ratio'] > 0.3:
            rule_score += 0.05
        
        # Currency mentions
        if features['has_currency']:
            rule_score += 0.1
        
        # Phone/email in suspicious context
        if features['has_phone'] or features['has_email']:
            rule_score += 0.05
        
        # Normalize score
        rule_score = min(rule_score, 1.0)
        
        # If ML model is trained, use it for additional scoring
        ml_score = 0.0
        if self.is_trained:
            try:
                # Convert features to array for ML model
                feature_array = np.array([
                    features['length'], features['word_count'], features['sentence_count'],
                    features['avg_word_length'], features['uppercase_ratio'],
                    features['exclamation_count'], features['question_count'],
                    features['exclamation_ratio'], features['has_phone'],
                    features['has_email'], features['has_url'], features['has_currency'],
                    features['scam_keyword_count'], features['urgency_keyword_count'],
                    features['threat_keyword_count'], features['scam_keyword_ratio'],
                    features['sentiment_compound'], features['sentiment_negative'],
                    features['sentiment_neutral'], features['sentiment_positive'],
                    features['repetition_score']
                ]).reshape(1, -1)
                
                ml_score = self.classifier.predict_proba(feature_array)[0][1]  # Probability of scam
            except Exception as e:
                print(f"ML prediction error: {e}")
        
        # Combine rule-based and ML scores
        final_score = 0.6 * rule_score + 0.4 * ml_score
        
        return final_score, features
    
    def train_model(self, data_file: str = "data/text_communications.csv"):
        """Train the ML model on text data"""
        if not os.path.exists(data_file):
            print(f"Data file {data_file} not found. Please generate data first.")
            return
        
        # Load data
        df = pd.read_csv(data_file)
        
        # Extract features for all texts
        features_list = []
        for text in df['content']:
            features = self.extract_text_features(text)
            # Convert to array (excluding non-numeric features)
            feature_array = [
                features['length'], features['word_count'], features['sentence_count'],
                features['avg_word_length'], features['uppercase_ratio'],
                features['exclamation_count'], features['question_count'],
                features['exclamation_ratio'], features['has_phone'],
                features['has_email'], features['has_url'], features['has_currency'],
                features['scam_keyword_count'], features['urgency_keyword_count'],
                features['threat_keyword_count'], features['scam_keyword_ratio'],
                features['sentiment_compound'], features['sentiment_negative'],
                features['sentiment_neutral'], features['sentiment_positive'],
                features['repetition_score']
            ]
            features_list.append(feature_array)
        
        X = np.array(features_list)
        y = df['is_scam'].astype(int).values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.classifier.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model trained successfully!")
        print(f"Accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        self.is_trained = True
        
        # Save model
        os.makedirs(self.config.MODEL_DIR, exist_ok=True)
        with open(f"{self.config.MODEL_DIR}/text_classifier.pkl", 'wb') as f:
            pickle.dump(self.classifier, f)
        
        print(f"Model saved to {self.config.MODEL_DIR}/text_classifier.pkl")
    
    def load_model(self, model_file: str = "models/text_classifier.pkl"):
        """Load a pre-trained model"""
        if os.path.exists(model_file):
            with open(model_file, 'rb') as f:
                self.classifier = pickle.load(f)
            self.is_trained = True
            print(f"Model loaded from {model_file}")
        else:
            print(f"Model file {model_file} not found")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text and return comprehensive results"""
        score, features = self.calculate_scam_score(text)
        
        # Determine risk level
        if score >= 0.8:
            risk_level = "HIGH"
        elif score >= 0.6:
            risk_level = "MEDIUM"
        elif score >= 0.4:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        # Generate explanation
        explanation = self.generate_explanation(features, score)
        
        return {
            "scam_score": score,
            "risk_level": risk_level,
            "is_scam": score >= self.config.TEXT_SCAM_THRESHOLD,
            "features": features,
            "explanation": explanation,
            "recommendations": self.get_recommendations(features, score)
        }
    
    def generate_explanation(self, features: Dict[str, Any], score: float) -> str:
        """Generate human-readable explanation of the analysis"""
        explanations = []
        
        if features['scam_keyword_count'] > 0:
            explanations.append(f"Contains {features['scam_keyword_count']} scam-related keywords: {', '.join(features['found_scam_keywords'])}")
        
        if features['urgency_keyword_count'] > 0:
            explanations.append(f"Contains {features['urgency_keyword_count']} urgency indicators: {', '.join(features['found_urgency_keywords'])}")
        
        if features['threat_keyword_count'] > 0:
            explanations.append(f"Contains {features['threat_keyword_count']} threat indicators: {', '.join(features['found_threat_keywords'])}")
        
        if features['exclamation_ratio'] > 0.1:
            explanations.append("Excessive use of exclamation marks suggests urgency")
        
        if features['sentiment_negative'] > 0.5:
            explanations.append("Strong negative sentiment detected")
        
        if features['has_currency']:
            explanations.append("Mentions monetary amounts")
        
        if features['uppercase_ratio'] > 0.3:
            explanations.append("Excessive use of uppercase letters")
        
        if not explanations:
            explanations.append("No obvious scam indicators detected")
        
        return "; ".join(explanations)
    
    def get_recommendations(self, features: Dict[str, Any], score: float) -> List[str]:
        """Get actionable recommendations based on analysis"""
        recommendations = []
        
        if score >= 0.7:
            recommendations.extend([
                "DO NOT respond to this message",
                "DO NOT share any personal information",
                "DO NOT make any payments",
                "Block the sender immediately",
                "Report to authorities if necessary"
            ])
        elif score >= 0.4:
            recommendations.extend([
                "Be cautious - verify the sender's identity",
                "Do not share sensitive information",
                "Contact the organization directly through official channels"
            ])
        else:
            recommendations.append("Message appears legitimate, but always verify important requests")
        
        return recommendations

if __name__ == "__main__":
    analyzer = TextAnalyzer()
    
    # Train model if data exists
    if os.path.exists("data/text_communications.csv"):
        analyzer.train_model()
    
    # Test with sample texts
    test_texts = [
        "Your bank account has been compromised. Please share your OTP 123456 immediately to secure it.",
        "Your monthly statement is ready. Please check your email for details.",
        "This is Police Department calling. You have a warrant for your arrest. Pay ₹50,000 immediately to avoid jail time."
    ]
    
    for text in test_texts:
        result = analyzer.analyze_text(text)
        print(f"\nText: {text}")
        print(f"Scam Score: {result['scam_score']:.3f}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Is Scam: {result['is_scam']}")
        print(f"Explanation: {result['explanation']}")
        print(f"Recommendations: {', '.join(result['recommendations'])}")