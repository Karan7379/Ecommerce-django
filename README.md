# Multi-Channel Digital Arrest & Fraud Scam Detection and Prevention System

A comprehensive AI-powered system for detecting and preventing digital arrest scams across multiple communication channels (text, audio, video). The system uses advanced machine learning techniques to identify scam patterns, detect deepfake content, and provide real-time alerts with detailed explanations.

## 🚀 Features

### Core Detection Capabilities
- **Text Analysis**: NLP-based scam detection with keyword spotting and sentiment analysis
- **Audio Analysis**: Speech-to-text conversion with deepfake audio detection
- **Video Analysis**: Deepfake video detection using facial consistency and behavioral analysis
- **Multi-Channel Support**: SMS, email, voice calls, video calls, and social media

### AI/ML Models
- **NLP Models**: Scam text classification using TF-IDF and Random Forest
- **Audio Models**: Deepfake detection using spectral and acoustic features
- **Video Models**: Deepfake detection using facial landmarks and temporal consistency
- **Real-time Processing**: Instant analysis and alerting

### User Interface
- **Web Dashboard**: Modern, responsive interface for monitoring and analysis
- **Real-time Alerts**: Instant notifications with risk levels and recommendations
- **Explainability**: Detailed explanations of detection decisions
- **Statistics**: Comprehensive analytics and reporting

### Alert System
- **Multi-level Alerts**: MINIMAL, LOW, MEDIUM, HIGH, CRITICAL risk levels
- **Real-time Notifications**: Web, email, and SMS alerts
- **Escalation**: Automatic escalation for high-risk alerts
- **Cooldown Management**: Prevents alert spam

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection for model downloads

### Dependencies
- Flask 2.3.3
- scikit-learn 1.3.0
- numpy 1.24.3
- pandas 2.0.3
- librosa 0.10.1
- opencv-python 4.8.0.76
- nltk 3.8.1
- transformers 4.33.2
- torch 2.0.1

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd digital-fraud-detection
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon'); nltk.download('stopwords')"
```

### 5. Set Up Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## 🚀 Quick Start

### 1. Generate Mock Data
```bash
python data_generator.py
```

### 2. Train Models
```bash
python -c "from fraud_detector import FraudDetector; detector = FraudDetector(); detector.train_models()"
```

### 3. Start the Web Application
```bash
python app.py
```

### 4. Access the Dashboard
Open your browser and navigate to: `http://localhost:5000`

## 📖 Usage

### Web Interface

#### Dashboard Overview
- View system statistics and active alerts
- Monitor processing metrics and system health
- Access recent alerts and system status

#### Analyze Communications
1. **Text Analysis**: Paste suspicious text messages or emails
2. **Audio Analysis**: Upload audio files or enter call metadata
3. **Video Analysis**: Upload video files or enter video call metadata
4. **Batch Analysis**: Upload CSV files for bulk processing

#### Alert Management
- View all active alerts with risk levels
- Acknowledge or resolve alerts
- Access alert history and statistics

#### Settings
- Adjust detection thresholds
- Train models with new data
- Generate mock data for testing
- Export system statistics

### API Usage

#### Analyze Text
```bash
curl -X POST http://localhost:5000/api/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your bank account has been compromised. Please share your OTP 123456 immediately.",
    "sender": "+1234567890",
    "channel": "sms"
  }'
```

#### Analyze Audio
```bash
curl -X POST http://localhost:5000/api/analyze/audio \
  -H "Content-Type: application/json" \
  -d '{
    "caller_id": "+1234567890",
    "duration": 120
  }'
```

#### Get Alerts
```bash
curl http://localhost:5000/api/alerts
```

#### Get Statistics
```bash
curl http://localhost:5000/api/statistics
```

### Python API

```python
from fraud_detector import FraudDetector

# Initialize detector
detector = FraudDetector()

# Analyze text
result = detector.analyze_text(
    "Your bank account has been compromised. Please share your OTP 123456 immediately.",
    sender="+1234567890",
    channel="sms"
)

print(f"Scam Score: {result['analysis']['scam_score']}")
print(f"Risk Level: {result['analysis']['risk_level']}")
print(f"Is Scam: {result['analysis']['is_scam']}")

# Analyze audio
audio_result = detector.analyze_audio(
    caller_id="+1234567890",
    duration=120
)

# Analyze video
video_result = detector.analyze_video(
    caller_id="+1234567890",
    duration=180
)
```

## 🔧 Configuration

### Detection Thresholds
Edit `config.py` to adjust detection sensitivity:

```python
# Detection thresholds
TEXT_SCAM_THRESHOLD = 0.7      # Text scam detection threshold
AUDIO_FAKE_THRESHOLD = 0.6     # Audio deepfake detection threshold
VIDEO_FAKE_THRESHOLD = 0.5     # Video deepfake detection threshold

# Alert settings
ALERT_COOLDOWN = 300           # Alert cooldown in seconds
```

### Scam Keywords
Customize scam detection keywords in `config.py`:

```python
SCAM_KEYWORDS = [
    'arrest warrant', 'digital arrest', 'police', 'court', 'legal action',
    'immediate payment', 'urgent', 'verify identity', 'suspended account',
    # Add your custom keywords here
]
```

## 📊 Data Formats

### Input Data Format
For batch processing, use CSV format with these columns:

```csv
type,content,sender,channel,duration
text,"Your account has been compromised",+1234567890,sms,
audio,,+1234567890,audio,120
video,,+1234567890,video,180
```

### Output Format
Analysis results include:

```json
{
  "success": true,
  "type": "text",
  "analysis": {
    "scam_score": 0.85,
    "risk_level": "HIGH",
    "is_scam": true,
    "explanation": "Contains 2 scam-related keywords: bank account, compromised",
    "recommendations": [
      "DO NOT respond to this message",
      "DO NOT share any personal information",
      "Block the sender immediately"
    ],
    "features": {
      "scam_keyword_count": 2,
      "urgency_keyword_count": 1,
      "sentiment_negative": 0.3
    }
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/
```

### Test Individual Components
```bash
# Test text analyzer
python text_analyzer.py

# Test audio analyzer
python audio_analyzer.py

# Test video analyzer
python video_analyzer.py

# Test fraud detector
python fraud_detector.py
```

### Generate Test Data
```bash
python data_generator.py
```

## 🚀 Deployment

### Production Deployment

#### 1. Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 2. Using Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t fraud-detection .
docker run -p 5000:5000 fraud-detection
```

#### 3. Using Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  fraud-detection:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=your-production-secret-key
      - DEBUG=False
    volumes:
      - ./data:/app/data
      - ./models:/app/models
```

Run:
```bash
docker-compose up -d
```

### Environment Variables
Set these environment variables for production:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
FLASK_ENV=production
```

### Security Considerations
- Use HTTPS in production
- Set strong SECRET_KEY
- Configure proper CORS settings
- Implement rate limiting
- Use environment variables for sensitive data
- Regular security updates

## 📈 Performance Optimization

### Model Optimization
- Use GPU acceleration for deep learning models
- Implement model caching
- Use batch processing for large datasets
- Optimize feature extraction

### System Optimization
- Use Redis for caching
- Implement database for persistent storage
- Use message queues for async processing
- Load balancing for high availability

## 🔍 Monitoring and Logging

### Health Checks
```bash
curl http://localhost:5000/api/health
```

### Logging
The system logs to console by default. For production, configure proper logging:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fraud_detection.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics
Monitor these key metrics:
- Processing latency
- Detection accuracy
- Alert response time
- System uptime
- Resource usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

#### 1. Model Training Fails
- Ensure data files exist in the `data/` directory
- Check Python dependencies are installed
- Verify sufficient disk space

#### 2. Audio/Video Analysis Errors
- Install system dependencies (ffmpeg, portaudio)
- Check file format compatibility
- Verify file permissions

#### 3. Web Interface Not Loading
- Check Flask is running on correct port
- Verify all static files are present
- Check browser console for errors

### Getting Help
- Check the documentation
- Review error logs
- Open an issue on GitHub
- Contact the development team

## 🔮 Future Enhancements

### Planned Features
- Real-time streaming analysis
- Mobile app integration
- Advanced deepfake detection
- Multi-language support
- Integration with telecom providers
- Machine learning model updates
- Advanced reporting and analytics

### Research Areas
- Federated learning for privacy
- Adversarial attack detection
- Cross-modal deepfake detection
- Real-time voice synthesis detection
- Behavioral biometrics analysis

## 📚 References

- [NLTK Documentation](https://www.nltk.org/)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [Librosa Documentation](https://librosa.org/)
- [OpenCV Documentation](https://opencv.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**⚠️ Disclaimer**: This system is designed for educational and research purposes. Always verify suspicious communications through official channels and report fraud to appropriate authorities.