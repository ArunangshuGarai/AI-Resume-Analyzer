"""
Streamlit Frontend for HR-Tech Challenge
File: frontend/streamlit_app.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from pathlib import Path
import io
from config import JOB_POSITIONS

# Configure page
st.set_page_config(
    page_title="HR-Tech AI Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

class HRTechDashboard:
    def __init__(self):
        self.api_url = API_BASE_URL
        
    def check_api_health(self):
        """Check if API is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200, response.json() if response.status_code == 200 else None
        except Exception as e:
            return False, str(e)
    
    def screen_resume(self, uploaded_file, department, position):
        """Screen uploaded resume for a specific position"""
        try:
            # Get job requirements for the selected position
            job_requirements = JOB_POSITIONS.get(department, {}).get(position, {})
            
            # Prepare multipart form data
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {
                "department": department,
                "position": position,
                "job_requirements": json.dumps(job_requirements)
            }
            
            # Make request to enhanced endpoint
            response = requests.post(
                f"{self.api_url}/screen-resume-with-job",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def analyze_sentiment(self, feedback_data):
        """Analyze employee sentiment"""
        try:
            response = requests.post(f"{self.api_url}/analyze-sentiment", json=feedback_data, timeout=30)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def batch_analyze_sentiment(self, feedback_entries):
        """Batch analyze sentiment"""
        try:
            data = {"feedback_entries": feedback_entries}
            response = requests.post(f"{self.api_url}/analyze-sentiment-batch", json=data, timeout=60)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return False, {"error": str(e)}

def main():
    st.title("🤖 HR-Tech AI Dashboard")
    st.markdown("---")
    
    # Initialize dashboard
    dashboard = HRTechDashboard()
    
    # Check API health
    api_healthy, health_data = dashboard.check_api_health()
    
    if not api_healthy:
        st.error(f"⚠️ API Connection Failed: {health_data}")
        st.info("Please ensure the API server is running on http://localhost:8000")
        st.code("python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Display API health status
    with st.sidebar:
        st.success("🟢 API Connected")
        if health_data:
            components = health_data.get('components', {})
            st.write("**System Status:**")
            for component, status in components.items():
                icon = "✅" if status else "❌"
                st.write(f"{icon} {component.replace('_', ' ').title()}")
    
    # Main navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Resume Screening", 
        "💬 Sentiment Analysis", 
        "📊 Batch Processing",
        "📈 Analytics Dashboard"
    ])
    
    # Resume Screening Tab
    with tab1:
        st.header("Resume Screening")
        st.write("Upload a resume to analyze candidate fit for available positions")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Department and position selection
            department = st.selectbox(
                "Select Department",
                options=list(JOB_POSITIONS.keys()),
                help="Choose the department for the position"
            )
            
            # Get available positions for selected department
            available_positions = list(JOB_POSITIONS.get(department, {}).keys())
            position = st.selectbox(
                "Select Position",
                options=available_positions,
                help="Choose the specific position"
            )
            
            # Show position requirements
            if department and position:
                requirements = JOB_POSITIONS[department][position]
                with st.expander("📋 Position Requirements"):
                    st.write("**Required Skills:**")
                    for category, skills in requirements["required_skills"].items():
                        st.write(f"- {category.replace('_', ' ').title()}:")
                        st.write(", ".join(skills))
                    
                    exp = requirements["required_experience"]
                    st.write(f"**Experience:** {exp['min_years']}-{exp['max_years']} years")
                    
                    edu = requirements["required_education"]
                    st.write(f"**Education:** {edu['degree']} in {' or '.join(edu['field'])}")
                    
                    salary = requirements["salary_range"]
                    st.write(f"**Salary Range:** ${salary['min']:,} - ${salary['max']:,}")
            
            st.markdown("---")
            
            uploaded_file = st.file_uploader(
                "Choose resume file", 
                type=['txt', 'pdf', 'docx'],
                help="Supported formats: TXT, PDF, DOCX"
            )
            
            if uploaded_file is not None:
                st.info(f"📁 File: {uploaded_file.name}")
                st.info(f"📏 Size: {len(uploaded_file.getvalue())} bytes")
                
                if st.button("🔍 Analyze Resume", type="primary"):
                    with st.spinner(f"Analyzing resume for {position} position..."):
                        success, result = dashboard.screen_resume(uploaded_file, department, position)
                    
                    if success:
                        st.session_state['resume_result'] = result
                        st.session_state['selected_position'] = {
                            'department': department,
                            'position': position,
                            'requirements': JOB_POSITIONS[department][position]
                        }
                    else:
                        st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
        
        with col2:
            if 'resume_result' in st.session_state:
                result = st.session_state['resume_result']
                
                if result.get('success'):
                    # Display results
                    st.success("Analysis Complete!")
                    
                    # Score visualization
                    score = result.get('final_score', 0)
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = score*100,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Match Score"},
                        gauge = {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 80], 'color': "yellow"},
                                {'range': [80, 100], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Candidate details
                    st.subheader("Candidate Profile")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Name:** {result.get('candidate_name', 'N/A')}")
                        st.write(f"**Email:** {result.get('candidate_email', 'N/A')}")
                    with col_b:
                        st.write(f"**Recommendation:** {result.get('recommendation', 'N/A').replace('_', ' ').title()}")
                        st.write(f"**Interview:** {'✅ Yes' if result.get('interview_recommended') else '❌ No'}")
                    
                    # Strengths and concerns
                    col_c, col_d = st.columns(2)
                    with col_c:
                        st.write("**Strengths:**")
                        strengths = result.get('strengths', [])
                        if strengths:
                            for strength in strengths[:5]:
                                st.write(f"• {strength}")
                        else:
                            st.write("No specific strengths identified")
                    
                    with col_d:
                        st.write("**Areas of Concern:**")
                        concerns = result.get('concerns', [])
                        if concerns:
                            for concern in concerns[:5]:
                                st.write(f"• {concern}")
                        else:
                            st.write("No major concerns identified")
                    
                    # Missing skills
                    missing_skills = result.get('missing_skills', [])
                    if missing_skills:
                        st.write("**Missing Skills:**")
                        st.write(", ".join(missing_skills[:10]))
                else:
                    st.error(f"Screening failed: {result.get('error', 'Unknown error')}")
    
    # Sentiment Analysis Tab
    with tab2:
        st.header("Employee Sentiment Analysis")
        st.write("Analyze employee feedback to predict attrition risk and recommend actions")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Employee Information")
            employee_id = st.text_input("Employee ID", value="EMP001")
            department = st.selectbox("Department", [
                "Engineering", "Marketing", "Sales", "HR", "Finance", 
                "Product", "Customer Support", "Operations", "Design"
            ])
            position = st.text_input("Position", value="Software Engineer")
            tenure_months = st.slider("Tenure (months)", 1, 60, 12)
            manager_rating = st.slider("Manager Rating", 1, 5, 3)
            performance_rating = st.slider("Performance Rating", 1, 5, 3)
            
            st.subheader("Feedback Text")
            feedback_text = st.text_area(
                "Employee Feedback",
                placeholder="Enter employee feedback, survey responses, or exit interview notes...",
                height=200
            )
            
            if st.button("🔍 Analyze Sentiment", type="primary"):
                if feedback_text.strip():
                    feedback_data = {
                        "feedback_text": feedback_text,
                        "employee_id": employee_id,
                        "department": department,
                        "position": position,
                        "tenure_months": tenure_months,
                        "manager_rating": manager_rating,
                        "performance_rating": performance_rating
                    }
                    
                    with st.spinner("Analyzing sentiment..."):
                        success, result = dashboard.analyze_sentiment(feedback_data)
                    
                    if success:
                        st.session_state['sentiment_result'] = result
                    else:
                        st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
                else:
                    st.warning("Please enter feedback text")
        
        with col2:
            if 'sentiment_result' in st.session_state:
                result = st.session_state['sentiment_result']
                
                if result.get('success'):
                    st.success("Analysis Complete!")
                    
                    # Sentiment and risk visualization
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        sentiment = result.get('sentiment', 'unknown')
                        confidence = result.get('confidence_score', 0)
                        
                        # Convert confidence to percentage (0-100)
                        confidence_percent = confidence * 100 if confidence <= 1 else confidence
                        
                        # Sentiment gauge
                        sentiment_colors = {
                            'positive': 'green',
                            'neutral': 'yellow', 
                            'negative': 'red',
                            'unknown': 'gray'
                        }
                        
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = confidence_percent,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': f"Sentiment: {sentiment.title()}<br>Confidence (%)"},
                            gauge = {
                                'axis': {'range': [0, 100]},
                                'bar': {'color': sentiment_colors.get(sentiment, 'gray')},
                                'steps': [
                                    {'range': [0, 30], 'color': "lightgray"},
                                    {'range': [30, 70], 'color': "yellow"},
                                    {'range': [70, 100], 'color': "green"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': confidence_percent
                                }
                            },
                            number = {'suffix': "%"}
                        ))
                        fig.update_layout(height=250)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col_b:
                        risk_level = result.get('attrition_risk', 'unknown')
                        risk_score = result.get('attrition_risk_score', 0)
                        
                        # Convert risk score to percentage (0-100)
                        risk_percent = risk_score * 100 if risk_score <= 1 else risk_score
                        
                        # Risk level visualization
                        risk_colors = {
                            'low': 'green',
                            'medium': 'yellow',
                            'high': 'red',
                            'unknown': 'gray'
                        }
                        
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = risk_percent,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': f"Attrition Risk: {risk_level.title()}<br>Risk Score (%)"},
                            gauge = {
                                'axis': {'range': [0, 100]},
                                'bar': {'color': risk_colors.get(risk_level, 'gray')},
                                'steps': [
                                    {'range': [0, 30], 'color': "green"},
                                    {'range': [30, 70], 'color': "yellow"},
                                    {'range': [70, 100], 'color': "red"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': risk_percent
                                }
                            },
                            number = {'suffix': "%"}
                        ))
                        fig.update_layout(height=250)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Key insights
                    st.subheader("Key Insights")
                    
                    col_c, col_d = st.columns(2)
                    with col_c:
                        st.write("**Key Concerns:**")
                        concerns = result.get('key_concerns', [])
                        if concerns:
                            for concern in concerns:
                                st.write(f"⚠️ {concern}")
                        else:
                            st.write("No major concerns identified")
                    
                    with col_d:
                        st.write("**Positive Indicators:**")
                        positives = result.get('positive_indicators', [])
                        if positives:
                            for positive in positives:
                                st.write(f"✅ {positive}")
                        else:
                            st.write("No specific positive indicators")
                    
                    # Recommended actions
                    st.subheader("Recommended Actions")
                    actions = result.get('recommended_actions', [])
                    if actions:
                        for i, action in enumerate(actions, 1):
                            # Handle both string and object formats
                            if isinstance(action, dict):
                                action_text = action.get('action', str(action))
                            else:
                                action_text = str(action)
                            st.write(f"{i}. {action_text}")
                    else:
                        st.write("No specific actions recommended")
                else:
                    st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
    
    # Batch Processing Tab
    with tab3:
        st.header("Batch Sentiment Processing")
        st.write("Process multiple employee feedback entries at once")
        
        # Sample data template
        st.subheader("Upload Batch Data")
        
        # CSV upload option
        uploaded_csv = st.file_uploader("Upload CSV file", type=['csv'])
        
        if uploaded_csv is not None:
            try:
                df = pd.read_csv(uploaded_csv)
                st.write("**Uploaded Data Preview:**")
                st.dataframe(df.head())
                
                # Validate required columns
                required_columns = ['employee_id', 'feedback_text', 'department']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {missing_columns}")
                else:
                    if st.button("🚀 Process Batch", type="primary"):
                        # Prepare batch data
                        feedback_entries = []
                        for _, row in df.iterrows():
                            entry = {
                                "employee_id": row.get('employee_id', 'Unknown'),
                                "feedback_text": row.get('feedback_text', ''),
                                "department": row.get('department', 'Unknown'),
                                "position": row.get('position', 'Unknown'),
                                "tenure_months": int(row.get('tenure_months', 12)),
                                "manager_rating": int(row.get('manager_rating', 3)),
                                "performance_rating": int(row.get('performance_rating', 3))
                            }
                            feedback_entries.append(entry)
                        
                        # Limit batch size for demo
                        if len(feedback_entries) > 10:
                            st.warning(f"Processing first 10 entries out of {len(feedback_entries)} for demo purposes")
                            feedback_entries = feedback_entries[:10]
                        
                        with st.spinner(f"Processing {len(feedback_entries)} entries..."):
                            success, result = dashboard.batch_analyze_sentiment(feedback_entries)
                        
                        if success:
                            st.session_state['batch_result'] = result
                        else:
                            st.error(f"Batch processing failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
        
        # Display batch results
        if 'batch_result' in st.session_state:
            result = st.session_state['batch_result']
            
            st.success(f"Processed {result.get('successful_analyses', 0)} entries successfully")
            
            # Summary statistics
            summary = result.get('summary', {})
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Sentiment Distribution")
                sentiment_dist = summary.get('sentiment_distribution', {})
                if sentiment_dist:
                    fig = px.pie(
                        values=list(sentiment_dist.values()),
                        names=list(sentiment_dist.keys()),
                        title="Sentiment Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Risk Distribution") 
                risk_dist = summary.get('risk_distribution', {})
                if risk_dist:
                    fig = px.pie(
                        values=list(risk_dist.values()),
                        names=list(risk_dist.keys()),
                        title="Attrition Risk Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Detailed results
            st.subheader("Detailed Results")
            detailed_results = result.get('results', [])
            if detailed_results:
                results_df = pd.DataFrame([
                    {
                        'Employee ID': r.get('employee_id', 'Unknown'),
                        'Sentiment': r.get('sentiment', 'Unknown'),
                        'Risk Level': r.get('attrition_risk', 'Unknown'),
                        'Success': r.get('success', False)
                    }
                    for r in detailed_results
                ])
                st.dataframe(results_df, use_container_width=True)
    
    # Analytics Dashboard Tab  
    with tab4:
        st.header("Analytics Dashboard")
        st.write("System performance metrics and insights")
        
        # Mock analytics data for demonstration
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Resumes Processed", "156", "12")
        with col2:
            st.metric("Average Match Score", "68.5", "2.3")
        with col3:
            st.metric("High-Risk Employees", "23", "-5")
        
        # Sample charts
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Sample processing trends
            dates = pd.date_range(start='2024-01-01', end='2024-09-14', freq='D')
            processed = [20 + i % 15 + (i // 7) % 10 for i in range(len(dates))]
            
            fig = px.line(
                x=dates,
                y=processed,
                title="Daily Processing Volume",
                labels={'x': 'Date', 'y': 'Documents Processed'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_b:
            # Sample department breakdown
            departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance']
            risk_levels = [15, 8, 12, 3, 7]
            
            fig = px.bar(
                x=departments,
                y=risk_levels,
                title="High-Risk Employees by Department",
                labels={'x': 'Department', 'y': 'High-Risk Count'}
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()