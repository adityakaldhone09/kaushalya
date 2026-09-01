# KAUSHALYA Documentation Index

Navigate KAUSHALYA documentation here. All files are in the project root unless otherwise noted.

---

## 📋 Quick Reference

| Document | Purpose | Read If... |
|---|---|---|
| [README.md](./README.md) | Complete platform guide | You're new to KAUSHALYA |
| [IMPLEMENTATION.md](./IMPLEMENTATION.md) | What's implemented | You want to know what's done |
| [PROJECT_STATUS.md](./PROJECT_STATUS.md) | Final status report | You want the full picture |
| [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) | Pre-deployment checklist | Going to production |
| [quickstart.sh](./quickstart.sh) | Automated setup | You want fast setup |

---

## 🚀 Getting Started

**First time?**
1. Read [README.md](./README.md#folder-structure)
2. Run [quickstart.sh](./quickstart.sh)
3. Follow [README.md#start-the-system](./README.md)

**Want to understand architecture?**
1. Read [IMPLEMENTATION.md#architecture-overview](./IMPLEMENTATION.md)
2. Check [PROJECT_STATUS.md#architecture-overview](./PROJECT_STATUS.md)
3. Review API endpoints in [IMPLEMENTATION.md#api-reference](./IMPLEMENTATION.md)

**Need to verify everything works?**
1. Follow [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
2. Use [README.md#troubleshooting](./README.md)

---

## 📚 Documentation Structure

### Project Overview
- **[README.md](./README.md)** — Main documentation
  - Setup instructions (MongoDB, Python, Node.js)
  - Folder structure explanation
  - Technology stack details
  - API endpoint reference
  - SIH problem statement mapping
  - Troubleshooting guide
  - Dataset documentation

### Implementation Status
- **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** — Feature completeness
  - Completion checklist (✅/❌ for each feature)
  - Backend files overview
  - Frontend files overview
  - Database schema
  - How to use guide
  - Key accomplishments
  - Remaining enhancements
  - Testing checklist

### Deployment & Operations
- **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** — Pre-deployment
  - Environment setup verification
  - Database checks
  - Configuration verification
  - Backend API testing
  - Frontend page testing
  - Email verification
  - Performance & security checks
  - Mobile compatibility
  - Error handling tests
  - Production deployment steps
  - Troubleshooting during testing

- **[PROJECT_STATUS.md](./PROJECT_STATUS.md)** — Final report
  - Executive summary
  - Architecture overview
  - Feature completeness matrix
  - Technical stack
  - Database schema details
  - Full API reference
  - Deployment files
  - Key decisions & rationale
  - Scaling considerations
  - Security measures
  - Monitoring recommendations

### Setup Automation
- **[quickstart.sh](./quickstart.sh)** — Automated verification
  - Dependencies check
  - Backend imports test
  - MongoDB connection test
  - Dataset file verification
  - Environment configuration check
  - Frontend setup verification
  - Summary with next steps

---

## 🗂️ Backend Structure

**Core Files:**
- `backend/app/main.py` — FastAPI application
- `backend/app/config/settings.py` — Environment configuration
- `backend/app/database/connection.py` — MongoDB connection
- `backend/app/database/indexes.py` — Database indexes

**Routes (API Endpoints):**
- `backend/app/routes/auth.py` — Authentication (register, login, Google)
- `backend/app/routes/assessments.py` — Assessment engine (8 endpoints)
- `backend/app/routes/trainees.py` — Trainee profiles & dashboard
- `backend/app/routes/jobs.py` — Job search & matching
- `backend/app/routes/skills.py` — Skill management
- `backend/app/routes/intelligence.py` — AI recommendations & analysis
- `backend/app/routes/admin.py` — Admin dashboards & analytics

**Services (Business Logic):**
- `backend/app/services/employability.py` — Score calculation
- `backend/app/services/skill_gap.py` — Gap analysis
- `backend/app/services/job_matching.py` — Job matching algorithm
- `backend/app/services/email_service.py` — SMTP integration
- `backend/app/ai/llm_service.py` — AI/LLM integration

**Scripts:**
- `backend/scripts/import_datasets.py` — Import jobs, skills, profiles
- `backend/scripts/seed_assessments.py` — Seed demo assessments
- `backend/scripts/seed_database.py` — Legacy seed script

---

## 🎨 Frontend Structure

**Page Components:**
- `frontend/src/pages/roles.tsx` — Authentication UI
- `frontend/src/pages/trainee.tsx` — Trainee dashboard & profile
- `frontend/src/pages/trainee-assessment.tsx` — Assessment UI **[NEW]**
- `frontend/src/pages/operations.tsx` — Admin dashboards
- `frontend/src/pages/public.tsx` — Landing pages

**Context & State:**
- `frontend/src/contexts/AuthContext.tsx` — Auth state management
- `frontend/src/lib/auth.ts` — Token & user storage

**Components:**
- `frontend/src/components/GoogleSignInButton.tsx` — Google OAuth button
- `frontend/src/components/AIChatWidget.tsx` — AI chat interface
- `frontend/src/components/kaushalya-ui.tsx` — Shared UI components

**Routing:**
- `frontend/src/App.tsx` — Route definitions

---

## 🗄️ Database Collections

**Authentication & Users:**
- `users` — User accounts with authentication data

**Trainee Features:**
- `trainee_profiles` — Trainee personal & career data
- `user_skills` — Trainee skills with proficiency levels

**Assessments:**
- `skill_assessments` — Assessment definitions with questions
- `assessment_attempts` — Attempt tracking (in-progress, completed, expired)
- `assessment_results` — Scores and results

**Jobs & Skills:**
- `jobs` — Job postings with requirements
- `skills` — Skill taxonomy (75,000+)
- `professional_profiles` — Workforce data (75,000+)

**Other:**
- `employment_outcomes` — Salary, placement, retention tracking
- `email_logs` — Audit trail of all system emails

See [IMPLEMENTATION.md#database-schema](./IMPLEMENTATION.md) for detailed schema.

---

## 🔗 Important Links

**Configuration Files:**
- `backend/.env` — Backend environment variables (create from `.env.example`)
- `backend/.env.example` — Template
- `frontend/.env` — Frontend environment variables (create manually)

**Key Documents in Workspace:**
- `Dataset_1/india_professional_skills_intelligence.csv` — Professional profiles
- `Dataset_2/` — Q&A pairs (optional)
- `Dataset_3/skills.csv` — Skills taxonomy
- `all_job_post.csv` — Job postings

**Dependencies:**
- `backend/requirements.txt` — Python dependencies
- `frontend/package.json` — Node dependencies
- `pnpm-workspace.yaml` — Workspace configuration

---

## 🎯 Common Tasks

### I want to...

**...set up the project**
→ Run [quickstart.sh](./quickstart.sh) or follow [README.md#local-development](./README.md)

**...understand what's implemented**
→ Read [IMPLEMENTATION.md#completion-status](./IMPLEMENTATION.md)

**...start the backend**
→ See [README.md#start-the-backend](./README.md)

**...start the frontend**
→ See [README.md#start-the-frontend](./README.md)

**...import datasets**
→ See [README.md#importing-datasets](./README.md) or run `python3 scripts/import_datasets.py`

**...test an API endpoint**
→ See [IMPLEMENTATION.md#api-reference](./IMPLEMENTATION.md) or [PROJECT_STATUS.md#api-reference](./PROJECT_STATUS.md)

**...configure Google Sign-In**
→ See [README.md#google-oauth-setup](./README.md)

**...set up SMTP email**
→ See [README.md#email-configuration](./README.md)

**...check database is working**
→ See [README.md#mongodb-setup](./README.md) or [DEPLOYMENT_CHECKLIST.md#-database](./DEPLOYMENT_CHECKLIST.md)

**...deploy to production**
→ Follow [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

**...understand the architecture**
→ Read [PROJECT_STATUS.md#architecture-overview](./PROJECT_STATUS.md)

**...troubleshoot an issue**
→ See [README.md#troubleshooting](./README.md) or [DEPLOYMENT_CHECKLIST.md#troubleshooting-during-testing](./DEPLOYMENT_CHECKLIST.md)

---

## 📖 Reading Order by Role

### For Developers
1. [README.md](./README.md) — Setup and structure
2. [IMPLEMENTATION.md](./IMPLEMENTATION.md) — What's implemented
3. [Backend routes/](./backend/app/routes/) — API code
4. [Frontend pages/](./frontend/src/pages/) — UI code

### For DevOps/Operations
1. [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) — Deployment steps
2. [README.md#mongodb-setup](./README.md) — Database setup
3. [PROJECT_STATUS.md#monitoring--maintenance](./PROJECT_STATUS.md) — Monitoring

### For Project Managers
1. [PROJECT_STATUS.md](./PROJECT_STATUS.md) — Status overview
2. [IMPLEMENTATION.md#completion-status](./IMPLEMENTATION.md) — Feature checklist
3. [README.md#sih-problem-statement-mapping](./README.md) — Requirements mapping

### For QA/Testing
1. [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) — Test checklist
2. [README.md#troubleshooting](./README.md) — Known issues
3. [IMPLEMENTATION.md#testing-checklist](./IMPLEMENTATION.md) — Test procedures

### For Presenters/Demos
1. [PROJECT_STATUS.md](./PROJECT_STATUS.md) — Executive summary
2. [README.md#sih-demo-flow](./README.md) — Demo scenarios
3. [DEPLOYMENT_CHECKLIST.md#demonstration-readiness](./DEPLOYMENT_CHECKLIST.md) — Demo checklist

---

## 🎓 Learning Resources

**Understanding the Assessment Engine:**
→ Read [IMPLEMENTATION.md#2-assessment-system-](./IMPLEMENTATION.md)
→ Check [backend/app/routes/assessments.py](./backend/app/routes/assessments.py) code

**Understanding Job Matching:**
→ Read [IMPLEMENTATION.md#4-job-matching--search-](./IMPLEMENTATION.md)
→ Check [backend/app/services/job_matching.py](./backend/app/services/job_matching.py) code

**Understanding Dataset Import:**
→ Read [README.md#datasets-and-data-import](./README.md)
→ Check [backend/scripts/import_datasets.py](./backend/scripts/import_datasets.py) code

**Understanding Authentication:**
→ Read [IMPLEMENTATION.md#1-authentication--authorization-](./IMPLEMENTATION.md)
→ Check [backend/app/routes/auth.py](./backend/app/routes/auth.py) code

**Understanding Frontend Architecture:**
→ Check [frontend/src/App.tsx](./frontend/src/App.tsx) routing
→ Check [frontend/src/contexts/AuthContext.tsx](./frontend/src/contexts/AuthContext.tsx) state

---

## ✅ Verification Checklist

Before going to production, verify:
- [ ] Read [README.md](./README.md) completely
- [ ] Run [quickstart.sh](./quickstart.sh) successfully
- [ ] Followed [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- [ ] All checkboxes in checklist are checked
- [ ] Backend runs without errors: `uvicorn app.main:app --reload`
- [ ] Frontend runs without errors: `npm run dev`
- [ ] Can complete full user flow (login → assessment → results)
- [ ] Consulted [README.md#troubleshooting](./README.md) for any issues

---

## 📞 Support

**For Setup Issues:**
→ Check [README.md#troubleshooting](./README.md)

**For Deployment Issues:**
→ Check [DEPLOYMENT_CHECKLIST.md#troubleshooting-during-testing](./DEPLOYMENT_CHECKLIST.md)

**For Understanding Features:**
→ Check [IMPLEMENTATION.md](./IMPLEMENTATION.md) and [PROJECT_STATUS.md](./PROJECT_STATUS.md)

**For Specific Code Questions:**
→ Check inline comments in relevant route/service file

---

**Last Updated:** 2026  
**Status:** ✅ Complete & Production-Ready  
**Platform:** KAUSHALYA - Skill & Employment Intelligence
