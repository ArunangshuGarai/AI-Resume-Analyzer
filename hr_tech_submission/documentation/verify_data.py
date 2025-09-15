"""
Script to verify all sample data has been generated correctly
"""

import os
from pathlib import Path
import pandas as pd
import yaml

def check_project_data():
    """Verify all required data files exist and are properly formatted"""
    
    print("🔍 Checking HR-Tech Challenge Data Generation")
    print("=" * 60)
    
    # Check directories
    data_dirs = [
        "data/resumes",
        "data/job_descriptions", 
        "data/employee_feedback"
    ]
    
    for dir_path in data_dirs:
        if Path(dir_path).exists():
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")
    
    print("\n📄 Checking Resume Data:")
    print("-" * 30)
    
    # Check resumes
    resumes_dir = Path("data/resumes")
    if resumes_dir.exists():
        resume_files = list(resumes_dir.glob("*.txt"))
        print(f"✅ Found {len(resume_files)} resume files")
        
        # Show sample resume files
        for i, resume_file in enumerate(resume_files[:5]):
            file_size = resume_file.stat().st_size
            print(f"   📝 {resume_file.name} ({file_size} bytes)")
        
        if len(resume_files) > 5:
            print(f"   ... and {len(resume_files) - 5} more resume files")
    else:
        print("❌ No resumes directory found")
    
    print("\n📋 Checking Job Description Data:")
    print("-" * 35)
    
    # Check job descriptions
    job_desc_dir = Path("data/job_descriptions")
    if job_desc_dir.exists():
        job_files = list(job_desc_dir.glob("*.yaml"))
        print(f"✅ Found {len(job_files)} job description files")
        
        for job_file in job_files:
            print(f"   📄 {job_file.name}")
            
            # Try to parse YAML
            try:
                with open(job_file, 'r') as f:
                    job_data = yaml.safe_load(f)
                    if 'required_skills' in job_data:
                        print(f"      ✅ Valid job description with skills")
                    else:
                        print(f"      ⚠️ Missing required_skills section")
            except Exception as e:
                print(f"      ❌ YAML parsing error: {str(e)}")
    else:
        print("❌ No job descriptions directory found")
    
    print("\n💬 Checking Employee Feedback Data:")
    print("-" * 37)
    
    # Check employee feedback
    feedback_dir = Path("data/employee_feedback")
    if feedback_dir.exists():
        csv_files = list(feedback_dir.glob("*.csv"))
        yaml_files = list(feedback_dir.glob("*.yaml"))
        
        print(f"✅ Found {len(csv_files)} CSV files and {len(yaml_files)} YAML files")
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                print(f"   📊 {csv_file.name}: {len(df)} rows, {len(df.columns)} columns")
                
                # Check required columns
                required_columns = ['employee_id', 'feedback_text', 'sentiment', 'rating']
                missing_cols = [col for col in required_columns if col not in df.columns]
                
                if missing_cols:
                    print(f"      ⚠️ Missing columns: {missing_cols}")
                else:
                    print(f"      ✅ All required columns present")
                
                # Show sentiment distribution
                if 'sentiment' in df.columns:
                    sentiment_counts = df['sentiment'].value_counts()
                    print(f"      📈 Sentiment distribution: {dict(sentiment_counts)}")
                
            except Exception as e:
                print(f"      ❌ CSV reading error: {str(e)}")
        
        for yaml_file in yaml_files:
            print(f"   📄 {yaml_file.name}")
    else:
        print("❌ No employee feedback directory found")
    
    print("\n🎯 Data Quality Summary:")
    print("-" * 25)
    
    # Summary statistics
    total_files = 0
    
    if resumes_dir.exists():
        resume_count = len(list(resumes_dir.glob("*.txt")))
        total_files += resume_count
        print(f"📝 Resume files: {resume_count}")
    
    if job_desc_dir.exists():
        job_count = len(list(job_desc_dir.glob("*.yaml")))
        total_files += job_count
        print(f"📋 Job description files: {job_count}")
    
    if feedback_dir.exists():
        feedback_count = len(list(feedback_dir.glob("*.csv")))
        total_files += feedback_count
        print(f"💬 Feedback data files: {feedback_count}")
    
    print(f"📊 Total data files: {total_files}")
    
    # Check if we have minimum required data
    min_requirements = {
        "resumes": 10,
        "job_descriptions": 1,
        "feedback_entries": 100
    }
    
    print(f"\n✅ Minimum Requirements Check:")
    print(f"-" * 32)
    
    # Check resumes
    if resumes_dir.exists():
        resume_count = len(list(resumes_dir.glob("*.txt")))
        status = "✅" if resume_count >= min_requirements["resumes"] else "⚠️"
        print(f"{status} Resumes: {resume_count}/{min_requirements['resumes']} minimum")
    
    # Check job descriptions
    if job_desc_dir.exists():
        job_count = len(list(job_desc_dir.glob("*.yaml")))
        status = "✅" if job_count >= min_requirements["job_descriptions"] else "⚠️"
        print(f"{status} Job descriptions: {job_count}/{min_requirements['job_descriptions']} minimum")
    
    # Check feedback entries
    if feedback_dir.exists() and (feedback_dir / "employee_feedback.csv").exists():
        try:
            df = pd.read_csv(feedback_dir / "employee_feedback.csv")
            feedback_count = len(df)
            status = "✅" if feedback_count >= min_requirements["feedback_entries"] else "⚠️"
            print(f"{status} Feedback entries: {feedback_count}/{min_requirements['feedback_entries']} minimum")
        except:
            print(f"⚠️ Could not read feedback data")
    
    print(f"\n🎉 Phase 2 Data Generation Status:")
    print(f"{'=' * 35}")
    
    # Overall status
    all_good = True
    
    if not resumes_dir.exists() or len(list(resumes_dir.glob("*.txt"))) < 10:
        all_good = False
        print("⚠️ Need more resume files")
    
    if not job_desc_dir.exists() or len(list(job_desc_dir.glob("*.yaml"))) < 1:
        all_good = False
        print("⚠️ Need job description file")
    
    if not feedback_dir.exists() or not (feedback_dir / "employee_feedback.csv").exists():
        all_good = False
        print("⚠️ Need employee feedback data")
    
    if all_good:
        print("🎉 ALL DATA READY! Phase 2 complete - Ready for Phase 3!")
        print("Next: Start building the AI models and prompt engineering")
    else:
        print("📋 Please complete the missing data generation steps above")
    
    return all_good

def show_sample_data():
    """Show samples of generated data"""
    print(f"\n📖 Sample Data Preview:")
    print(f"=" * 25)
    
    # Show sample resume
    resumes_dir = Path("data/resumes")
    if resumes_dir.exists():
        resume_files = list(resumes_dir.glob("*.txt"))
        if resume_files:
            print(f"\n📝 Sample Resume ({resume_files[0].name}):")
            print("-" * 40)
            with open(resume_files[0], 'r') as f:
                content = f.read()
                # Show first 300 characters
                print(content[:300] + "..." if len(content) > 300 else content)
    
    # Show sample feedback
    feedback_file = Path("data/employee_feedback/employee_feedback.csv")
    if feedback_file.exists():
        print(f"\n💬 Sample Employee Feedback:")
        print("-" * 32)
        try:
            df = pd.read_csv(feedback_file)
            # Show first few rows with key columns
            key_cols = ['employee_id', 'sentiment', 'rating', 'feedback_text']
            available_cols = [col for col in key_cols if col in df.columns]
            
            if available_cols:
                sample_df = df[available_cols].head(3)
                for _, row in sample_df.iterrows():
                    print(f"ID: {row.get('employee_id', 'N/A')}")
                    print(f"Sentiment: {row.get('sentiment', 'N/A')} | Rating: {row.get('rating', 'N/A')}")
                    feedback_text = row.get('feedback_text', 'N/A')
                    print(f"Feedback: {feedback_text[:100]}{'...' if len(feedback_text) > 100 else ''}")
                    print("-" * 40)
        except Exception as e:
            print(f"Error reading feedback data: {str(e)}")

if __name__ == "__main__":
    data_ready = check_project_data()
    
    if data_ready:
        show_sample_data()
        
        print(f"\n🚀 Ready for Phase 3: AI Model Development!")
        print("Run: python -c \"print('Phase 2 Complete - Data Ready!')\"")
    else:
        print(f"\n📋 Complete remaining data generation tasks first")
        print("Then re-run: python verify_data.py")