"""
Job positions configuration for HR-Tech Challenge
"""

JOB_POSITIONS = {
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
        },
        "Frontend Developer": {
            "required_skills": {
                "programming_languages": ["JavaScript", "TypeScript", "HTML", "CSS"],
                "frameworks": ["React", "Vue.js", "Angular", "Next.js"],
                "databases": ["Firebase", "MongoDB"],
                "cloud_platforms": ["Netlify", "Vercel", "AWS S3"],
                "tools": ["Git", "Webpack", "NPM", "Figma"]
            },
            "required_experience": {"min_years": 2, "max_years": 6},
            "required_education": {
                "degree": "Bachelor's",
                "field": ["Computer Science", "Web Development", "Design"]
            },
            "salary_range": {"min": 70000, "max": 110000}
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
    },
    "Marketing": {
        "Digital Marketing Manager": {
            "required_skills": {
                "programming_languages": ["Basic HTML", "CSS"],
                "frameworks": ["Google Analytics", "Facebook Ads Manager", "HubSpot"],
                "databases": ["CRM Systems"],
                "cloud_platforms": ["Google Cloud", "AWS"],
                "tools": ["Google Ads", "SEMrush", "Hootsuite", "Canva"]
            },
            "required_experience": {"min_years": 3, "max_years": 7},
            "required_education": {
                "degree": "Bachelor's",
                "field": ["Marketing", "Business", "Communications"]
            },
            "salary_range": {"min": 60000, "max": 95000}
        }
    }
}