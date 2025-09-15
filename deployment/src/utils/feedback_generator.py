"""
Employee feedback generator for sentiment analysis training data
"""

import random
import pandas as pd
from datetime import datetime, timedelta
import yaml
from pathlib import Path

class FeedbackGenerator:
    def __init__(self):
        self.departments = [
            "Engineering", "Marketing", "Sales", "HR", "Finance", 
            "Product", "Customer Support", "Operations", "Design"
        ]
        
        self.positions = {
            "Engineering": ["Software Engineer", "Senior Engineer", "Tech Lead", "Engineering Manager"],
            "Marketing": ["Marketing Specialist", "Marketing Manager", "Content Creator", "SEO Specialist"],
            "Sales": ["Sales Rep", "Account Manager", "Sales Manager", "Business Development"],
            "HR": ["HR Specialist", "Recruiter", "HR Manager", "People Operations"],
            "Finance": ["Financial Analyst", "Accountant", "Finance Manager", "Controller"],
            "Product": ["Product Manager", "Product Owner", "UX Designer", "Product Analyst"],
            "Customer Support": ["Support Specialist", "Support Manager", "Customer Success Manager"],
            "Operations": ["Operations Manager", "Project Manager", "Operations Analyst"],
            "Design": ["UI Designer", "UX Designer", "Graphic Designer", "Design Manager"]
        }
        
        self.positive_feedback = [
            "I absolutely love working here! The team is supportive and the projects are challenging.",
            "Great work-life balance and excellent career growth opportunities.",
            "Management is very supportive and listens to employee feedback.",
            "The company culture is amazing - collaborative and innovative.",
            "I feel valued and appreciated for my contributions.",
            "Excellent benefits package and competitive salary.",
            "Learning opportunities are abundant and encouraged.",
            "The workspace is modern and conducive to productivity.",
            "Strong team collaboration and knowledge sharing.",
            "Regular feedback and recognition from leadership."
        ]
        
        self.neutral_feedback = [
            "The work is interesting but can be repetitive at times.",
            "Management is decent, though communication could be improved.",
            "Good benefits but salary could be more competitive.",
            "The workload is manageable most of the time.",
            "Some projects are exciting, others not so much.",
            "Decent work environment with room for improvement.",
            "Career growth opportunities exist but are limited.",
            "The team is okay, some great people, some challenges.",
            "Work-life balance is acceptable but could be better.",
            "Company is stable but not particularly innovative."
        ]
        
        self.negative_feedback = [
            "The workload is overwhelming and unsustainable.",
            "Management doesn't listen to employee concerns.",
            "No clear career advancement opportunities available.",
            "Work-life balance is terrible - constantly working late.",
            "Feeling undervalued and underpaid for the work I do.",
            "Toxic work environment with poor communication.",
            "Outdated tools and processes make work inefficient.",
            "Lack of recognition for good work and achievements.",
            "High stress levels due to unrealistic deadlines.",
            "Considering leaving due to lack of growth opportunities."
        ]
        
        self.exit_interview_feedback = [
            "The main reason I'm leaving is lack of career growth opportunities.",
            "Workload became unmanageable and affected my personal life.",
            "Found a better opportunity with higher compensation elsewhere.",
            "Management style didn't align with my working preferences.",
            "Limited learning and development opportunities available.",
            "Work became monotonous without new challenges.",
            "Better work-life balance offered by new company.",
            "Seeking more responsibility and leadership opportunities.",
            "Company direction and my career goals don't align.",
            "Relocating for personal reasons but enjoyed working here."
        ]

    def generate_employee_data(self, num_employees=200):
        """Generate employee demographic data"""
        employees = []
        
        for i in range(num_employees):
            dept = random.choice(self.departments)
            position = random.choice(self.positions[dept])
            tenure_months = random.randint(1, 60)  # 1 month to 5 years
            
            employee = {
                "employee_id": f"EMP{i+1:04d}",
                "department": dept,
                "position": position,
                "tenure_months": tenure_months,
                "manager_rating": random.randint(1, 5),
                "performance_rating": random.choice([2, 3, 3, 4, 4, 5])  # Weighted toward higher performance
            }
            
            employees.append(employee)
        
        return employees

    def generate_feedback_entry(self, employee, feedback_type="survey"):
        """Generate a single feedback entry"""
        
        # Determine sentiment based on tenure and ratings
        if employee['manager_rating'] >= 4 and employee['performance_rating'] >= 4:
            sentiment_bias = "positive"
        elif employee['manager_rating'] <= 2 or employee['performance_rating'] <= 2:
            sentiment_bias = "negative"
        else:
            sentiment_bias = "neutral"
        
        # Add some randomness
        sentiment_choices = {
            "positive": ["positive", "neutral", "negative"],
            "neutral": ["neutral", "positive", "negative"],
            "negative": ["negative", "neutral", "positive"]
        }
        
        weights = {
            "positive": [0.7, 0.2, 0.1],
            "neutral": [0.6, 0.3, 0.1],
            "negative": [0.1, 0.2, 0.7]
        }
        
        sentiment = random.choices(
            sentiment_choices[sentiment_bias],
            weights=weights[sentiment_bias]
        )[0]
        
        # Select feedback based on sentiment
        if sentiment == "positive":
            feedback_text = random.choice(self.positive_feedback)
            rating = random.randint(4, 5)
        elif sentiment == "negative":
            if feedback_type == "exit_interview":
                feedback_text = random.choice(self.exit_interview_feedback)
            else:
                feedback_text = random.choice(self.negative_feedback)
            rating = random.randint(1, 2)
        else:
            feedback_text = random.choice(self.neutral_feedback)
            rating = 3
        
        # Generate date within last year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        return {
            "employee_id": employee["employee_id"],
            "feedback_date": random_date.strftime("%Y-%m-%d"),
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "rating": rating,
            "sentiment": sentiment,
            "department": employee["department"],
            "position": employee["position"],
            "tenure_months": employee["tenure_months"],
            "manager_rating": employee["manager_rating"],
            "performance_rating": employee["performance_rating"]
        }

    def generate_feedback_dataset(self, num_employees=200, feedback_per_employee=3):
        """Generate complete feedback dataset"""
        employees = self.generate_employee_data(num_employees)
        all_feedback = []
        
        for employee in employees:
            # Generate regular feedback
            for _ in range(feedback_per_employee):
                feedback_type = random.choice(["survey", "performance_review", "team_feedback"])
                feedback = self.generate_feedback_entry(employee, feedback_type)
                all_feedback.append(feedback)
            
            # 10% chance of exit interview
            if random.random() < 0.1:
                exit_feedback = self.generate_feedback_entry(employee, "exit_interview")
                all_feedback.append(exit_feedback)
        
        return pd.DataFrame(all_feedback)

    def save_datasets(self):
        """Save generated datasets to files"""
        feedback_dir = Path("data/employee_feedback")
        feedback_dir.mkdir(exist_ok=True)
        
        # Generate and save feedback dataset
        df = self.generate_feedback_dataset()
        
        # Save as CSV
        df.to_csv(feedback_dir / "employee_feedback.csv", index=False)
        
        # Save summary statistics
        summary = {
            "total_feedback_entries": len(df),
            "unique_employees": df["employee_id"].nunique(),
            "sentiment_distribution": df["sentiment"].value_counts().to_dict(),
            "feedback_type_distribution": df["feedback_type"].value_counts().to_dict(),
            "department_distribution": df["department"].value_counts().to_dict()
        }
        
        with open(feedback_dir / "dataset_summary.yaml", "w") as f:
            yaml.dump(summary, f, default_flow_style=False)
        
        print(f"Generated {len(df)} feedback entries from {df['employee_id'].nunique()} employees")
        print(f"Sentiment distribution: {summary['sentiment_distribution']}")
        
        return df

if __name__ == "__main__":
    generator = FeedbackGenerator()
    df = generator.save_datasets()
    print("Employee feedback dataset generation complete!")