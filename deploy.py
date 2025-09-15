"""
Deployment helper script for HR-Tech Challenge
Handles deployment preparation and cloud deployment
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
import zipfile
from datetime import datetime

class DeploymentManager:
    def __init__(self):
        self.project_root = Path(".")
        self.deployment_dir = Path("deployment")
        self.reports_dir = Path("reports")
    
    def prepare_deployment(self):
        """Prepare files for deployment"""
        print("📦 Preparing deployment package...")
        
        # Create deployment directory
        if self.deployment_dir.exists():
            shutil.rmtree(self.deployment_dir)
        self.deployment_dir.mkdir()
        
        # Copy essential files
        essential_files = [
            "src/",
            "config/",
            "requirements.txt",
            ".env",
            "README.md"
        ]
        
        for file_path in essential_files:
            source = self.project_root / file_path
            if source.exists():
                if source.is_dir():
                    shutil.copytree(source, self.deployment_dir / file_path)
                else:
                    shutil.copy2(source, self.deployment_dir / file_path)
                print(f"✅ Copied: {file_path}")
            else:
                print(f"⚠️ Missing: {file_path}")
        
        # Copy sample data (limited set for demo)
        sample_data_dir = self.deployment_dir / "data"
        sample_data_dir.mkdir(exist_ok=True)
        
        # Copy job descriptions
        job_desc_source = self.project_root / "data" / "job_descriptions"
        if job_desc_source.exists():
            shutil.copytree(job_desc_source, sample_data_dir / "job_descriptions")
            print("✅ Copied job descriptions")
        
        # Copy a few sample resumes
        resume_source = self.project_root / "data" / "resumes"
        resume_dest = sample_data_dir / "resumes"
        resume_dest.mkdir(exist_ok=True)
        
        if resume_source.exists():
            resume_files = list(resume_source.glob("*.txt"))[:5]  # Limit to 5 for demo
            for resume_file in resume_files:
                shutil.copy2(resume_file, resume_dest)
            print(f"✅ Copied {len(resume_files)} sample resumes")
        
        # Create deployment info
        deployment_info = {
            "deployment_date": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": [
                "Resume Screening API",
                "Sentiment Analysis API", 
                "Batch Processing API",
                "Interactive Documentation"
            ],
            "endpoints": {
                "health": "/health",
                "resume_screening": "/screen-resume",
                "sentiment_analysis": "/analyze-sentiment",
                "batch_sentiment": "/analyze-sentiment-batch",
                "documentation": "/docs"
            }
        }
        
        with open(self.deployment_dir / "deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print("✅ Deployment package prepared")
        return True
    
    def create_docker_files(self):
        """Create Docker configuration files"""
        print("🐳 Creating Docker configuration...")
        
        # Dockerfile
        dockerfile_content = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/resumes data/job_descriptions reports

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        with open(self.deployment_dir / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # Docker Compose
        docker_compose_content = """version: '3.8'

services:
  hr-tech-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}
      - MODEL_NAME=models/gemini-2.0-flash
    volumes:
      - ./reports:/app/reports
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
"""
        
        with open(self.deployment_dir / "docker-compose.yml", "w") as f:
            f.write(docker_compose_content)
        
        print("✅ Docker files created")
        return True
    
    def create_deployment_guide(self):
        """Create deployment guide README"""
        print("📖 Creating deployment guide...")
        
        guide_content = """# HR-Tech Challenge API - Deployment Guide

## Quick Start

### Option 1: Docker Deployment (Recommended)

1. **Prerequisites:**
   ```bash
   # Install Docker and Docker Compose
   docker --version
   docker-compose --version
   ```

2. **Environment Setup:**
   ```bash
   # Copy your Google AI API key to .env file
   echo "GOOGLE_AI_API_KEY=your_api_key_here" > .env
   ```

3. **Deploy:**
   ```bash
   # Build and start the API
   docker-compose up -d
   
   # Check status
   docker-compose ps
   
   # View logs
   docker-compose logs -f hr-tech-api
   ```

4. **Access:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - API Root: http://localhost:8000/

### Option 2: Local Development

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables:**
   ```bash
   export GOOGLE_AI_API_KEY=your_api_key_here
   export MODEL_NAME=models/gemini-2.0-flash
   ```

3. **Start API Server:**
   ```bash
   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### Resume Screening
- **POST** `/screen-resume`
  - Upload resume file (PDF, DOCX, TXT)
  - Returns screening score and recommendations

### Sentiment Analysis
- **POST** `/analyze-sentiment`
  - Analyze employee feedback text
  - Returns sentiment and attrition risk

### Batch Processing
- **POST** `/analyze-sentiment-batch`
  - Process multiple feedback entries
  - Returns batch analysis results

### Health Check
- **GET** `/health`
  - API health status and component check

## Testing

```bash
# Test all endpoints
python test_api.py

# Test specific endpoint
curl -X GET "http://localhost:8000/health"
```

## Cloud Deployment

### Google Cloud Run
```bash
# Build and deploy
gcloud run deploy hr-tech-api \\
  --source . \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --set-env-vars GOOGLE_AI_API_KEY=$GOOGLE_AI_API_KEY
```

### Heroku
```bash
# Create Heroku app
heroku create your-hr-tech-api

# Set environment variables
heroku config:set GOOGLE_AI_API_KEY=your_api_key_here

# Deploy
git push heroku main
```

### Azure Container Instances
```bash
# Deploy to Azure
az container create \\
  --resource-group myResourceGroup \\
  --name hr-tech-api \\
  --image hr-tech-api:latest \\
  --dns-name-label hr-tech-unique \\
  --ports 8000 \\
  --environment-variables GOOGLE_AI_API_KEY=your_api_key_here
```

## Configuration

### Environment Variables
- `GOOGLE_AI_API_KEY`: Your Google AI Studio API key (required)
- `MODEL_NAME`: Google AI model name (default: models/gemini-2.0-flash)
- `PORT`: API server port (default: 8000)

### Rate Limiting
- Default: 5 requests per minute per IP
- Configurable in `src/api/main.py`

## Monitoring

### Health Checks
```bash
# Check API health
curl http://localhost:8000/health

# Check component status
curl http://localhost:8000/health | jq '.components'
```

### Logs
```bash
# Docker logs
docker-compose logs -f hr-tech-api

# Application logs
tail -f logs/api.log
```

## Troubleshooting

### Common Issues

1. **Rate Limit Errors (429)**
   - Solution: Wait for rate limit reset or upgrade Google AI plan
   - Check: Google AI Studio usage dashboard

2. **API Key Issues**
   - Verify key is set: `echo $GOOGLE_AI_API_KEY`
   - Check permissions: Ensure Vertex AI API is enabled

3. **File Upload Issues**
   - Supported formats: PDF, DOCX, TXT
   - Max file size: 10MB
   - Check file permissions

### Support
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Test Endpoints: http://localhost:8000/test-sample-resume

## Production Notes

- Enable HTTPS in production
- Set up proper logging and monitoring
- Configure database for persistent storage
- Implement authentication/authorization
- Set up backup and disaster recovery
"""
        
        with open(self.deployment_dir / "README.md", "w") as f:
            f.write(guide_content)
        
        print("✅ Deployment guide created")
        return True
    
    def create_submission_package(self):
        """Create final submission package"""
        print("📋 Creating submission package...")
        
        # Create submission directory
        submission_dir = Path("hr_tech_submission")
        if submission_dir.exists():
            shutil.rmtree(submission_dir)
        submission_dir.mkdir()
        
        # Copy deployment package
        shutil.copytree(self.deployment_dir, submission_dir / "deployment")
        
        # Copy reports if they exist
        if self.reports_dir.exists():
            shutil.copytree(self.reports_dir, submission_dir / "reports")
        
        # Create technical report structure
        docs_dir = submission_dir / "documentation"
        docs_dir.mkdir()
        
        # Copy any existing documentation
        existing_docs = [
            "test_complete_systems.py",
            "test_api.py",
            "verify_data.py"
        ]
        
        for doc in existing_docs:
            if Path(doc).exists():
                shutil.copy2(doc, docs_dir)
        
        # Create submission info
        submission_info = {
            "project": "HR-Tech Innovation Challenge",
            "student_name": "Your Name Here",
            "submission_date": datetime.now().isoformat(),
            "components": {
                "resume_screening": "✅ Complete - AI-powered resume parsing and job matching",
                "sentiment_analysis": "✅ Complete - Employee feedback analysis with attrition prediction",
                "api_endpoints": "✅ Complete - RESTful APIs with documentation",
                "deployment": "✅ Complete - Docker containerization and deployment guides",
                "testing": "✅ Complete - Comprehensive testing suite"
            },
            "technologies_used": [
                "Google AI Studio (Gemini 2.0 Flash)",
                "FastAPI",
                "Python 3.11",
                "Docker",
                "Pydantic",
                "Uvicorn"
            ],
            "api_url": "http://localhost:8000",
            "documentation_url": "http://localhost:8000/docs"
        }
        
        with open(submission_dir / "SUBMISSION_INFO.json", "w") as f:
            json.dump(submission_info, f, indent=2)
        
        # Create ZIP file
        zip_filename = f"hr_tech_submission_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(submission_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, submission_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Submission package created: {zip_filename}")
        return zip_filename
    
    def run_deployment_preparation(self):
        """Run complete deployment preparation"""
        print("🚀 HR-Tech Deployment Preparation")
        print("=" * 40)
        
        steps = [
            ("Preparing Deployment", self.prepare_deployment),
            ("Creating Docker Files", self.create_docker_files),
            ("Creating Deployment Guide", self.create_deployment_guide),
            ("Creating Submission Package", self.create_submission_package)
        ]
        
        results = []
        for step_name, step_func in steps:
            try:
                print(f"\n📋 {step_name}...")
                result = step_func()
                results.append((step_name, result))
                
                if result:
                    print(f"✅ {step_name}: SUCCESS")
                else:
                    print(f"❌ {step_name}: FAILED")
                    
            except Exception as e:
                print(f"💥 {step_name}: ERROR - {str(e)}")
                results.append((step_name, False))
        
        # Summary
        print(f"\n{'='*40}")
        print("📊 DEPLOYMENT PREPARATION RESULTS:")
        
        successful_steps = [name for name, success in results if success]
        failed_steps = [name for name, success in results if not success]
        
        print(f"✅ Successful: {len(successful_steps)}/{len(results)}")
        for step in successful_steps:
            print(f"   ✅ {step}")
        
        if failed_steps:
            print(f"❌ Failed: {len(failed_steps)}")
            for step in failed_steps:
                print(f"   ❌ {step}")
        
        all_success = len(failed_steps) == 0
        
        if all_success:
            print(f"\n🎉 DEPLOYMENT READY!")
            print(f"   📁 Deployment files: ./deployment/")
            print(f"   📦 Submission package: Created")
            print(f"   🐳 Docker configuration: Ready")
            print(f"   📖 Documentation: Complete")
            
            print(f"\n🚀 Next Steps:")
            print(f"   1. Test API locally: python test_api.py")
            print(f"   2. Start API server: docker-compose up")
            print(f"   3. Access docs: http://localhost:8000/docs")
            print(f"   4. Submit your solution!")
        else:
            print(f"\n⚠️ Fix failed steps before deployment")
        
        return all_success

if __name__ == "__main__":
    manager = DeploymentManager()
    success = manager.run_deployment_preparation()
    
    if success:
        print(f"\n✅ Ready for submission and deployment!")
    else:
        print(f"\n🔧 Fix issues before proceeding")