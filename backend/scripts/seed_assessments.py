#!/usr/bin/env python3
"""
KAUSHALYA Seed Assessment Questions

Creates demo assessment questions mapped to common skills from the job dataset.
This helps trainees practice before taking real assessments.

Usage:
    python scripts/seed_assessments.py
"""

from __future__ import annotations
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import get_settings
from bson import ObjectId

# ────────────────────────────────────────────────────────────────────────────
# DEMO ASSESSMENT QUESTIONS
# ────────────────────────────────────────────────────────────────────────────

DEMO_QUESTIONS = {
    "Python Fundamentals": [
        {
            "id": "py001",
            "text": "What is the output of print(type([]))?",
            "options": [
                {"id": "opt_a", "text": "<class 'list'>"},
                {"id": "opt_b", "text": "<class 'dict'>"},
                {"id": "opt_c", "text": "<class 'tuple'>"},
                {"id": "opt_d", "text": "<class 'set'>"},
            ],
            "correct_option_id": "opt_a",
            "difficulty": "easy",
            "points": 1,
        },
        {
            "id": "py002",
            "text": "Which of the following is a mutable data type in Python?",
            "options": [
                {"id": "opt_a", "text": "Tuple"},
                {"id": "opt_b", "text": "String"},
                {"id": "opt_c", "text": "List"},
                {"id": "opt_d", "text": "Frozen Set"},
            ],
            "correct_option_id": "opt_c",
            "difficulty": "easy",
            "points": 1,
        },
        {
            "id": "py003",
            "text": "What does the 'async/await' pattern in Python enable?",
            "options": [
                {"id": "opt_a", "text": "Synchronous blocking operations"},
                {"id": "opt_b", "text": "Asynchronous non-blocking operations"},
                {"id": "opt_c", "text": "Memory management optimization"},
                {"id": "opt_d", "text": "Type hinting"},
            ],
            "correct_option_id": "opt_b",
            "difficulty": "hard",
            "points": 2,
        },
    ],
    "JavaScript Basics": [
        {
            "id": "js001",
            "text": "What is the correct way to declare a variable in ES6?",
            "options": [
                {"id": "opt_a", "text": "var x = 5;"},
                {"id": "opt_b", "text": "const x = 5;"},
                {"id": "opt_c", "text": "Both var and const"},
                {"id": "opt_d", "text": "variable x = 5;"},
            ],
            "correct_option_id": "opt_b",
            "difficulty": "easy",
            "points": 1,
        },
        {
            "id": "js002",
            "text": "What is the difference between '==' and '===' in JavaScript?",
            "options": [
                {"id": "opt_a", "text": "'===' checks type and value"},
                {"id": "opt_b", "text": "'==' checks type and value"},
                {"id": "opt_c", "text": "They are identical"},
                {"id": "opt_d", "text": "'===' is only used in loops"},
            ],
            "correct_option_id": "opt_a",
            "difficulty": "medium",
            "points": 1,
        },
        {
            "id": "js003",
            "text": "What is a Promise in JavaScript?",
            "options": [
                {"id": "opt_a", "text": "A variable declaration"},
                {"id": "opt_b", "text": "An object representing eventual completion of an async operation"},
                {"id": "opt_c", "text": "A function that returns immediately"},
                {"id": "opt_d", "text": "A type of loop"},
            ],
            "correct_option_id": "opt_b",
            "difficulty": "hard",
            "points": 2,
        },
    ],
    "Data Structures": [
        {
            "id": "ds001",
            "text": "What is the time complexity of searching in a binary search tree?",
            "options": [
                {"id": "opt_a", "text": "O(1)"},
                {"id": "opt_b", "text": "O(log n)"},
                {"id": "opt_c", "text": "O(n)"},
                {"id": "opt_d", "text": "O(n²)"},
            ],
            "correct_option_id": "opt_b",
            "difficulty": "medium",
            "points": 2,
        },
        {
            "id": "ds002",
            "text": "Which data structure uses LIFO (Last In First Out)?",
            "options": [
                {"id": "opt_a", "text": "Queue"},
                {"id": "opt_b", "text": "Stack"},
                {"id": "opt_c", "text": "Linked List"},
                {"id": "opt_d", "text": "Heap"},
            ],
            "correct_option_id": "opt_b",
            "difficulty": "easy",
            "points": 1,
        },
    ],
    "React Fundamentals": [
        {
            "id": "react001",
            "text": "What is the purpose of the 'key' prop in React lists?",
            "options": [
                {"id": "opt_a", "text": "To encrypt data"},
                {"id": "opt_b", "text": "To help React identify which items have changed"},
                {"id": "opt_c", "text": "To sort the list"},
                {"id": "opt_d", "text": "To filter the list"},
            ],
            "correct_option_id": "opt_b",
            "difficulty": "medium",
            "points": 1,
        },
        {
            "id": "react002",
            "text": "What is a functional component in React?",
            "options": [
                {"id": "opt_a", "text": "A component that extends React.Component"},
                {"id": "opt_b", "text": "A JavaScript function that returns JSX"},
                {"id": "opt_c", "text": "A component that manages state"},
                {"id": "opt_d", "text": "A component that cannot have props"},
            ],
            "correct_option_id": "opt_b",
            "difficulty": "easy",
            "points": 1,
        },
    ],
}

async def seed_assessments():
    """Seed demo assessments into MongoDB."""
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    
    print("Seeding demo assessments...")
    
    for skill_name, questions in DEMO_QUESTIONS.items():
        # Create or find skill
        skill = await db.skills.find_one({"name": skill_name})
        if not skill:
            skill_result = await db.skills.insert_one({
                "name": skill_name,
                "normalized_name": skill_name.lower(),
                "category": "Technology",
                "demand_score": 0,
                "source": "DEMO",
                "created_at": datetime.now(timezone.utc),
            })
            skill_id = str(skill_result.inserted_id)
        else:
            skill_id = str(skill["_id"])
        
        # Create assessment
        assessment = {
            "skill_id": skill_id,
            "skill_name": skill_name,
            "title": f"{skill_name} Assessment",
            "description": f"Test your knowledge of {skill_name}",
            "duration_minutes": 30,
            "total_questions": len(questions),
            "difficulty": "mixed",
            "active": True,
            "questions": questions,
            "source": "DEMO",
            "created_at": datetime.now(timezone.utc),
        }
        
        result = await db.skill_assessments.insert_one(assessment)
        print(f"✓ Created assessment: {skill_name} (ID: {result.inserted_id})")
    
    print(f"\n✓ Seeded {len(DEMO_QUESTIONS)} assessments with {sum(len(q) for q in DEMO_QUESTIONS.values())} total questions")
    await client.close()

if __name__ == "__main__":
    asyncio.run(seed_assessments())
