from __future__ import annotations

from fastapi import APIRouter

from app.routes.compat import router as compat_router
from app.routes.auth import router as auth_router
from app.routes.trainees import router as trainees_router
from app.routes.skills import router as skills_router
from app.routes.assessments import router as assessments_router
from app.routes.training import router as training_router
from app.routes.employers import router as employers_router
from app.routes.jobs import router as jobs_router
from app.routes.employment import router as employment_router
from app.routes.intelligence import router as intelligence_router
from app.routes.analytics import router as analytics_router
from app.routes.ai import router as ai_router
from app.routes.system import router as system_router
from app.routes.users import router as users_router

api_router = APIRouter()

# Compat routes first — they cover ALL the paths the generated frontend hooks call.
# These are the "source of truth" paths for the existing OpenAPI contract.
api_router.include_router(compat_router)

# Auth routes — new paths not in original spec
api_router.include_router(auth_router)

# Trainees — /trainees/me and /trainees/{id}/PUT (compat handles GET + PATCH)
api_router.include_router(trainees_router)

# Skills — /trainees/me/skills/* (user skill management; compat handles /skills list)
api_router.include_router(skills_router)

# Assessments
api_router.include_router(assessments_router)

# Training — /enrollments/* and /certifications/* (compat handles /training-programs)
api_router.include_router(training_router)

# Employers
api_router.include_router(employers_router)

# Jobs — /jobs/{id} GET/PUT/DELETE and /jobs/{id}/applications
# (compat handles list/create/apply/matches)
api_router.include_router(jobs_router)

# Employment outcomes
api_router.include_router(employment_router)

# Intelligence (all /intelligence/* paths)
api_router.include_router(intelligence_router)

# Analytics (/analytics/*)
api_router.include_router(analytics_router)

# AI features (/ai/*)
api_router.include_router(ai_router)

# System routes (/system/*)
api_router.include_router(system_router)
api_router.include_router(users_router)
