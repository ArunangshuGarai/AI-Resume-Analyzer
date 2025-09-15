"""
FastAPI REST API for HR-Tech Challenge
Main API endpoints for resume screening and sentiment analysis
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
import os
import shutil
import tempfile
from pathlib import Path
import json
from datetime import datetime
import time
import atexit

# Import your HR-Tech components
from ..resume_screening.screener import ResumeScreener
from ..sentiment_analysis.sentiment_analyzer import SentimentAnalyzer
from ..utils.llm_client import GoogleAIClient
# Add this at the top of src/api/main.py (after imports)
from dotenv import load_dotenv

# Load environment variables before anything else
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="HR-Tech AI APIs",
    description="AI-powered Resume Screening and Employee Sentiment Analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI components
resume_screener = None
sentiment_analyzer = None

@app.on_event("startup")
async def startup_event():
    """Initialize AI components on startup"""
    global resume_screener, sentiment_analyzer
    
    try:
        # Initialize resume screener with default job requirements
        job_requirements_path = "data/job_descriptions/software_engineer_job.yaml"
        resume_screener = ResumeScreener(job_requirements_path)
        
        # Initialize sentiment analyzer
        sentiment_analyzer = SentimentAnalyzer()
        
        print("✅ AI components initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize AI components: {str(e)}")

# Pydantic models for request/response
class ScreeningResponse(BaseModel):
    success: bool
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    final_score: float
    recommendation: str
    interview_recommended: bool
    strengths: List[str] = []
    concerns: List[str] = []
    missing_skills: List[str] = []
    position_context: Optional[Dict[str, str]] = None
    error: Optional[str] = None

class ExperienceRequirement(BaseModel):
    min_years: int
    max_years: int

class EducationRequirement(BaseModel):
    degree: str
    field: List[str]

class SalaryRange(BaseModel):
    min: int
    max: int

class JobRequirements(BaseModel):
    required_skills: Dict[str, List[str]]
    required_experience: ExperienceRequirement
    required_education: EducationRequirement
    salary_range: SalaryRange

@app.post("/screen-resume-with-job", response_model=ScreeningResponse)
async def screen_resume_with_job(
    file: UploadFile = File(...),
    department: str = Form(...),
    position: str = Form(...),
    job_requirements: str = Form(None)
):
    """
    Screen a resume against specific job requirements
    """
    if not resume_screener:
        raise HTTPException(status_code=503, detail="Resume screening service not available")
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_extension}. Allowed: {allowed_extensions}"
        )
    
    # Parse job requirements if provided
    position_requirements = None
    if job_requirements:
        try:
            position_requirements = json.loads(job_requirements)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid job requirements format")
    
    tmp_file_path = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        await file.seek(0)  # Reset file pointer
        
        # Store original requirements
        original_requirements = resume_screener.job_requirements
        
        try:
            # Update screener with position-specific requirements if provided
            if position_requirements:
                resume_screener.job_requirements = position_requirements
            
            # Screen the resume
            result = resume_screener.screen_single_resume(tmp_file_path)
            
            # Add position context to result
            if result['success']:
                result['position_context'] = {
                    'department': department,
                    'position': position,
                    'screening_date': datetime.now().isoformat()
                }
            
            if result['success']:
                return ScreeningResponse(
                    success=True,
                    candidate_name=result.get('candidate_name'),
                    candidate_email=result.get('candidate_email'),
                    final_score=result['final_score'],
                    recommendation=result['recommendation'],
                    interview_recommended=result['interview_recommended'],
                    strengths=result.get('strengths', []),
                    concerns=result.get('concerns', []),
                    missing_skills=result.get('missing_skills', []),
                    position_context=result.get('position_context')
                )
            else:
                return ScreeningResponse(
                    success=False,
                    final_score=0.0,
                    recommendation="error",
                    interview_recommended=False,
                    error=result.get('error', 'Unknown error occurred')
                )
        finally:
            # Restore original requirements
            resume_screener.job_requirements = original_requirements
            
    except Exception as e:
        return ScreeningResponse(
            success=False,
            final_score=0.0,
            recommendation="error",
            interview_recommended=False,
            error=str(e)
        )
    finally:
        # Clean up temporary file
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                time.sleep(0.1)  # Small delay to ensure file is not in use
                os.unlink(tmp_file_path)
            except PermissionError:
                # If file is still in use, register for cleanup at exit
                try:
                    atexit.register(lambda: os.path.exists(tmp_file_path) and os.unlink(tmp_file_path))
                except:
                    pass

class ResumeScreeningRequest(BaseModel):
    department: str = Field(..., description="Department for the position")
    position: str = Field(..., description="Job position title")
    job_requirements: Optional[JobRequirements] = Field(None, description="Specific requirements for the position")

class SentimentRequest(BaseModel):
    feedback_text: str
    employee_id: str
    department: str = "Unknown"
    position: str = "Unknown"
    tenure_months: int = 12
    manager_rating: int = 3
    performance_rating: int = 3

class SentimentResponse(BaseModel):
    success: bool
    employee_id: str
    sentiment: str
    confidence_score: float
    attrition_risk: str
    attrition_risk_score: float
    key_concerns: List[str] = []
    positive_indicators: List[str] = []
    recommended_actions: List[str] = []
    error: Optional[str] = None

class BatchSentimentRequest(BaseModel):
    feedback_entries: List[SentimentRequest]

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "HR-Tech AI APIs",
        "version": "1.0.0",
        "endpoints": {
            "resume_screening": "/screen-resume",
            "resume_screening_with_job": "/screen-resume-with-job",
            "sentiment_analysis": "/analyze-sentiment",
            "batch_sentiment": "/analyze-sentiment-batch",
            "job_positions": "/get-job-positions",
            "health_check": "/health"
        },
        "documentation": "/docs",
        "status": "active"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "resume_screener": resume_screener is not None,
            "sentiment_analyzer": sentiment_analyzer is not None,
            "google_ai": bool(os.getenv('GOOGLE_AI_API_KEY'))
        }
    }
    return status

class JobPosition(BaseModel):
    required_skills: Dict[str, List[str]]
    required_experience: ExperienceRequirement
    required_education: EducationRequirement
    salary_range: SalaryRange

class DepartmentPositions(BaseModel):
    positions: Dict[str, JobPosition]

class GetJobPositionsResponse(BaseModel):
    success: bool
    positions: Dict[str, Dict[str, JobPosition]]
    total_departments: int
    total_positions: int

# Get available job positions
@app.get("/get-job-positions", response_model=GetJobPositionsResponse)
async def get_job_positions():
    """Get all available job positions by department"""
    positions = {
        "Engineering": {
            "Software Engineer": {
                "required_skills": {
                    "programming_languages": ["Python", "Java", "JavaScript"],
                    "frameworks": ["React", "Node.js", "Django", "Spring Boot"],
                    "databases": ["MySQL", "PostgreSQL", "MongoDB"],
                    "cloud_platforms": ["AWS", "Azure", "Google Cloud"],
                    "tools": ["Git", "Docker", "Kubernetes", "Jenkins"]
                },
                "required_experience": {"min_years": 3, "max_years": 7},
                "required_education": {
                    "degree": "Bachelor's",
                    "field": ["Computer Science", "Software Engineering", "Information Technology"]
                },
                "salary_range": {"min": 80000, "max": 120000}
            },
            "Senior Software Engineer": {
                "required_skills": {
                    "programming_languages": ["Python", "Java", "JavaScript", "Go", "Rust"],
                    "frameworks": ["React", "Node.js", "Django", "Spring Boot", "Microservices"],
                    "databases": ["MySQL", "PostgreSQL", "MongoDB", "Redis"],
                    "cloud_platforms": ["AWS", "Azure", "Google Cloud"],
                    "tools": ["Git", "Docker", "Kubernetes", "Jenkins", "Terraform"]
                },
                "required_experience": {"min_years": 5, "max_years": 10},
                "required_education": {
                    "degree": "Bachelor's",
                    "field": ["Computer Science", "Software Engineering", "Information Technology"]
                },
                "salary_range": {"min": 120000, "max": 180000}
            }
        },
        "Data Science": {
            "Data Scientist": {
                "required_skills": {
                    "programming_languages": ["Python", "R", "SQL"],
                    "frameworks": ["Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch"],
                    "databases": ["MySQL", "PostgreSQL", "MongoDB", "BigQuery"],
                    "cloud_platforms": ["AWS", "Azure", "Google Cloud"],
                    "tools": ["Jupyter", "Git", "Tableau", "Power BI"]
                },
                "required_experience": {"min_years": 3, "max_years": 7},
                "required_education": {
                    "degree": "Master's",
                    "field": ["Data Science", "Statistics", "Mathematics", "Computer Science"]
                },
                "salary_range": {"min": 90000, "max": 140000}
            }
        }
    }
    
    return {
        "success": True,
        "positions": positions,
        "total_departments": len(positions),
        "total_positions": sum(len(dept_positions) for dept_positions in positions.values())
    }

@app.post("/screen-resume-with-job", response_model=ScreeningResponse)
async def screen_resume_with_job(
    department: str = Form(...),
    position: str = Form(...),
    job_requirements: str = Form(None),
    file: UploadFile = File(...)
):
    """
    Screen a resume file against specific job requirements
    """
    
    if not resume_screener:
        raise HTTPException(status_code=503, detail="Resume screening service not available")
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_extension}. Allowed: {allowed_extensions}"
        )
    
    # Parse job requirements if provided
    job_req = None
    if job_requirements:
        try:
            job_req = json.loads(job_requirements)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid job requirements format")
    
    tmp_file_path = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Rewind file for further processing
        await file.seek(0)
        
        # Screen resume with job-specific requirements
        if job_req:
            # Backup original requirements
            original_req = resume_screener.job_requirements
            resume_screener.job_requirements = job_req
            
            result = resume_screener.screen_single_resume(tmp_file_path)
            
            # Restore original requirements
            resume_screener.job_requirements = original_req
        else:
            result = resume_screener.screen_single_resume(tmp_file_path)
        
        # Add job context to result
        if result.get('success'):
            result['job_context'] = {
                'department': department,
                'position': position,
                'screening_date': datetime.now().isoformat()
            }
        
        # Format response
        if result['success']:
            return ScreeningResponse(
                success=True,
                candidate_name=result.get('candidate_name'),
                candidate_email=result.get('candidate_email'),
                final_score=result['final_score'],
                recommendation=result['recommendation'],
                interview_recommended=result['interview_recommended'],
                strengths=result.get('strengths', []),
                concerns=result.get('concerns', []),
                missing_skills=result.get('missing_skills', []),
                job_context=result.get('job_context')
            )
        else:
            return ScreeningResponse(
                success=False,
                final_score=0.0,
                recommendation="error",
                interview_recommended=False,
                error=result.get('error', 'Unknown error occurred')
            )
            
    except Exception as e:
        return ScreeningResponse(
            success=False,
            final_score=0.0,
            recommendation="error",
            interview_recommended=False,
            error=str(e)
        )
    finally:
        # Clean up temporary file
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                time.sleep(0.1)  # Small delay to ensure file is not in use
                os.unlink(tmp_file_path)
            except PermissionError:
                # Register cleanup for program exit if immediate deletion fails
                try:
                    atexit.register(lambda: os.path.exists(tmp_file_path) and os.unlink(tmp_file_path))
                except:
                    pass

@app.get("/get-job-positions")
async def get_job_positions():
    """Get all available job positions by department"""
    positions = {
        "Engineering": {
            "Software Engineer": {
                "required_skills": {
                    "programming_languages": ["Python", "Java", "JavaScript"],
                    "frameworks": ["React", "Node.js", "Django", "Spring Boot"],
                    "databases": ["MySQL", "PostgreSQL", "MongoDB"],
                    "cloud_platforms": ["AWS", "Azure", "Google Cloud"],
                    "tools": ["Git", "Docker", "Kubernetes", "Jenkins"]
                },
                "required_experience": {"min_years": 3, "max_years": 7},
                "required_education": {
                    "degree": "Bachelor's",
                    "field": ["Computer Science", "Software Engineering", "Information Technology"]
                },
                "salary_range": {"min": 80000, "max": 120000}
            },
            "Senior Software Engineer": {
                "required_skills": {
                    "programming_languages": ["Python", "Java", "JavaScript", "Go", "Rust"],
                    "frameworks": ["React", "Node.js", "Django", "Spring Boot", "Microservices"],
                    "databases": ["MySQL", "PostgreSQL", "MongoDB", "Redis"],
                    "cloud_platforms": ["AWS", "Azure", "Google Cloud"],
                    "tools": ["Git", "Docker", "Kubernetes", "Jenkins", "Terraform"]
                },
                "required_experience": {"min_years": 5, "max_years": 10},
                "required_education": {
                    "degree": "Bachelor's",
                    "field": ["Computer Science", "Software Engineering", "Information Technology"]
                },
                "salary_range": {"min": 120000, "max": 180000}
            }
        },
        "Data Science": {
            "Data Scientist": {
                "required_skills": {
                    "programming_languages": ["Python", "R", "SQL"],
                    "frameworks": ["Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch"],
                    "databases": ["MySQL", "PostgreSQL", "MongoDB", "BigQuery"],
                    "cloud_platforms": ["AWS", "Azure", "Google Cloud"],
                    "tools": ["Jupyter", "Git", "Tableau", "Power BI"]
                },
                "required_experience": {"min_years": 3, "max_years": 7},
                "required_education": {
                    "degree": "Master's",
                    "field": ["Data Science", "Statistics", "Mathematics", "Computer Science"]
                },
                "salary_range": {"min": 90000, "max": 140000}
            }
        }
    }
    
    return {
        "success": True,
        "positions": positions,
        "total_departments": len(positions),
        "total_positions": sum(len(dept_positions) for dept_positions in positions.values())
    }

@app.post("/screen-resume", response_model=ScreeningResponse)
async def screen_resume(file: UploadFile = File(...)):
    """
    Screen a resume file against job requirements
    
    Accepts: PDF, DOCX, or TXT files
    Returns: Screening results with score and recommendations
    """
    
    if not resume_screener:
        raise HTTPException(status_code=503, detail="Resume screening service not available")
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_extension}. Allowed: {allowed_extensions}"
        )
    
    # Create temporary file to process upload
    tmp_file_path = None
    try:
        # Create temporary file with proper context management
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            # Save uploaded file content
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Reset file pointer for potential reuse
        await file.seek(0)
        
        # Screen the resume
        result = resume_screener.screen_single_resume(tmp_file_path)
        
        # Format response
        if result['success']:
            return ScreeningResponse(
                success=True,
                candidate_name=result.get('candidate_name'),
                candidate_email=result.get('candidate_email'),
                final_score=result['final_score'],
                recommendation=result['recommendation'],
                interview_recommended=result['interview_recommended'],
                strengths=result.get('strengths', []),
                concerns=result.get('concerns', []),
                missing_skills=result.get('missing_skills', [])
            )
        else:
            return ScreeningResponse(
                success=False,
                final_score=0.0,
                recommendation="error",
                interview_recommended=False,
                error=result.get('error', 'Unknown error occurred')
            )
            
    except Exception as e:
        return ScreeningResponse(
            success=False,
            final_score=0.0,
            recommendation="error", 
            interview_recommended=False,
            error=str(e)
        )
    finally:
        # Clean up temporary file with proper error handling
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                # Small delay to ensure file is released
                import time
                time.sleep(0.1)
                os.unlink(tmp_file_path)
            except PermissionError:
                # If we can't delete immediately, schedule for later cleanup
                try:
                    # Try to delete on next restart
                    import atexit
                    atexit.register(lambda: os.path.exists(tmp_file_path) and os.unlink(tmp_file_path))
                except:
                    pass  # Ignore cleanup failures
                
# Single sentiment analysis endpoint
# Replace the analyze_sentiment endpoint in src/api/main.py with this fixed version:

@app.post("/analyze-sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze employee feedback sentiment and predict attrition risk
    
    Returns: Sentiment analysis with attrition risk and recommendations
    """
    
    if not sentiment_analyzer:
        raise HTTPException(status_code=503, detail="Sentiment analysis service not available")
    
    try:
        # Prepare employee context
        employee_context = {
            'employee_id': request.employee_id,
            'department': request.department,
            'position': request.position,
            'tenure_months': request.tenure_months,
            'manager_rating': request.manager_rating,
            'performance_rating': request.performance_rating
        }
        
        # Analyze sentiment
        result = sentiment_analyzer.analyze_single_feedback(
            request.feedback_text, 
            employee_context
        )
        
        # Format response
        if result['success']:
            sentiment_data = result['sentiment_analysis']
            recommendations = result.get('engagement_recommendations', {})
            
            # Extract and format recommended actions
            recommended_actions = []
            immediate_actions = recommendations.get('immediate_actions', [])
            
            for action in immediate_actions:
                if isinstance(action, dict):
                    # Extract text from dictionary format
                    if 'action' in action:
                        recommended_actions.append(str(action['action']))
                    else:
                        recommended_actions.append(str(action))
                else:
                    recommended_actions.append(str(action))
            
            # Also add other action types if available
            for action_type in ['short_term_strategies', 'long_term_initiatives']:
                actions = recommendations.get(action_type, [])
                for action in actions[:2]:  # Limit to avoid overwhelming
                    if isinstance(action, dict):
                        if 'action' in action:
                            recommended_actions.append(f"[{action_type.replace('_', ' ').title()}] {action['action']}")
                        else:
                            recommended_actions.append(f"[{action_type.replace('_', ' ').title()}] {str(action)}")
                    else:
                        recommended_actions.append(f"[{action_type.replace('_', ' ').title()}] {str(action)}")
            
            # Format key concerns and positive indicators similarly
            key_concerns = []
            for concern in result.get('key_concerns', []):
                if isinstance(concern, dict):
                    key_concerns.append(str(concern.get('concern', concern)))
                else:
                    key_concerns.append(str(concern))
            
            positive_indicators = []
            pos_indicators = sentiment_data.get('positive_indicators', [])
            for indicator in pos_indicators:
                if isinstance(indicator, dict):
                    positive_indicators.append(str(indicator.get('indicator', indicator)))
                else:
                    positive_indicators.append(str(indicator))
            
            return SentimentResponse(
                success=True,
                employee_id=request.employee_id,
                sentiment=sentiment_data.get('sentiment', 'neutral'),
                confidence_score=sentiment_data.get('confidence_score', 0.0),
                attrition_risk=result['attrition_risk_level'],
                attrition_risk_score=result['attrition_risk_score'],
                key_concerns=key_concerns,
                positive_indicators=positive_indicators,
                recommended_actions=recommended_actions[:10]  # Limit to 10 actions
            )
        else:
            return SentimentResponse(
                success=False,
                employee_id=request.employee_id,
                sentiment="unknown",
                confidence_score=0.0,
                attrition_risk="unknown",
                attrition_risk_score=0.0,
                error=result.get('error', 'Unknown error occurred')
            )
            
    except Exception as e:
        return SentimentResponse(
            success=False,
            employee_id=request.employee_id,
            sentiment="unknown",
            confidence_score=0.0,
            attrition_risk="unknown", 
            attrition_risk_score=0.0,
            error=str(e)
        )
        
# Batch sentiment analysis endpoint
@app.post("/analyze-sentiment-batch")
async def analyze_sentiment_batch(request: BatchSentimentRequest, background_tasks: BackgroundTasks):
    """
    Analyze multiple employee feedback entries
    
    Returns: Batch analysis results
    """
    
    if not sentiment_analyzer:
        raise HTTPException(status_code=503, detail="Sentiment analysis service not available")
    
    if len(request.feedback_entries) > 50:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 50 entries allowed per batch request"
        )
    
    try:
        results = []
        
        for entry in request.feedback_entries:
            employee_context = {
                'employee_id': entry.employee_id,
                'department': entry.department,
                'position': entry.position,
                'tenure_months': entry.tenure_months,
                'manager_rating': entry.manager_rating,
                'performance_rating': entry.performance_rating
            }
            
            # Analyze each entry
            result = sentiment_analyzer.analyze_single_feedback(
                entry.feedback_text,
                employee_context
            )
            
            # Format individual result
            if result['success']:
                sentiment_data = result['sentiment_analysis']
                recommendations = result.get('engagement_recommendations', {})
                
                formatted_result = {
                    "employee_id": entry.employee_id,
                    "success": True,
                    "sentiment": sentiment_data.get('sentiment', 'neutral'),
                    "confidence_score": sentiment_data.get('confidence_score', 0.0),
                    "attrition_risk": result['attrition_risk_level'],
                    "attrition_risk_score": result['attrition_risk_score'],
                    "key_concerns": result.get('key_concerns', []),
                    "recommended_actions": recommendations.get('immediate_actions', [])
                }
            else:
                formatted_result = {
                    "employee_id": entry.employee_id,
                    "success": False,
                    "error": result.get('error', 'Unknown error')
                }
            
            results.append(formatted_result)
        
        # Calculate summary statistics
        successful_results = [r for r in results if r.get('success', False)]
        sentiment_counts = {}
        risk_counts = {}
        
        for result in successful_results:
            sentiment = result.get('sentiment', 'unknown')
            risk = result.get('attrition_risk', 'unknown')
            
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        return {
            "success": True,
            "total_entries": len(request.feedback_entries),
            "successful_analyses": len(successful_results),
            "failed_analyses": len(request.feedback_entries) - len(successful_results),
            "summary": {
                "sentiment_distribution": sentiment_counts,
                "risk_distribution": risk_counts
            },
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Development endpoint to test with sample data
@app.get("/test-sample-resume")
async def test_sample_resume():
    """Test endpoint with sample resume (for development/demo)"""
    
    if not resume_screener:
        raise HTTPException(status_code=503, detail="Resume screening service not available")
    
    # Use first available sample resume
    sample_resume_path = "data/resumes/john_smith_resume.txt"
    
    if not Path(sample_resume_path).exists():
        raise HTTPException(status_code=404, detail="Sample resume not found")
    
    try:
        result = resume_screener.screen_single_resume(sample_resume_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-sample-sentiment")
async def test_sample_sentiment():
    """Test endpoint with sample sentiment analysis (for development/demo)"""
    
    if not sentiment_analyzer:
        raise HTTPException(status_code=503, detail="Sentiment analysis service not available")
    
    # Sample employee feedback
    sample_feedback = "I really enjoy working here and love the team collaboration, but sometimes the workload feels overwhelming."
    sample_context = {
        'employee_id': 'DEMO001',
        'department': 'Engineering',
        'position': 'Software Engineer', 
        'tenure_months': 18,
        'manager_rating': 4,
        'performance_rating': 4
    }
    
    try:
        result = sentiment_analyzer.analyze_single_feedback(sample_feedback, sample_context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)