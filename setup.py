#!/usr/bin/env python3
"""
Setup script for the Digital Fraud Detection System
"""
import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"✗ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_system_dependencies():
    """Install system dependencies"""
    print("\nInstalling system dependencies...")
    
    system = platform.system().lower()
    
    if system == "linux":
        # Install system packages for Ubuntu/Debian
        packages = [
            "python3-dev",
            "python3-pip",
            "libasound2-dev",
            "portaudio19-dev",
            "libportaudio2",
            "libportaudiocpp0",
            "ffmpeg",
            "libsndfile1"
        ]
        
        for package in packages:
            if not run_command(f"sudo apt-get install -y {package}", f"Installing {package}"):
                print(f"Warning: Failed to install {package}")
    
    elif system == "darwin":  # macOS
        if not run_command("brew install portaudio ffmpeg", "Installing system packages via Homebrew"):
            print("Warning: Failed to install system packages. Please install manually:")
            print("brew install portaudio ffmpeg")
    
    elif system == "windows":
        print("Windows detected. Please install the following manually:")
        print("- Visual Studio Build Tools")
        print("- FFmpeg")
        print("- PortAudio")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    directories = ["data", "models", "uploads", "templates", "static", "logs"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        except Exception as e:
            print(f"✗ Failed to create directory {directory}: {e}")
            return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("\nDownloading NLTK data...")
    
    nltk_commands = [
        "python -c \"import nltk; nltk.download('punkt')\"",
        "python -c \"import nltk; nltk.download('vader_lexicon')\"",
        "python -c \"import nltk; nltk.download('stopwords')\""
    ]
    
    for command in nltk_commands:
        if not run_command(command, "Downloading NLTK data"):
            print("Warning: Failed to download some NLTK data")
    
    return True

def generate_initial_data():
    """Generate initial mock data"""
    print("\nGenerating initial data...")
    
    if not run_command("python data_generator.py", "Generating mock datasets"):
        print("Warning: Failed to generate initial data")
        return False
    
    return True

def train_initial_models():
    """Train initial models"""
    print("\nTraining initial models...")
    
    train_command = "python -c \"from fraud_detector import FraudDetector; detector = FraudDetector(); detector.train_models()\""
    
    if not run_command(train_command, "Training ML models"):
        print("Warning: Failed to train initial models")
        return False
    
    return True

def create_env_file():
    """Create environment file"""
    print("\nCreating environment file...")
    
    env_content = """# Digital Fraud Detection System Environment Variables
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
FLASK_ENV=development

# Optional: Email configuration for alerts
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password

# Optional: SMS configuration for alerts
# TWILIO_ACCOUNT_SID=your-twilio-sid
# TWILIO_AUTH_TOKEN=your-twilio-token
# TWILIO_PHONE_NUMBER=your-twilio-number
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False

def run_tests():
    """Run system tests"""
    print("\nRunning system tests...")
    
    if not run_command("python test_system.py", "Running test suite"):
        print("Warning: Some tests failed")
        return False
    
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("Digital Fraud Detection System - Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        print("❌ Setup failed: Incompatible Python version")
        return 1
    
    # Install system dependencies
    install_system_dependencies()
    
    # Create directories
    if not create_directories():
        print("❌ Setup failed: Could not create directories")
        return 1
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Setup failed: Could not install Python dependencies")
        return 1
    
    # Download NLTK data
    download_nltk_data()
    
    # Create environment file
    if not create_env_file():
        print("❌ Setup failed: Could not create environment file")
        return 1
    
    # Generate initial data
    generate_initial_data()
    
    # Train initial models
    train_initial_models()
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Start the web application:")
    print("   python app.py")
    print("\n2. Open your browser and navigate to:")
    print("   http://localhost:5000")
    print("\n3. Explore the dashboard and test the system")
    print("\n4. For production deployment, see README.md")
    
    print("\nSystem features:")
    print("✓ Text scam detection")
    print("✓ Audio deepfake detection")
    print("✓ Video deepfake detection")
    print("✓ Real-time alerting")
    print("✓ Web dashboard")
    print("✓ API endpoints")
    print("✓ Explainable AI")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())