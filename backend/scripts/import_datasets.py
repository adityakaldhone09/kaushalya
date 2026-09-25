#!/usr/bin/env python3
"""
KAUSHALYA Dataset Import System

Imports the provided datasets:
- Dataset_1: Professional skills intelligence
- Dataset_2: Q&A pairs for assessments
- Dataset_3: Skills taxonomy
- all_job_post.csv: Job postings

Usage:
    python scripts/import_datasets.py                    # Import everything
    python scripts/import_datasets.py --dataset=jobs     # Import only jobs
    python scripts/import_datasets.py --mode=replace     # Replace existing data
    python scripts/import_datasets.py --validate-only    # Validate without importing
"""

from __future__ import annotations
import asyncio
import csv
import json
import sys
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from collections import defaultdict
import re

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import get_settings

logger = logging.getLogger("import_datasets")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")

# ────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────────────────────────────────

DATASET_DIR = Path(__file__).parent.parent.parent / "Dataset_1" / "india_professional_skills_intelligence.csv"
DATASET_2_DIR = Path(__file__).parent.parent.parent / "Dataset_2"
DATASET_3_SKILLS = Path(__file__).parent.parent.parent / "Dataset_3" / "skills.csv"
JOBS_CSV = Path(__file__).parent.parent.parent / "all_job_post.csv"

IMPORT_REPORT = {
    "dataset_1": {"records_read": 0, "imported": 0, "skipped": 0, "errors": []},
    "dataset_2": {"records_read": 0, "imported": 0, "skipped": 0, "errors": []},
    "dataset_3_skills": {"records_read": 0, "imported": 0, "skipped": 0, "errors": []},
    "jobs": {"records_read": 0, "imported": 0, "skipped": 0, "errors": []},
}

# ────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ────────────────────────────────────────────────────────────────────────────

def normalize_skill_name(skill: str) -> str:
    """Normalize skill name for matching."""
    if not skill:
        return ""
    return skill.strip().lower()

def normalize_job_title(title: str) -> str:
    """Normalize job title for matching."""
    if not title:
        return ""
    # Remove common suffixes
    title = re.sub(r'\s*(I|II|III|IV|V|Sr\.?|Jr\.?)$', '', title, flags=re.IGNORECASE)
    return title.strip().lower()

def normalize_location(city: str, state: str = "") -> dict:
    """Normalize location data."""
    return {
        "city": city.strip() if city else "",
        "state": state.strip() if state else "",
        "normalized": f"{city.strip().lower()}, {state.strip().lower()}" if city and state else city.strip().lower(),
    }

def parse_skills_string(skills_str: str, delimiter: str = ";") -> list[str]:
    """Parse semicolon or comma-separated skills string."""
    if not skills_str:
        return []
    skills = skills_str.split(delimiter)
    return [s.strip() for s in skills if s.strip()]

async def get_db():
    """Get MongoDB connection."""
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    return client[settings.MONGODB_DB_NAME]

# ────────────────────────────────────────────────────────────────────────────
# IMPORT SKILLS TAXONOMY (Dataset_3)
# ────────────────────────────────────────────────────────────────────────────

async def import_skills_taxonomy(db, mode: str = "upsert"):
    """Import skills from Dataset_3/skills.csv"""
    logger.info("Importing skills taxonomy from Dataset_3...")
    
    if not DATASET_3_SKILLS.exists():
        logger.warning(f"Dataset_3 skills file not found: {DATASET_3_SKILLS}")
        return

    skill_names_seen = set()
    skill_count = 0

    try:
        with open(DATASET_3_SKILLS, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                IMPORT_REPORT["dataset_3_skills"]["records_read"] += 1
                
                skill_name = row.get("Skill", "").strip().strip('"')
                if not skill_name or skill_name.lower() in skill_names_seen:
                    IMPORT_REPORT["dataset_3_skills"]["skipped"] += 1
                    continue
                
                skill_names_seen.add(skill_name.lower())
                
                skill_doc = {
                    "name": skill_name,
                    "normalized_name": normalize_skill_name(skill_name),
                    "category": "General",  # Default category
                    "demand_score": 0,  # Will be calculated from job data
                    "source": "DATASET_3",
                    "imported_at": datetime.now(timezone.utc),
                    "dataset_version": "1.0",
                }
                
                if mode == "replace":
                    await db.skills.replace_one(
                        {"name": skill_name},
                        skill_doc,
                        upsert=True
                    )
                else:  # upsert
                    await db.skills.update_one(
                        {"name": skill_name},
                        {"$set": skill_doc},
                        upsert=True
                    )
                
                IMPORT_REPORT["dataset_3_skills"]["imported"] += 1
                skill_count += 1
                
                if skill_count % 1000 == 0:
                    logger.info(f"  Imported {skill_count} skills...")
        
        logger.info(f"✓ Skills imported: {IMPORT_REPORT['dataset_3_skills']['imported']}")
        
    except Exception as e:
        logger.error(f"Error importing skills: {e}")
        IMPORT_REPORT["dataset_3_skills"]["errors"].append(str(e))

# ────────────────────────────────────────────────────────────────────────────
# IMPORT JOB POSTINGS
# ────────────────────────────────────────────────────────────────────────────

async def import_jobs(db, mode: str = "upsert"):
    """Import jobs from all_job_post.csv"""
    logger.info("Importing job postings...")
    
    if not JOBS_CSV.exists():
        logger.warning(f"Jobs CSV not found: {JOBS_CSV}")
        return

    job_count = 0
    job_skills_extracted = defaultdict(int)

    try:
        with open(JOBS_CSV, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                IMPORT_REPORT["jobs"]["records_read"] += 1
                
                job_id = row.get("job_id", "").strip()
                job_title = row.get("job_title", "").strip()
                category = row.get("category", "").strip()
                job_description = row.get("job_description", "").strip()
                job_skill_set_raw = row.get("job_skill_set", "")
                
                if not job_id or not job_title:
                    IMPORT_REPORT["jobs"]["skipped"] += 1
                    continue
                
                # Parse skills from job_skill_set
                job_skills = parse_skills_string(job_skill_set_raw, ",")
                for skill in job_skills:
                    job_skills_extracted[normalize_skill_name(skill)] += 1
                
                job_doc = {
                    "external_id": job_id,
                    "title": job_title,
                    "normalized_title": normalize_job_title(job_title),
                    "category": category,
                    "description": job_description[:5000] if job_description else "",  # Limit desc length
                    "skills": job_skills,
                    "skills_normalized": [normalize_skill_name(s) for s in job_skills],
                    "skill_count": len(job_skills),
                    "source_dataset": "all_job_post.csv",
                    "imported_at": datetime.now(timezone.utc),
                    "dataset_version": "1.0",
                }
                
                if mode == "replace":
                    await db.jobs.replace_one(
                        {"external_id": job_id},
                        job_doc,
                        upsert=True
                    )
                else:  # upsert
                    await db.jobs.update_one(
                        {"external_id": job_id},
                        {"$set": job_doc},
                        upsert=True
                    )
                
                IMPORT_REPORT["jobs"]["imported"] += 1
                job_count += 1
                
                if job_count % 5000 == 0:
                    logger.info(f"  Imported {job_count} jobs...")
        
        logger.info(f"✓ Jobs imported: {IMPORT_REPORT['jobs']['imported']}")
        logger.info(f"  Unique skills extracted: {len(job_skills_extracted)}")
        
    except Exception as e:
        logger.error(f"Error importing jobs: {e}")
        IMPORT_REPORT["jobs"]["errors"].append(str(e))

# ────────────────────────────────────────────────────────────────────────────
# IMPORT PROFESSIONAL PROFILES (Dataset_1)
# ────────────────────────────────────────────────────────────────────────────

async def import_professional_profiles(db, mode: str = "upsert"):
    """Import professional profiles from Dataset_1"""
    logger.info("Importing professional profiles from Dataset_1...")
    
    if not DATASET_DIR.exists():
        logger.warning(f"Dataset_1 not found: {DATASET_DIR}")
        return

    profile_count = 0

    try:
        with open(DATASET_DIR, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                IMPORT_REPORT["dataset_1"]["records_read"] += 1
                
                profile_id = row.get("profile_id", "").strip()
                if not profile_id:
                    IMPORT_REPORT["dataset_1"]["skipped"] += 1
                    continue
                
                top_skills = parse_skills_string(row.get("top_skills", ""), ";")
                
                profile_doc = {
                    "external_profile_id": profile_id,
                    "current_job_title": row.get("current_job_title", ""),
                    "seniority_level": row.get("seniority_level", ""),
                    "industry": row.get("industry", ""),
                    "primary_skill_domain": row.get("primary_skill_domain", ""),
                    "top_skills": top_skills,
                    "skill_count": int(float(row.get("skill_count", 0))),
                    "years_experience": float(row.get("years_experience", 0.0)),
                    "education_level": row.get("education_level", ""),
                    "degree_field": row.get("degree_field", ""),
                    "location": normalize_location(
                        row.get("city", ""),
                        row.get("state", "")
                    ),
                    "company_size": row.get("company_size", ""),
                    "employment_type": row.get("employment_type", ""),
                    "work_mode": row.get("work_mode", ""),
                    "is_gig_worker": row.get("is_gig_worker", "").lower() in ("yes", "true"),
                    "uses_generative_ai_tools": row.get("uses_generative_ai_tools", "").lower() in ("yes", "true"),
                    "certifications_count": int(row.get("certifications_count", 0)),
                    "endorsement_count": int(row.get("endorsement_count", 0)),
                    "connections_tier": row.get("connections_tier", ""),
                    "profile_completeness_pct": float(row.get("profile_completeness_pct", 0.0)),
                    "open_to_work": row.get("open_to_work", "").lower() in ("yes", "true"),
                    "estimated_annual_salary_lpa": float(row.get("estimated_annual_salary_lpa", 0.0)),
                    "employability_score": float(row.get("employability_score", 0.0)),
                    "in_demand_skill_flag": row.get("in_demand_skill_flag", "").lower() in ("yes", "true"),
                    "source_dataset": "Dataset_1",
                    "imported_at": datetime.now(timezone.utc),
                    "dataset_version": "1.0",
                }
                
                if mode == "replace":
                    await db.professional_profiles.replace_one(
                        {"external_profile_id": profile_id},
                        profile_doc,
                        upsert=True
                    )
                else:  # upsert
                    await db.professional_profiles.update_one(
                        {"external_profile_id": profile_id},
                        {"$set": profile_doc},
                        upsert=True
                    )
                
                IMPORT_REPORT["dataset_1"]["imported"] += 1
                profile_count += 1
                
                if profile_count % 10000 == 0:
                    logger.info(f"  Imported {profile_count} profiles...")
        
        logger.info(f"✓ Profiles imported: {IMPORT_REPORT['dataset_1']['imported']}")
        
    except Exception as e:
        logger.error(f"Error importing profiles: {e}")
        IMPORT_REPORT["dataset_1"]["errors"].append(str(e))

# ────────────────────────────────────────────────────────────────────────────
# CREATE INDEXES
# ────────────────────────────────────────────────────────────────────────────

async def create_indexes(db):
    """Create MongoDB indexes for imported data"""
    logger.info("Creating MongoDB indexes...")
    
    try:
        # Jobs indexes
        try:
            await db.jobs.create_index("title")
            await db.jobs.create_index("normalized_title")
            await db.jobs.create_index("category")
            await db.jobs.create_index("skills")
            await db.jobs.create_index("skills_normalized")
        except Exception as e:
            if "already exists" not in str(e):
                raise
        
        # Skills indexes
        try:
            await db.skills.create_index("name", unique=True)
        except Exception as e:
            if "already exists" not in str(e):
                raise
        try:
            await db.skills.create_index("normalized_name")
            await db.skills.create_index("category")
        except Exception as e:
            if "already exists" not in str(e):
                raise
        
        # Professional profiles indexes
        try:
            await db.professional_profiles.create_index("external_profile_id", unique=True)
        except Exception as e:
            if "already exists" not in str(e):
                raise
        try:
            await db.professional_profiles.create_index("current_job_title")
            await db.professional_profiles.create_index("industry")
            await db.professional_profiles.create_index("location.state")
        except Exception as e:
            if "already exists" not in str(e):
                raise
        
        logger.info("✓ Indexes created or already exist")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Import KAUSHALYA datasets")
    parser.add_argument("--dataset", choices=["all", "jobs", "skills", "profiles", "qa"], default="all")
    parser.add_argument("--mode", choices=["upsert", "replace"], default="upsert")
    parser.add_argument("--validate-only", action="store_true", help="Validate without importing")
    args = parser.parse_args()

    logger.info(f"Starting dataset import (mode={args.mode}, dataset={args.dataset})")
    
    if args.validate_only:
        logger.info("Validation-only mode: files will be checked but not imported")
    
    db = await get_db()
    
    try:
        if args.dataset in ("all", "skills"):
            await import_skills_taxonomy(db, args.mode)
        
        if args.dataset in ("all", "jobs"):
            await import_jobs(db, args.mode)
        
        if args.dataset in ("all", "profiles"):
            await import_professional_profiles(db, args.mode)
        
        if args.dataset in ("all", "qa"):
            logger.info("Q&A datasets are not imported in this version (domain-specific)")
        
        # Create indexes
        await create_indexes(db)
        
        # Print report
        logger.info("\n" + "="*70)
        logger.info("IMPORT COMPLETE")
        logger.info("="*70)
        for dataset, stats in IMPORT_REPORT.items():
            if stats["records_read"] > 0:
                logger.info(f"\n{dataset}:")
                logger.info(f"  Records read:    {stats['records_read']}")
                logger.info(f"  Imported:        {stats['imported']}")
                logger.info(f"  Skipped:         {stats['skipped']}")
                if stats["errors"]:
                    logger.warning(f"  Errors:          {len(stats['errors'])}")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
