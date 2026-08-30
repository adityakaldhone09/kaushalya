from __future__ import annotations
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, IndexModel

logger = logging.getLogger(__name__)


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create all required MongoDB indexes."""
    try:
        # users
        await db.users.create_indexes([
            IndexModel([("email", ASCENDING)], unique=True, name="users_email_unique"),
            IndexModel([("role", ASCENDING)], name="users_role"),
        ])

        # trainee_profiles
        await db.trainee_profiles.create_indexes([
            IndexModel([("user_id", ASCENDING)], unique=True, name="trainee_user_id_unique"),
            IndexModel([("location.district", ASCENDING)], name="trainee_district"),
            IndexModel([("employment_status", ASCENDING)], name="trainee_employment_status"),
        ])

        # employers
        await db.employers.create_indexes([
            IndexModel([("user_id", ASCENDING)], unique=True, name="employer_user_id_unique"),
            IndexModel([("industry", ASCENDING)], name="employer_industry"),
        ])

        # training_institutes
        await db.training_institutes.create_indexes([
            IndexModel([("user_id", ASCENDING)], unique=True, name="institute_user_id_unique"),
            IndexModel([("location.district", ASCENDING)], name="institute_district"),
        ])

        # skills
        await db.skills.create_indexes([
            IndexModel([("name", ASCENDING)], unique=True, name="skills_name_unique"),
            IndexModel([("category", ASCENDING)], name="skills_category"),
            IndexModel([("demand_score", DESCENDING)], name="skills_demand_score"),
        ])

        # user_skills
        await db.user_skills.create_indexes([
            IndexModel([("user_id", ASCENDING)], name="user_skills_user_id"),
            IndexModel([("skill_id", ASCENDING)], name="user_skills_skill_id"),
            IndexModel(
                [("user_id", ASCENDING), ("skill_id", ASCENDING)],
                unique=True,
                name="user_skills_user_skill_unique",
            ),
        ])

        # skill_assessments
        await db.skill_assessments.create_indexes([
            IndexModel([("skill_id", ASCENDING)], name="assessments_skill_id"),
            IndexModel([("difficulty", ASCENDING)], name="assessments_difficulty"),
        ])

        # assessment_results
        await db.assessment_results.create_indexes([
            IndexModel([("user_id", ASCENDING)], name="results_user_id"),
            IndexModel([("assessment_id", ASCENDING)], name="results_assessment_id"),
            IndexModel([("completed_at", DESCENDING)], name="results_completed_at"),
        ])

        # training_programs
        await db.training_programs.create_indexes([
            IndexModel([("industry", ASCENDING)], name="programs_industry"),
            IndexModel([("location", ASCENDING)], name="programs_location"),
            IndexModel([("status", ASCENDING)], name="programs_status"),
        ])

        # enrollments
        await db.enrollments.create_indexes([
            IndexModel([("trainee_id", ASCENDING)], name="enrollments_trainee"),
            IndexModel([("program_id", ASCENDING)], name="enrollments_program"),
            IndexModel([("status", ASCENDING)], name="enrollments_status"),
        ])

        # certifications
        await db.certifications.create_indexes([
            IndexModel([("user_id", ASCENDING)], name="certs_user_id"),
            IndexModel([("program_id", ASCENDING)], name="certs_program_id"),
        ])

        # jobs
        await db.jobs.create_indexes([
            IndexModel([("employer_id", ASCENDING)], name="jobs_employer_id"),
            IndexModel([("location", ASCENDING)], name="jobs_location"),
            IndexModel([("status", ASCENDING)], name="jobs_status"),
            IndexModel([("industry", ASCENDING)], name="jobs_industry"),
            IndexModel([("posted_at", DESCENDING)], name="jobs_posted_at"),
        ])

        # job_skills
        await db.job_skills.create_indexes([
            IndexModel([("job_id", ASCENDING)], name="job_skills_job_id"),
            IndexModel([("skill_id", ASCENDING)], name="job_skills_skill_id"),
        ])

        # job_applications
        await db.job_applications.create_indexes([
            IndexModel([("job_id", ASCENDING)], name="applications_job_id"),
            IndexModel([("trainee_id", ASCENDING)], name="applications_trainee_id"),
            IndexModel([("status", ASCENDING)], name="applications_status"),
        ])

        # employment_outcomes
        await db.employment_outcomes.create_indexes([
            IndexModel([("trainee_id", ASCENDING)], name="outcomes_trainee_id"),
            IndexModel(
                [("training_program_id", ASCENDING)], name="outcomes_program_id"
            ),
            IndexModel([("employment_date", DESCENDING)], name="outcomes_employment_date"),
        ])

        # skill_demand
        await db.skill_demand.create_indexes([
            IndexModel([("skill_id", ASCENDING)], name="demand_skill_id"),
            IndexModel([("location", ASCENDING)], name="demand_location"),
            IndexModel([("recorded_at", DESCENDING)], name="demand_recorded_at"),
        ])

        # district_data
        await db.district_data.create_indexes([
            IndexModel([("district", ASCENDING)], unique=True, name="district_name_unique"),
            IndexModel([("status", ASCENDING)], name="district_status"),
        ])

        # program_impact
        await db.program_impact.create_indexes([
            IndexModel([("program_id", ASCENDING)], unique=True, name="impact_program_unique"),
            IndexModel([("impact_score", DESCENDING)], name="impact_score"),
        ])

        # ai_conversations
        await db.ai_conversations.create_indexes([
            IndexModel([("user_id", ASCENDING)], name="conversations_user_id"),
            IndexModel([("created_at", DESCENDING)], name="conversations_created_at"),
        ])

        # email delivery audit trail
        await db.email_logs.create_indexes([
            IndexModel([("recipient", ASCENDING)], name="email_logs_recipient"),
            IndexModel([("user_id", ASCENDING)], name="email_logs_user_id"),
            IndexModel([("email_type", ASCENDING)], name="email_logs_type"),
            IndexModel([("status", ASCENDING)], name="email_logs_status"),
            IndexModel([("sent_at", DESCENDING)], name="email_logs_sent_at"),
        ])

        logger.info("Database indexes created successfully")

    except Exception as exc:
        logger.error("Failed to create indexes: %s", exc)
        raise
