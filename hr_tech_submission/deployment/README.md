# HR-Tech Challenge API - Deployment Guide

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
gcloud run deploy hr-tech-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
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
az container create \
  --resource-group myResourceGroup \
  --name hr-tech-api \
  --image hr-tech-api:latest \
  --dns-name-label hr-tech-unique \
  --ports 8000 \
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
