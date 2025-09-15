"""
Resume generator for creating diverse sample resumes
"""

import random
from pathlib import Path
import yaml

class ResumeGenerator:
    def __init__(self):
        self.names = [
            "Alex Chen", "Maria Rodriguez", "David Wilson", "Priya Patel",
            "James Thompson", "Lisa Wang", "Carlos Mendez", "Amy Foster",
            "Michael Brown", "Zara Khan", "Ryan O'Connor", "Nina Johansson"
        ]
        
        self.programming_languages = [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
            "PHP", "Ruby", "Kotlin", "Swift", "Scala", "R", "MATLAB"
        ]
        
        self.frameworks = [
            "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot",
            "Laravel", "Ruby on Rails", "ASP.NET", "Express.js", "FastAPI", "Svelte"
        ]
        
        self.databases = [
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle",
            "Cassandra", "Neo4j", "DynamoDB", "InfluxDB", "MariaDB"
        ]
        
        self.cloud_platforms = [
            "AWS", "Azure", "Google Cloud", "Heroku", "DigitalOcean", 
            "Vercel", "Netlify", "Firebase"
        ]
        
        self.universities = [
            "State University", "Tech Institute", "Community College", 
            "Engineering University", "Computer Science College", "Online University"
        ]
        
        self.companies = [
            "TechCorp", "StartupXYZ", "BigTech Inc", "InnovateLab", "CodeFactory",
            "DataSystems", "CloudWorks", "DevSolutions", "AgileTeam", "ScaleUp"
        ]

    def generate_skill_level(self, base_experience_years):
        """Generate skills based on experience level"""
        if base_experience_years >= 5:
            return {
                "programming_languages": random.sample(self.programming_languages, random.randint(4, 7)),
                "frameworks": random.sample(self.frameworks, random.randint(3, 6)),
                "databases": random.sample(self.databases, random.randint(2, 5)),
                "cloud_platforms": random.sample(self.cloud_platforms, random.randint(2, 4))
            }
        elif base_experience_years >= 2:
            return {
                "programming_languages": random.sample(self.programming_languages, random.randint(2, 4)),
                "frameworks": random.sample(self.frameworks, random.randint(2, 4)),
                "databases": random.sample(self.databases, random.randint(1, 3)),
                "cloud_platforms": random.sample(self.cloud_platforms, random.randint(1, 2))
            }
        else:
            return {
                "programming_languages": random.sample(self.programming_languages, random.randint(1, 2)),
                "frameworks": random.sample(self.frameworks, random.randint(1, 2)),
                "databases": random.sample(self.databases, random.randint(0, 2)),
                "cloud_platforms": random.sample(self.cloud_platforms, random.randint(0, 1))
            }

    def generate_resume(self, experience_years=None):
        """Generate a single resume"""
        if experience_years is None:
            experience_years = random.randint(0, 10)
        
        name = random.choice(self.names)
        skills = self.generate_skill_level(experience_years)
        
        # Generate work experience
        experiences = []
        current_year = 2024
        years_left = experience_years
        
        while years_left > 0:
            job_duration = min(random.randint(1, 4), years_left)
            start_year = current_year - years_left
            end_year = start_year + job_duration
            
            company = random.choice(self.companies)
            if experience_years >= 5:
                position = random.choice(["Senior Software Engineer", "Lead Developer", "Tech Lead"])
            elif experience_years >= 2:
                position = random.choice(["Software Engineer", "Full Stack Developer", "Backend Developer"])
            else:
                position = random.choice(["Junior Developer", "Software Developer Intern", "Junior Software Engineer"])
            
            experiences.append({
                "position": position,
                "company": company,
                "start_year": start_year,
                "end_year": end_year if end_year < 2024 else "Present"
            })
            
            years_left -= job_duration
            current_year = start_year
        
        return {
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}@email.com",
            "experience_years": experience_years,
            "skills": skills,
            "experiences": experiences,
            "education": {
                "degree": random.choice(["Bachelor's", "Master's"]),
                "field": random.choice(["Computer Science", "Software Engineering", "Information Technology", "Mathematics", "Electrical Engineering"]),
                "university": random.choice(self.universities)
            }
        }

    def generate_resume_text(self, resume_data):
        """Convert resume data to text format"""
        name = resume_data["name"]
        email = resume_data["email"]
        skills = resume_data["skills"]
        experiences = resume_data["experiences"]
        education = resume_data["education"]
        
        text = f"""{name.upper()}
Software Engineer
Email: {email} | Phone: (555) {random.randint(100, 999)}-{random.randint(1000, 9999)}

PROFESSIONAL SUMMARY
Software Engineer with {resume_data['experience_years']} years of experience in full-stack development.
Experienced in building scalable applications and working with modern development practices.

TECHNICAL SKILLS
- Programming Languages: {', '.join(skills.get('programming_languages', []))}
- Frameworks: {', '.join(skills.get('frameworks', []))}
- Databases: {', '.join(skills.get('databases', []))}
- Cloud Platforms: {', '.join(skills.get('cloud_platforms', []))}
- Tools: Git, Docker, Jenkins, JIRA

PROFESSIONAL EXPERIENCE
"""
        
        for exp in experiences:
            text += f"\n{exp['position']} | {exp['company']} | {exp['start_year']} - {exp['end_year']}\n"
            text += f"- Developed and maintained web applications\n"
            text += f"- Collaborated with cross-functional teams\n"
            text += f"- Participated in code reviews and testing\n"
        
        text += f"""
EDUCATION
{education['degree']} in {education['field']}
{education['university']} | 2015 - 2019
"""
        
        return text

    def generate_multiple_resumes(self, count=20):
        """Generate multiple resume files"""
        resumes_dir = Path("data/resumes")
        resumes_dir.mkdir(exist_ok=True)
        
        for i in range(count):
            # Vary experience levels
            if i < count // 3:
                exp_years = random.randint(0, 2)  # Junior
            elif i < 2 * count // 3:
                exp_years = random.randint(3, 5)  # Mid-level
            else:
                exp_years = random.randint(6, 10)  # Senior
            
            resume_data = self.generate_resume(exp_years)
            resume_text = self.generate_resume_text(resume_data)
            
            filename = f"{resume_data['name'].lower().replace(' ', '_')}_resume.txt"
            filepath = resumes_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(resume_text)
            
            print(f"Generated: {filename} ({exp_years} years experience)")

if __name__ == "__main__":
    generator = ResumeGenerator()
    generator.generate_multiple_resumes(25)
    print("Resume generation complete!")