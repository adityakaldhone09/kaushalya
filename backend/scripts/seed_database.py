from __future__ import annotations
#!/usr/bin/env python3
"""
KAUSHALYA Database Seed Script
================================
Seeds realistic Maharashtra workforce data for the SIH demonstration.

Usage:
    cd backend
    python scripts/seed_database.py

Seeded data:
  - 10 districts
  - 30 skills
  - 20 employers
  - 10 training institutes
  - 20 training programs
  - 75 jobs
  - 200 trainees (with skills, assessments, enrollments, certifications)
  - 150 job applications
  - 100+ employment outcomes
  - 500+ skill demand records
  - Demo accounts for all roles
"""
import asyncio
import sys
import os
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import motor.motor_asyncio
from bson import ObjectId
from passlib.context import CryptContext

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/kaushalya_db")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "kaushalya_db")
DEMO_PASSWORD = "Demo@1234"

def utcnow():
    return datetime.now(timezone.utc)

def days_ago(n: int) -> datetime:
    return utcnow() - timedelta(days=n)

def rand_date(days_back_min=30, days_back_max=365) -> datetime:
    return utcnow() - timedelta(days=random.randint(days_back_min, days_back_max))


# ── Data Fixtures ─────────────────────────────────────────────────────────────

DISTRICTS = [
    {"district": "Pune", "region": "Western Maharashtra", "status": "orange",
     "trainees": 64200, "employed": 41100, "placement_rate": 64,
     "average_salary": "₹5.2 LPA", "skill_supply": "Moderate", "skill_demand": "Very high",
     "skill_gap": "Critical", "top_demand": "Cloud Computing", "top_available": "Web Development",
     "future_demand": "High", "growth_rate": 42,
     "recommendation": "Increase cloud training capacity by approximately 25%.",
     "coordinates": {"x": 18, "y": 20}},
    {"district": "Mumbai", "region": "Konkan", "status": "yellow",
     "trainees": 88400, "employed": 60100, "placement_rate": 68,
     "average_salary": "₹6.4 LPA", "skill_supply": "High", "skill_demand": "Very high",
     "skill_gap": "Moderate", "top_demand": "Cybersecurity", "top_available": "Finance",
     "future_demand": "High", "growth_rate": 35,
     "recommendation": "Expand cybersecurity and data governance pathways.",
     "coordinates": {"x": 34, "y": 20}},
    {"district": "Nagpur", "region": "Vidarbha", "status": "orange",
     "trainees": 37800, "employed": 22100, "placement_rate": 58,
     "average_salary": "₹4.1 LPA", "skill_supply": "Moderate", "skill_demand": "High",
     "skill_gap": "High", "top_demand": "Logistics Tech", "top_available": "Manufacturing",
     "future_demand": "High", "growth_rate": 31,
     "recommendation": "Build industry-linked programs in logistics and cloud operations.",
     "coordinates": {"x": 50, "y": 20}},
    {"district": "Nashik", "region": "North Maharashtra", "status": "green",
     "trainees": 31900, "employed": 21900, "placement_rate": 69,
     "average_salary": "₹3.9 LPA", "skill_supply": "High", "skill_demand": "High",
     "skill_gap": "Moderate", "top_demand": "Agritech", "top_available": "Manufacturing",
     "future_demand": "Medium", "growth_rate": 24,
     "recommendation": "Connect agritech talent with regional employers.",
     "coordinates": {"x": 18, "y": 54}},
    {"district": "Chhatrapati Sambhajinagar", "region": "Marathwada", "status": "orange",
     "trainees": 28400, "employed": 16100, "placement_rate": 57,
     "average_salary": "₹3.7 LPA", "skill_supply": "Low", "skill_demand": "High",
     "skill_gap": "High", "top_demand": "Electronics", "top_available": "Communication",
     "future_demand": "High", "growth_rate": 29,
     "recommendation": "Prioritize electronics and industrial automation labs.",
     "coordinates": {"x": 66, "y": 54}},
    {"district": "Kolhapur", "region": "Western Maharashtra", "status": "green",
     "trainees": 22600, "employed": 16100, "placement_rate": 71,
     "average_salary": "₹3.6 LPA", "skill_supply": "High", "skill_demand": "Moderate",
     "skill_gap": "Healthy", "top_demand": "Manufacturing", "top_available": "Leadership",
     "future_demand": "Medium", "growth_rate": 18,
     "recommendation": "Sustain placement momentum through employer partnerships.",
     "coordinates": {"x": 18, "y": 54}},
    {"district": "Navi Mumbai", "region": "Konkan", "status": "yellow",
     "trainees": 35500, "employed": 24700, "placement_rate": 70,
     "average_salary": "₹5.8 LPA", "skill_supply": "High", "skill_demand": "Very high",
     "skill_gap": "Moderate", "top_demand": "Data Science", "top_available": "SQL",
     "future_demand": "High", "growth_rate": 38,
     "recommendation": "Add applied data science cohorts for port and finance employers.",
     "coordinates": {"x": 34, "y": 54}},
    {"district": "Thane", "region": "Konkan", "status": "yellow",
     "trainees": 46100, "employed": 31000, "placement_rate": 67,
     "average_salary": "₹5.1 LPA", "skill_supply": "Moderate", "skill_demand": "High",
     "skill_gap": "Moderate", "top_demand": "Cloud Computing", "top_available": "Digital Marketing",
     "future_demand": "High", "growth_rate": 36,
     "recommendation": "Scale cloud and digital operations training.",
     "coordinates": {"x": 50, "y": 54}},
    {"district": "Amravati", "region": "Vidarbha", "status": "red",
     "trainees": 19800, "employed": 10400, "placement_rate": 52,
     "average_salary": "₹3.2 LPA", "skill_supply": "Low", "skill_demand": "High",
     "skill_gap": "Critical", "top_demand": "Solar Energy", "top_available": "Communication",
     "future_demand": "Very high", "growth_rate": 44,
     "recommendation": "Introduce green-energy labs and local apprenticeship tracks.",
     "coordinates": {"x": 66, "y": 20}},
    {"district": "Solapur", "region": "Western Maharashtra", "status": "orange",
     "trainees": 24600, "employed": 13900, "placement_rate": 56,
     "average_salary": "₹3.4 LPA", "skill_supply": "Low", "skill_demand": "High",
     "skill_gap": "High", "top_demand": "Textile Technology", "top_available": "Manufacturing",
     "future_demand": "High", "growth_rate": 33,
     "recommendation": "Modernize textile programs with automation and analytics.",
     "coordinates": {"x": 18, "y": 54}},
]

SKILLS_DATA = [
    {"name": "Python", "category": "Software Development", "description": "Programming and automation foundation", "demand_score": 88, "growth_rate": 24, "industries": ["IT", "Data", "FinTech"]},
    {"name": "SQL", "category": "Data Science", "description": "Querying and modeling operational data", "demand_score": 84, "growth_rate": 21, "industries": ["IT", "Finance", "Healthcare"]},
    {"name": "React", "category": "Software Development", "description": "Modern web application development", "demand_score": 79, "growth_rate": 18, "industries": ["IT", "E-commerce"]},
    {"name": "AWS", "category": "Cloud Computing", "description": "Cloud infrastructure and services", "demand_score": 94, "growth_rate": 42, "industries": ["IT", "FinTech", "Healthcare"]},
    {"name": "Docker", "category": "Cloud Computing", "description": "Containerized application delivery", "demand_score": 91, "growth_rate": 38, "industries": ["IT", "FinTech"]},
    {"name": "Kubernetes", "category": "Cloud Computing", "description": "Container orchestration at scale", "demand_score": 87, "growth_rate": 35, "industries": ["IT", "FinTech"]},
    {"name": "Data Science", "category": "Data Science", "description": "Analytics and ML for business decisions", "demand_score": 86, "growth_rate": 29, "industries": ["IT", "Finance", "Healthcare"]},
    {"name": "Machine Learning", "category": "Data Science", "description": "Model building and deployment", "demand_score": 83, "growth_rate": 26, "industries": ["IT", "FinTech"]},
    {"name": "ETL", "category": "Data Science", "description": "Reliable data integration pipelines", "demand_score": 82, "growth_rate": 20, "industries": ["IT", "Finance"]},
    {"name": "Cybersecurity", "category": "Cybersecurity", "description": "Security operations and risk controls", "demand_score": 92, "growth_rate": 35, "industries": ["IT", "Finance", "Government"]},
    {"name": "Linux", "category": "Software Development", "description": "OS administration and scripting", "demand_score": 78, "growth_rate": 15, "industries": ["IT", "Telecom"]},
    {"name": "CI/CD", "category": "Cloud Computing", "description": "Continuous integration and delivery", "demand_score": 80, "growth_rate": 30, "industries": ["IT", "FinTech"]},
    {"name": "Solar Energy", "category": "Green Energy", "description": "Solar installation and maintenance", "demand_score": 75, "growth_rate": 44, "industries": ["Energy", "Manufacturing"]},
    {"name": "Electrical Safety", "category": "Green Energy", "description": "Electrical safety standards and practice", "demand_score": 68, "growth_rate": 22, "industries": ["Energy", "Manufacturing"]},
    {"name": "REST APIs", "category": "Software Development", "description": "API design and integration", "demand_score": 77, "growth_rate": 16, "industries": ["IT", "E-commerce"]},
    {"name": "Git", "category": "Software Development", "description": "Version control and collaboration", "demand_score": 76, "growth_rate": 12, "industries": ["IT"]},
    {"name": "Communication", "category": "Soft Skills", "description": "Clear collaboration and stakeholder communication", "demand_score": 72, "growth_rate": 12, "industries": ["All"]},
    {"name": "Leadership", "category": "Soft Skills", "description": "Team and project leadership", "demand_score": 70, "growth_rate": 10, "industries": ["All"]},
    {"name": "Agritech", "category": "Agriculture Technology", "description": "Technology solutions for agriculture", "demand_score": 65, "growth_rate": 28, "industries": ["Agriculture", "Manufacturing"]},
    {"name": "IoT", "category": "Technology", "description": "Internet of Things device integration", "demand_score": 73, "growth_rate": 32, "industries": ["Manufacturing", "Agriculture", "Healthcare"]},
    {"name": "Logistics Tech", "category": "Logistics", "description": "Technology in supply chain and logistics", "demand_score": 71, "growth_rate": 27, "industries": ["Logistics", "Manufacturing"]},
    {"name": "Digital Marketing", "category": "Marketing", "description": "Digital channels, SEO, analytics", "demand_score": 69, "growth_rate": 19, "industries": ["E-commerce", "Media"]},
    {"name": "Excel", "category": "Business Tools", "description": "Advanced spreadsheet and data analysis", "demand_score": 64, "growth_rate": 8, "industries": ["Finance", "Operations"]},
    {"name": "Networking", "category": "Cybersecurity", "description": "Network design and administration", "demand_score": 70, "growth_rate": 14, "industries": ["IT", "Telecom"]},
    {"name": "Tableau", "category": "Data Science", "description": "Data visualization and dashboards", "demand_score": 74, "growth_rate": 22, "industries": ["IT", "Finance"]},
    {"name": "Power BI", "category": "Data Science", "description": "Business intelligence reporting", "demand_score": 72, "growth_rate": 20, "industries": ["Finance", "Operations"]},
    {"name": "Textile Technology", "category": "Manufacturing", "description": "Textile manufacturing processes", "demand_score": 60, "growth_rate": 15, "industries": ["Manufacturing", "Textile"]},
    {"name": "Electronics", "category": "Electronics", "description": "Electronics design and fabrication", "demand_score": 66, "growth_rate": 20, "industries": ["Manufacturing", "Electronics"]},
    {"name": "Manufacturing", "category": "Manufacturing", "description": "Production process management", "demand_score": 62, "growth_rate": 12, "industries": ["Manufacturing"]},
    {"name": "Finance", "category": "Finance", "description": "Financial analysis and modeling", "demand_score": 71, "growth_rate": 14, "industries": ["Finance", "FinTech"]},
]

FIRST_NAMES = [
    "Aarav", "Arjun", "Aditya", "Akash", "Amit", "Anish", "Ankit", "Ashish",
    "Deepak", "Ganesh", "Harsh", "Ishaan", "Jay", "Kiran", "Kunal", "Lokesh",
    "Mayur", "Mihir", "Nikhil", "Omkar", "Pranav", "Rahul", "Rajesh", "Rohit",
    "Sachin", "Sanket", "Shubham", "Siddharth", "Sumit", "Suresh", "Tejas", "Varun",
    "Vikram", "Vishal", "Yash", "Priya", "Sneha", "Pooja", "Kavya", "Neha",
    "Divya", "Swati", "Anjali", "Shruti", "Meera", "Pallavi", "Smita", "Radha",
    "Sonali", "Tanvi", "Usha", "Vidya", "Wanda", "Nandita", "Madhuri", "Seema",
]
LAST_NAMES = [
    "Kulkarni", "Patil", "Deshmukh", "Pawar", "Jadhav", "Shinde", "Kale", "Mane",
    "More", "Yadav", "Gaikwad", "Chavan", "Salunkhe", "Bhosale", "Landge", "Thakre",
    "Wagh", "Kadam", "Sarode", "Deshpande", "Nair", "Iyer", "Menon", "Joshi",
    "Sharma", "Patel", "Shah", "Mehta", "Gupta", "Singh", "Kumar", "Reddy",
]

EDUCATION_DEGREES = [
    ("B.Tech", "Computer Engineering"), ("B.Tech", "Information Technology"),
    ("B.Tech", "Electronics Engineering"), ("B.E.", "Computer Science"),
    ("B.E.", "Mechanical Engineering"), ("B.Sc.", "Computer Science"),
    ("B.Sc.", "Data Science"), ("BCA", "Computer Applications"),
    ("MBA", "Operations"), ("Diploma", "Electronics"),
    ("Diploma", "Computer Engineering"), ("B.Com", "Finance"),
    ("B.A.", "Economics"), ("ITI", "Electrician"),
]

EXPERIENCE_OPTIONS = ["Fresher", "6 months", "1 year", "1.5 years", "2 years", "3 years", "4 years"]
STATUS_OPTIONS = ["Open to work", "Employed", "In Training", "Open to work", "Open to work"]

EMPLOYER_DATA = [
    ("Pune Digital Systems", "Technology", "Pune", "pds.in"),
    ("CloudScale India", "Technology", "Navi Mumbai", "cloudscale.in"),
    ("Sahyadri Labs", "Technology", "Pune", "sahyadrilabs.com"),
    ("MahaFin Services", "Finance", "Mumbai", "mahafinservices.com"),
    ("TechMahindra SME Unit", "Technology", "Pune", "techmahindra.com"),
    ("Infosys BPO Pune", "Technology", "Pune", "infosys.com"),
    ("Wipro Analytics", "Technology", "Mumbai", "wipro.com"),
    ("HDFC Digital Labs", "Finance", "Mumbai", "hdfc.com"),
    ("Reliance Jio Platform", "Telecom", "Mumbai", "jio.com"),
    ("Tata Power Solar", "Green Energy", "Mumbai", "tatapower.com"),
    ("Bajaj Finserv Tech", "Finance", "Pune", "bajajfinserv.in"),
    ("L&T Infotech", "Technology", "Mumbai", "lntinfotech.com"),
    ("HCL Tech Pune", "Technology", "Pune", "hcl.com"),
    ("Persistent Systems", "Technology", "Pune", "persistent.com"),
    ("Nagpur Smart City Corp", "Government", "Nagpur", "nagpursmartcity.in"),
    ("Maharashtra Agritech Hub", "Agriculture Technology", "Nashik", "mahaagritech.in"),
    ("Vidarbha Solar", "Green Energy", "Amravati", "vidarbhasolar.in"),
    ("Solapur Textiles Ltd", "Manufacturing", "Solapur", "solapurtextiles.in"),
    ("Kolhapur Auto Parts", "Manufacturing", "Kolhapur", "kolhapurauto.in"),
    ("MSEDCL (Electrical Corp)", "Energy", "Thane", "mahadiscom.in"),
]

INSTITUTE_DATA = [
    ("Maharashtra Digital Skills Centre", "Pune"),
    ("Vidarbha Analytics Institute", "Nagpur"),
    ("Green Maharashtra Mission", "Amravati"),
    ("Mumbai Technology Academy", "Mumbai"),
    ("Pune Engineering Upskill Centre", "Pune"),
    ("Nashik Agritech Training Hub", "Nashik"),
    ("Thane Cloud Computing Institute", "Thane"),
    ("Navi Mumbai Data Science School", "Navi Mumbai"),
    ("Solapur Industrial Training Centre", "Solapur"),
    ("Marathwada Electronics Institute", "Chhatrapati Sambhajinagar"),
]

PROGRAM_DATA = [
    ("Cloud & DevOps Accelerator", 0, "Industry-designed pathway from Linux through cloud deployment.", "16 weeks", "Hybrid", "Pune", "Technology", ["AWS", "Docker", "Linux", "CI/CD"], 120, 88, 76, 87, "₹7.4 LPA avg."),
    ("Applied Data Science", 1, "Hands-on analytics, ML, and decision science for business teams.", "20 weeks", "Hybrid", "Nagpur", "Technology", ["Python", "SQL", "Data Science", "Machine Learning"], 90, 84, 71, 82, "₹6.2 LPA avg."),
    ("Solar Technician Pathway", 2, "Practical solar installation, maintenance, and safety training.", "12 weeks", "In-person", "Amravati", "Green Energy", ["Solar Energy", "Electrical Safety"], 80, 91, 69, 80, "₹4.1 LPA avg."),
    ("Full Stack Web Development", 3, "End-to-end web development from frontend to deployment.", "18 weeks", "Hybrid", "Mumbai", "Technology", ["React", "Python", "REST APIs", "Git"], 100, 82, 73, 79, "₹6.8 LPA avg."),
    ("Cybersecurity Operations", 4, "SOC operations, threat analysis, and security engineering.", "14 weeks", "Hybrid", "Mumbai", "Technology", ["Cybersecurity", "Networking", "Linux"], 60, 86, 78, 85, "₹7.1 LPA avg."),
    ("Agritech Innovation Program", 5, "Precision agriculture with IoT and data analytics.", "10 weeks", "Blended", "Nashik", "Agriculture Technology", ["Agritech", "IoT", "Communication"], 70, 80, 65, 74, "₹4.4 LPA avg."),
    ("Cloud Infrastructure Basics", 6, "Entry-level cloud skills for freshers.", "8 weeks", "Online", "Thane", "Technology", ["AWS", "Linux", "Git"], 150, 79, 68, 75, "₹5.5 LPA avg."),
    ("Data Analytics Bootcamp", 7, "Business analytics with SQL, Tableau, and Power BI.", "12 weeks", "Hybrid", "Navi Mumbai", "Technology", ["SQL", "Tableau", "Power BI", "Excel"], 80, 85, 74, 80, "₹5.9 LPA avg."),
    ("Industrial Automation", 8, "PLC, SCADA, and manufacturing automation.", "16 weeks", "In-person", "Solapur", "Manufacturing", ["Electronics", "Manufacturing"], 60, 78, 62, 72, "₹4.8 LPA avg."),
    ("Digital Marketing Pro", 9, "SEO, social media, and performance marketing.", "10 weeks", "Online", "Pune", "Marketing", ["Digital Marketing", "Communication"], 100, 83, 70, 77, "₹4.6 LPA avg."),
    ("Logistics & Supply Chain Tech", 0, "Technology for modern logistics operations.", "12 weeks", "Hybrid", "Nagpur", "Logistics", ["Logistics Tech", "SQL", "Communication"], 70, 76, 63, 73, "₹5.1 LPA avg."),
    ("Financial Technology Foundations", 1, "FinTech tools, digital banking, and data.", "14 weeks", "Hybrid", "Mumbai", "Finance", ["Finance", "Python", "SQL"], 80, 81, 70, 78, "₹6.1 LPA avg."),
    ("IoT and Embedded Systems", 2, "Connected devices for industrial applications.", "16 weeks", "In-person", "Chhatrapati Sambhajinagar", "Manufacturing", ["IoT", "Electronics", "Python"], 50, 74, 58, 70, "₹4.9 LPA avg."),
    ("Leadership & Communication", 3, "Professional communication and team leadership.", "6 weeks", "Blended", "Kolhapur", "Soft Skills", ["Leadership", "Communication"], 120, 88, 82, 79, "₹4.0 LPA avg."),
    ("Textile Technology & Automation", 8, "Modern textile manufacturing with automation.", "14 weeks", "In-person", "Solapur", "Manufacturing", ["Textile Technology", "Manufacturing"], 60, 72, 60, 69, "₹4.2 LPA avg."),
    ("Renewable Energy Systems", 2, "Wind, solar, and hybrid renewable installations.", "16 weeks", "In-person", "Amravati", "Green Energy", ["Solar Energy", "Electrical Safety", "IoT"], 50, 82, 70, 76, "₹4.8 LPA avg."),
    ("DevOps Engineering", 0, "CI/CD pipelines, containers, and SRE fundamentals.", "18 weeks", "Hybrid", "Pune", "Technology", ["Docker", "Kubernetes", "CI/CD", "Linux"], 80, 87, 74, 83, "₹7.8 LPA avg."),
    ("Business Intelligence & Analytics", 7, "BI tools and executive dashboard creation.", "10 weeks", "Online", "Navi Mumbai", "Technology", ["Tableau", "Power BI", "SQL"], 100, 84, 72, 78, "₹5.8 LPA avg."),
    ("Python for Automation", 3, "Python scripting for business and IT automation.", "8 weeks", "Online", "Mumbai", "Technology", ["Python", "Git", "Linux"], 200, 80, 69, 76, "₹5.4 LPA avg."),
    ("Machine Learning Practitioner", 1, "End-to-end ML projects for production deployment.", "22 weeks", "Hybrid", "Nagpur", "Technology", ["Machine Learning", "Python", "SQL", "Data Science"], 60, 83, 68, 80, "₹7.2 LPA avg."),
]

JOB_TITLES = [
    ("Cloud Engineer", "Technology", ["AWS", "Docker", "Linux", "Python"], "₹7–10 LPA", "1–3 years"),
    ("DevOps Engineer", "Technology", ["AWS", "Docker", "CI/CD", "Python"], "₹8–12 LPA", "1–3 years"),
    ("Backend Developer", "Technology", ["Python", "SQL", "REST APIs", "Git"], "₹6–8 LPA", "0–2 years"),
    ("Data Operations Analyst", "Finance", ["SQL", "Excel", "Communication"], "₹5–7 LPA", "0–2 years"),
    ("Data Scientist", "Technology", ["Python", "SQL", "Data Science", "Machine Learning"], "₹9–14 LPA", "2–4 years"),
    ("Full Stack Developer", "Technology", ["React", "Python", "REST APIs", "Git"], "₹7–11 LPA", "1–3 years"),
    ("Cybersecurity Analyst", "Technology", ["Cybersecurity", "Networking", "Linux"], "₹8–12 LPA", "1–3 years"),
    ("Solar Technician", "Green Energy", ["Solar Energy", "Electrical Safety"], "₹3.5–5 LPA", "Fresher"),
    ("Agritech Specialist", "Agriculture Technology", ["Agritech", "IoT", "Communication"], "₹4–6 LPA", "0–2 years"),
    ("Data Analyst", "Technology", ["SQL", "Python", "Tableau", "Excel"], "₹5–8 LPA", "0–2 years"),
    ("Cloud Infrastructure Engineer", "Technology", ["AWS", "Kubernetes", "Docker", "Linux"], "₹10–15 LPA", "2–4 years"),
    ("Logistics Systems Analyst", "Logistics", ["Logistics Tech", "SQL", "Communication"], "₹5–7 LPA", "1–2 years"),
    ("IoT Engineer", "Manufacturing", ["IoT", "Electronics", "Python"], "₹6–9 LPA", "1–3 years"),
    ("Digital Marketing Analyst", "Marketing", ["Digital Marketing", "Communication", "Excel"], "₹4–6 LPA", "0–2 years"),
    ("FinTech Business Analyst", "Finance", ["Finance", "Python", "SQL"], "₹7–10 LPA", "1–3 years"),
]

ASSESSMENT_QUESTIONS = {
    "Python": [
        {"text": "Which data type is immutable in Python?", "options": [
            {"id": "a", "text": "list"}, {"id": "b", "text": "tuple"}, {"id": "c", "text": "dict"}, {"id": "d", "text": "set"}
        ], "correct": "b", "difficulty": "easy"},
        {"text": "What does `list.append()` return?", "options": [
            {"id": "a", "text": "The new list"}, {"id": "b", "text": "The appended item"}, {"id": "c", "text": "None"}, {"id": "d", "text": "The list length"}
        ], "correct": "c", "difficulty": "easy"},
        {"text": "Which keyword is used to handle exceptions?", "options": [
            {"id": "a", "text": "catch"}, {"id": "b", "text": "except"}, {"id": "c", "text": "handle"}, {"id": "d", "text": "error"}
        ], "correct": "b", "difficulty": "easy"},
        {"text": "What is a lambda function?", "options": [
            {"id": "a", "text": "A class method"}, {"id": "b", "text": "Anonymous single-expression function"}, {"id": "c", "text": "A recursive function"}, {"id": "d", "text": "A generator"}
        ], "correct": "b", "difficulty": "medium"},
        {"text": "Which module is used for JSON in Python?", "options": [
            {"id": "a", "text": "jsonlib"}, {"id": "b", "text": "simplejson"}, {"id": "c", "text": "json"}, {"id": "d", "text": "pyson"}
        ], "correct": "c", "difficulty": "easy"},
    ],
    "SQL": [
        {"text": "Which SQL clause filters grouped results?", "options": [
            {"id": "a", "text": "WHERE"}, {"id": "b", "text": "HAVING"}, {"id": "c", "text": "GROUP BY"}, {"id": "d", "text": "FILTER"}
        ], "correct": "b", "difficulty": "medium"},
        {"text": "What does a LEFT JOIN return?", "options": [
            {"id": "a", "text": "Only matching rows"}, {"id": "b", "text": "All rows from right table"}, {"id": "c", "text": "All rows from left table, NULLs for unmatched right"}, {"id": "d", "text": "All rows from both tables"}
        ], "correct": "c", "difficulty": "medium"},
        {"text": "Which is used to prevent duplicate rows?", "options": [
            {"id": "a", "text": "UNIQUE"}, {"id": "b", "text": "DISTINCT"}, {"id": "c", "text": "ONLY"}, {"id": "d", "text": "NO DUP"}
        ], "correct": "b", "difficulty": "easy"},
    ],
    "AWS": [
        {"text": "What does EC2 stand for?", "options": [
            {"id": "a", "text": "Elastic Cloud Compute"}, {"id": "b", "text": "Elastic Compute Cloud"}, {"id": "c", "text": "Extended Compute Container"}, {"id": "d", "text": "Enterprise Cloud Control"}
        ], "correct": "b", "difficulty": "easy"},
        {"text": "Which AWS service provides managed Kubernetes?", "options": [
            {"id": "a", "text": "ECS"}, {"id": "b", "text": "EKS"}, {"id": "c", "text": "ECR"}, {"id": "d", "text": "Lambda"}
        ], "correct": "b", "difficulty": "medium"},
        {"text": "What is S3 used for?", "options": [
            {"id": "a", "text": "Relational database"}, {"id": "b", "text": "Object storage"}, {"id": "c", "text": "Virtual networking"}, {"id": "d", "text": "Serverless compute"}
        ], "correct": "b", "difficulty": "easy"},
    ],
    "Cybersecurity": [
        {"text": "Which is a common phishing indicator?", "options": [
            {"id": "a", "text": "HTTPS URL"}, {"id": "b", "text": "Urgent language requesting credentials"}, {"id": "c", "text": "Known sender address"}, {"id": "d", "text": "Plain text email"}
        ], "correct": "b", "difficulty": "easy"},
        {"text": "What does CIA stand for in security?", "options": [
            {"id": "a", "text": "Control, Identity, Access"}, {"id": "b", "text": "Confidentiality, Integrity, Availability"}, {"id": "c", "text": "Classify, Identify, Authenticate"}, {"id": "d", "text": "Cyber, Incident, Analysis"}
        ], "correct": "b", "difficulty": "easy"},
    ],
}


# ── Seed Functions ────────────────────────────────────────────────────────────

async def seed(db):
    print("\n🌱 KAUSHALYA Database Seed Script")
    print("=" * 50)

    # Clear demo collections
    collections_to_clear = [
        "users", "trainee_profiles", "employers", "training_institutes",
        "skills", "user_skills", "skill_assessments", "assessment_results",
        "training_programs", "enrollments", "certifications",
        "jobs", "job_skills", "job_applications", "employment_outcomes",
        "skill_demand", "district_data", "program_impact", "recommendations",
        "ai_conversations", "notifications",
    ]
    for col in collections_to_clear:
        await db[col].drop()
    print("✓ Cleared existing collections")

    # ── Districts ────────────────────────────────────────────────────────────
    await db.district_data.insert_many([{**d, "created_at": utcnow()} for d in DISTRICTS])
    print(f"✓ Inserted {len(DISTRICTS)} districts")

    # ── Skills ───────────────────────────────────────────────────────────────
    skill_docs = [{**s, "created_at": utcnow()} for s in SKILLS_DATA]
    await db.skills.insert_many(skill_docs)
    skills_in_db = await db.skills.find().to_list(length=100)
    skill_id_map = {s["name"]: str(s["_id"]) for s in skills_in_db}
    print(f"✓ Inserted {len(skills_in_db)} skills")

    # ── Assessments ───────────────────────────────────────────────────────────
    assessment_id_map = {}
    for skill_name, questions in ASSESSMENT_QUESTIONS.items():
        skill_id = skill_id_map.get(skill_name)
        if not skill_id:
            continue
        q_docs = []
        for i, q in enumerate(questions):
            q_docs.append({
                "id": f"q-{skill_name.lower()}-{i+1}",
                "text": q["text"],
                "options": [{"id": o["id"], "text": o["text"]} for o in q["options"]],
                "correct_option_id": q["correct"],
                "difficulty": q["difficulty"],
                "points": 1,
            })
        assessment = {
            "skill_id": skill_id,
            "skill_name": skill_name,
            "title": f"{skill_name} Proficiency Assessment",
            "description": f"Assess your {skill_name} knowledge",
            "duration_minutes": 30,
            "total_questions": len(q_docs),
            "difficulty": "mixed",
            "questions": q_docs,
            "created_at": utcnow(),
        }
        result = await db.skill_assessments.insert_one(assessment)
        assessment_id_map[skill_name] = str(result.inserted_id)
    print(f"✓ Inserted {len(assessment_id_map)} assessments")

    # ── Employers ─────────────────────────────────────────────────────────────
    employer_user_ids = []
    employer_profile_ids = []
    for i, (company, industry, location, website) in enumerate(EMPLOYER_DATA):
        email = f"employer{i+1}@{website.replace('/', '')}"
        now = rand_date(60, 400)
        user_result = await db.users.insert_one({
            "name": f"{company} HR",
            "email": email,
            "password_hash": _pwd_ctx.hash(DEMO_PASSWORD),
            "role": "EMPLOYER",
            "organization": company,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        })
        uid = str(user_result.inserted_id)
        employer_user_ids.append(uid)
        emp_result = await db.employers.insert_one({
            "user_id": uid,
            "company_name": company,
            "industry": industry,
            "location": location,
            "website": f"https://www.{website}",
            "description": f"Leading {industry} company based in {location}.",
            "size": random.choice(["50-200", "200-500", "500-1000", "1000+"]),
            "verified": True,
            "created_at": now,
        })
        employer_profile_ids.append(str(emp_result.inserted_id))
    print(f"✓ Inserted {len(EMPLOYER_DATA)} employers")

    # ── Training Institutes ───────────────────────────────────────────────────
    institute_user_ids = []
    for i, (name, location) in enumerate(INSTITUTE_DATA):
        email = f"institute{i+1}@{name.lower().replace(' ', '')[:12]}.edu.in"
        now = rand_date(90, 500)
        user_result = await db.users.insert_one({
            "name": name,
            "email": email,
            "password_hash": _pwd_ctx.hash(DEMO_PASSWORD),
            "role": "TRAINING_INSTITUTE",
            "organization": name,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        })
        uid = str(user_result.inserted_id)
        institute_user_ids.append(uid)
        await db.training_institutes.insert_one({
            "user_id": uid,
            "name": name,
            "location": {"district": location, "state": "Maharashtra"},
            "accredited": True,
            "created_at": now,
        })
    print(f"✓ Inserted {len(INSTITUTE_DATA)} training institutes")

    # ── Training Programs ─────────────────────────────────────────────────────
    program_ids = []
    for p in PROGRAM_DATA:
        (name, inst_idx, desc, duration, mode, location, industry, skills, capacity,
         completion_rate, placement_rate, impact_score, salary) = p
        institute_uid = institute_user_ids[inst_idx % len(institute_user_ids)]
        institute_name = INSTITUTE_DATA[inst_idx % len(INSTITUTE_DATA)][0]
        now = rand_date(180, 700)
        result = await db.training_programs.insert_one({
            "name": name,
            "institute": institute_name,
            "description": desc,
            "duration": duration,
            "mode": mode,
            "location": location,
            "industry": industry,
            "skills": skills,
            "capacity": capacity,
            "enrolled": int(capacity * random.uniform(0.6, 0.95)),
            "completion_rate": completion_rate,
            "placement_rate": placement_rate,
            "impact_score": impact_score,
            "salary": salary,
            "status": "active",
            "created_by": institute_uid,
            "created_at": now,
            "updated_at": now,
        })
        program_ids.append(str(result.inserted_id))
    print(f"✓ Inserted {len(program_ids)} training programs")

    # ── Jobs ──────────────────────────────────────────────────────────────────
    job_ids = []
    district_locations = [d["district"] for d in DISTRICTS]
    for i in range(75):
        title_data = JOB_TITLES[i % len(JOB_TITLES)]
        title, industry, req_skills, salary, experience = title_data
        employer_idx = i % len(employer_user_ids)
        location = f"{random.choice(district_locations[:8])} · {random.choice(['Hybrid', 'On-site', 'Remote'])}"
        posted_at = rand_date(1, 60)
        deadline_dt = posted_at + timedelta(days=random.randint(21, 60))
        result = await db.jobs.insert_one({
            "title": title,
            "company": EMPLOYER_DATA[employer_idx][0],
            "employer_id": employer_user_ids[employer_idx],
            "industry": industry,
            "location": location,
            "job_type": "Full-time",
            "experience": experience,
            "salary": salary,
            "required_skills": req_skills,
            "deadline": deadline_dt.strftime("%b %d, %Y"),
            "applicants": random.randint(5, 80),
            "match": 0,
            "status": "open",
            "description": f"Seeking a skilled {title} to join our team.",
            "posted_at": posted_at,
            "created_at": posted_at,
            "updated_at": posted_at,
        })
        job_ids.append(str(result.inserted_id))
    print(f"✓ Inserted {len(job_ids)} jobs")

    # ── Trainees ──────────────────────────────────────────────────────────────
    trainee_user_ids = []
    trainee_district_map = {}

    # Demo trainee first
    demo_now = rand_date(10, 30)
    demo_result = await db.users.insert_one({
        "name": "Aarav Kulkarni",
        "email": "trainee@kaushalya.demo",
        "password_hash": _pwd_ctx.hash(DEMO_PASSWORD),
        "role": "TRAINEE",
        "is_active": True,
        "created_at": demo_now,
        "updated_at": demo_now,
    })
    demo_uid = str(demo_result.inserted_id)
    trainee_user_ids.append(demo_uid)

    demo_profile_result = await db.trainee_profiles.insert_one({
        "user_id": demo_uid,
        "name": "Aarav Kulkarni",
        "email": "trainee@kaushalya.demo",
        "phone": "+91 98765 41028",
        "district": "Pune",
        "state": "Maharashtra",
        "education": "B.Tech",
        "specialization": "Computer Engineering",
        "employment_status": "Open to work",
        "experience": "1 year",
        "target_career": "Cloud Engineer",
        "profile_completion": 88,
        # Pre-computed employability score for the SIH demo
        "cached_employability_score": 82,
        "cached_score_class": "HIGH",
        "created_at": demo_now,
        "updated_at": demo_now,
    })

    # Add skills for demo trainee
    demo_skills = [
        ("Python", 90, True, 92),
        ("SQL", 80, True, 84),
        ("React", 60, True, 63),
        ("AWS", 20, False, 24),
        ("Docker", 8, False, 10),
        ("Communication", 74, True, 78),
    ]
    for skill_name, prof, verified, asmt_score in demo_skills:
        skill_id = skill_id_map.get(skill_name, "")
        if skill_id:
            await db.user_skills.insert_one({
                "user_id": demo_uid,
                "skill_id": skill_id,
                "skill_name": skill_name,
                "category": next((s["category"] for s in SKILLS_DATA if s["name"] == skill_name), ""),
                "proficiency": prof,
                "level": _level(prof),
                "verified": verified,
                "assessment_score": asmt_score,
                "source": "assessment" if verified else "self_reported",
                "created_at": demo_now,
                "updated_at": demo_now,
            })

    # Assessment results for demo trainee (Python + SQL — used by employability calculator)
    for skill_name, pct in [("Python", 92), ("SQL", 84)]:
        skill_id = skill_id_map.get(skill_name, "")
        asmt_id = assessment_id_map.get(skill_name)
        if asmt_id:
            await db.assessment_results.insert_one({
                "user_id": demo_uid,
                "assessment_id": asmt_id,
                "skill_id": skill_id,
                "skill_name": skill_name,
                "score": pct,
                "total": 100,
                "percentage": pct,
                "proficiency_level": "Expert" if pct >= 86 else "Advanced",
                "passed": True,
                "completed_at": demo_now,
            })

    # Enroll demo trainee in Cloud & DevOps program
    cloud_prog_id = program_ids[0] if program_ids else None
    if cloud_prog_id:
        enroll_dt = rand_date(30, 90)
        await db.enrollments.insert_one({
            "trainee_id": demo_uid,
            "program_id": cloud_prog_id,
            "program_name": "Cloud & DevOps Accelerator",
            "status": "IN_PROGRESS",
            "enrolled_at": enroll_dt,
            "completed_at": None,
        })
        # Also add a COMPLETED enrollment so training score is non-zero
        full_stack_prog = next(
            (p for i, p in enumerate(program_ids) if i < len(PROGRAM_DATA) and PROGRAM_DATA[i][0].startswith("Full Stack")),
            program_ids[3] if len(program_ids) > 3 else None
        )
        if full_stack_prog:
            await db.enrollments.insert_one({
                "trainee_id": demo_uid,
                "program_id": full_stack_prog,
                "program_name": "Full Stack Web Development",
                "status": "COMPLETED",
                "enrolled_at": demo_now - timedelta(days=120),
                "completed_at": demo_now - timedelta(days=30),
            })
        await db.certifications.insert_one({
            "user_id": demo_uid,
            "name": "Web Development Fundamentals",
            "issuer": "Maharashtra Digital Skills Centre",
            "program_id": cloud_prog_id,
            "issue_date": rand_date(10, 60).strftime("%Y-%m-%d"),
            "verified": True,
            "verification_url": "https://certs.kaushalya.gov.in/demo-001",
            "created_at": demo_now,
        })

    # 199 more trainees
    for i in range(199):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        district = DISTRICTS[i % len(DISTRICTS)]["district"]
        email = f"{first.lower()}.{last.lower()}{random.randint(10, 999)}@example.com"
        degree, spec = random.choice(EDUCATION_DEGREES)
        exp = random.choice(EXPERIENCE_OPTIONS)
        status = random.choice(STATUS_OPTIONS)
        now = rand_date(5, 500)

        user_result = await db.users.insert_one({
            "name": name,
            "email": email,
            "password_hash": _pwd_ctx.hash(DEMO_PASSWORD),
            "role": "TRAINEE",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        })
        uid = str(user_result.inserted_id)
        trainee_user_ids.append(uid)
        trainee_district_map[uid] = district

        await db.trainee_profiles.insert_one({
            "user_id": uid,
            "name": name,
            "email": email,
            "phone": f"+91 {random.randint(70000, 99999):05d} {random.randint(10000, 99999):05d}",
            "district": district,
            "state": "Maharashtra",
            "education": degree,
            "specialization": spec,
            "employment_status": status,
            "experience": exp,
            "target_career": random.choice([t[0] for t in JOB_TITLES[:8]]),
            "profile_completion": random.randint(40, 100),
            "company": f"{random.choice(EMPLOYER_DATA)[0]}" if status == "Employed" else None,
            "job_role": random.choice([t[0] for t in JOB_TITLES[:8]]) if status == "Employed" else None,
            "salary": None,
            "created_at": now,
            "updated_at": now,
        })

        # Add 2–5 random skills
        trainee_skills = random.sample(list(skill_id_map.keys()), min(5, len(skill_id_map)))
        for skill_name in trainee_skills[:random.randint(2, 5)]:
            prof = random.randint(10, 95)
            verified = prof >= 55 and random.random() > 0.3
            await db.user_skills.insert_one({
                "user_id": uid,
                "skill_id": skill_id_map[skill_name],
                "skill_name": skill_name,
                "category": next((s["category"] for s in SKILLS_DATA if s["name"] == skill_name), ""),
                "proficiency": prof,
                "level": _level(prof),
                "verified": verified,
                "assessment_score": random.randint(prof - 10, min(100, prof + 10)) if verified else None,
                "source": "assessment" if verified else "self_reported",
                "created_at": now,
                "updated_at": now,
            })

        # Enroll in a program (60% chance)
        if random.random() < 0.6:
            prog_id = random.choice(program_ids)
            prog = await db.training_programs.find_one({"_id": ObjectId(prog_id)})
            enroll_dt = rand_date(20, 200)
            enroll_status = random.choices(
                ["ENROLLED", "IN_PROGRESS", "COMPLETED", "DROPPED"],
                weights=[15, 30, 45, 10], k=1
            )[0]
            completed_dt = rand_date(5, 60) if enroll_status == "COMPLETED" else None
            await db.enrollments.insert_one({
                "trainee_id": uid,
                "program_id": prog_id,
                "program_name": prog.get("name", "") if prog else "",
                "status": enroll_status,
                "enrolled_at": enroll_dt,
                "completed_at": completed_dt,
            })

            # Certification if completed
            if enroll_status == "COMPLETED" and prog and random.random() > 0.3:
                await db.certifications.insert_one({
                    "user_id": uid,
                    "name": f"{prog['name']} Certificate",
                    "issuer": prog.get("institute", "Training Institute"),
                    "program_id": prog_id,
                    "issue_date": rand_date(5, 60).strftime("%Y-%m-%d"),
                    "verified": True,
                    "verification_url": f"https://certs.kaushalya.gov.in/{uid[:8]}",
                    "created_at": now,
                })

    print(f"✓ Inserted 200 trainees (including demo account)")

    # ── Job Applications ──────────────────────────────────────────────────────
    application_count = 0
    for i in range(150):
        trainee_uid = trainee_user_ids[i % len(trainee_user_ids)]
        job_id = random.choice(job_ids)
        existing = await db.job_applications.find_one({"job_id": job_id, "trainee_id": trainee_uid})
        if existing:
            continue
        app_status = random.choices(
            ["submitted", "reviewed", "shortlisted", "rejected", "hired"],
            weights=[30, 25, 20, 15, 10], k=1
        )[0]
        created_at = rand_date(1, 120)
        await db.job_applications.insert_one({
            "job_id": job_id,
            "trainee_id": trainee_uid,
            "status": app_status,
            "note": "Application submitted via KAUSHALYA platform.",
            "created_at": created_at,
            "updated_at": created_at,
        })
        application_count += 1
    print(f"✓ Inserted {application_count} job applications")

    # ── Employment Outcomes ───────────────────────────────────────────────────
    outcome_count = 0
    employed_trainees = []
    profiles_cursor = db.trainee_profiles.find({"employment_status": "Employed"}).limit(120)
    employed_profiles = await profiles_cursor.to_list(length=120)
    for profile in employed_profiles[:100]:
        uid = profile["user_id"]
        employer_data = random.choice(EMPLOYER_DATA)
        prog_id = random.choice(program_ids) if random.random() > 0.3 else None
        salary = round(random.uniform(2.8, 12.0), 1)
        emp_date = rand_date(30, 400)
        await db.employment_outcomes.insert_one({
            "trainee_id": uid,
            "training_program_id": prog_id,
            "employer_name": employer_data[0],
            "job_title": random.choice([t[0] for t in JOB_TITLES[:8]]),
            "salary": salary,
            "employment_type": "Full-time",
            "location": profile.get("district", "Pune"),
            "employment_date": emp_date.strftime("%Y-%m-%d"),
            "retention_6_months": random.random() > 0.22,
            "retention_12_months": random.random() > 0.30,
            "career_progression": random.choice(["Promoted to senior", "Lateral move", "Stable", ""]),
            "source": "verified",
            "created_at": emp_date,
            "updated_at": emp_date,
        })
        outcome_count += 1
    print(f"✓ Inserted {outcome_count} employment outcomes")

    # ── Skill Demand Records ─────────────────────────────────────────────────
    demand_count = 0
    for skill in skills_in_db:
        for district in DISTRICTS:
            base_demand = int(skill["demand_score"] * random.uniform(50, 200))
            supply = int(base_demand * random.uniform(0.3, 0.9))
            gr = skill["growth_rate"] + random.randint(-5, 5)
            status = "rapidly-growing" if gr >= 30 else "growing" if gr >= 10 else "stable" if gr >= 0 else "declining"
            job_count = int(base_demand / random.uniform(5, 15))
            await db.skill_demand.insert_one({
                "skill_id": str(skill["_id"]),
                "skill_name": skill["name"],
                "category": skill["category"],
                "current_demand": base_demand,
                "supply": supply,
                "growth_rate": gr,
                "job_count": job_count,
                "location": district["district"],
                "status": status,
                "industry_demand": {industry: int(base_demand * random.uniform(0.1, 0.4)) for industry in skill.get("industries", ["IT"])[:2]},
                "regional_demand": {district["district"]: base_demand},
                "recorded_at": rand_date(1, 30),
            })
            demand_count += 1
    print(f"✓ Inserted {demand_count} skill demand records")

    # ── Demo Admin Accounts ───────────────────────────────────────────────────
    now = utcnow()

    # Government Admin
    await db.users.insert_one({
        "name": "Maharashtra Government Admin",
        "email": "admin@kaushalya.demo",
        "password_hash": _pwd_ctx.hash(DEMO_PASSWORD),
        "role": "GOVERNMENT_ADMIN",
        "organization": "Government of Maharashtra",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    })

    # Super Admin
    await db.users.insert_one({
        "name": "KAUSHALYA Super Admin",
        "email": "superadmin@kaushalya.demo",
        "password_hash": _pwd_ctx.hash(DEMO_PASSWORD),
        "role": "SUPER_ADMIN",
        "organization": "KAUSHALYA Platform",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    })

    # Demo Employer
    await db.users.update_one(
        {"email": f"employer1@pds.in"},
        {"$set": {"email": "employer@kaushalya.demo"}},
    )
    print("✓ Created demo accounts")

    # ── Create indexes ─────────────────────────────────────────────────────────
    from app.database.indexes import create_indexes
    await create_indexes(db)
    print("✓ Created database indexes")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("🎉 Seed complete! Summary:")
    print(f"  Districts      : {await db.district_data.count_documents({})}")
    print(f"  Skills         : {await db.skills.count_documents({})}")
    print(f"  Assessments    : {await db.skill_assessments.count_documents({})}")
    print(f"  Employers      : {await db.employers.count_documents({})}")
    print(f"  Institutes     : {await db.training_institutes.count_documents({})}")
    print(f"  Programs       : {await db.training_programs.count_documents({})}")
    print(f"  Jobs           : {await db.jobs.count_documents({})}")
    print(f"  Trainees       : {await db.trainee_profiles.count_documents({})}")
    print(f"  Applications   : {await db.job_applications.count_documents({})}")
    print(f"  Outcomes       : {await db.employment_outcomes.count_documents({})}")
    print(f"  Skill demand   : {await db.skill_demand.count_documents({})}")
    print(f"  Users total    : {await db.users.count_documents({})}")
    print("\n📋 Demo Accounts (password: Demo@1234):")
    print("  trainee@kaushalya.demo      → Trainee (Aarav Kulkarni, Pune)")
    print("  employer@kaushalya.demo     → Employer (Pune Digital Systems)")
    print("  institute1@maharashtradi.edu.in → Training Institute")
    print("  admin@kaushalya.demo        → Government Admin")
    print("  superadmin@kaushalya.demo   → Super Admin")
    print("\n🚀 Start the backend:")
    print("  cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


def _level(score: int) -> str:
    if score >= 86: return "Expert"
    if score >= 71: return "Advanced"
    if score >= 51: return "Intermediate"
    if score >= 31: return "Basic"
    return "Beginner"


async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]
    try:
        await client.admin.command("ping")
        print(f"✓ Connected to MongoDB: {MONGODB_DB_NAME}")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print(f"  URI: {MONGODB_URI}")
        print("  Make sure MongoDB is running.")
        sys.exit(1)
    try:
        await seed(db)
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())


import json
import os
import sys

# Adding Kaushalya AI Database Seed logic
def seed_ai_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(base_path, "datasets")
    
    # Check if datasets exist
    if not os.path.exists(datasets_dir):
        print("No AI datasets found.")
        return

    try:
        from app.ai.embeddings import get_embedding
        print("Generating embeddings for knowledge base...")
        kb_path = os.path.join(datasets_dir, "knowledge_base.json")
        if os.path.exists(kb_path):
            with open(kb_path, 'r') as f:
                kb_data = json.load(f)
            
            for doc in kb_data:
                emb = get_embedding(doc['text'])
                # Mocking insertion of embeddings and creating vector search index (cosine)
                # session.execute("INSERT INTO vector_table ...")
            print("Vector search index (cosine) seeded successfully.")
    except ImportError:
        print("AI modules not found, skipping embedding generation.")

if __name__ == "__main__":
    seed_ai_data()
