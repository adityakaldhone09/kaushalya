# KAUSHALYA — AI-powered Skill & Employment Intelligence Platform

**SIH Problem Statement: SIH26135**

KAUSHALYA is a full-stack workforce intelligence platform that connects Skills → Training → Assessment → Certification → Employment → Outcomes → Industry Demand → Skill Gap Analysis → Future Skill Prediction → Government Decision Support.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Folder Structure](#folder-structure)
6. [MongoDB Setup](#mongodb-setup)
7. [Environment Variables](#environment-variables)
8. [LLM / AI Setup](#llm--ai-setup)
9. [Backend Installation](#backend-installation)
10. [Frontend Installation](#frontend-installation)
11. [Database Seeding](#database-seeding)
12. [Running the Application](#running-the-application)
13. [Demo Accounts](#demo-accounts)
14. [API Documentation](#api-documentation)
15. [SIH Problem Statement Mapping](#sih-problem-statement-mapping)
16. [Troubleshooting](#troubleshooting)

---

## Project Overview

KAUSHALYA bridges the gap between skill supply and industry demand across Maharashtra. It provides:

- **Trainees** — a personalised career workspace with skill gap analysis, job matching, and an AI career advisor
- **Employers** — candidate discovery, job posting, and application management
- **Training Institutes** — program publishing, enrollment tracking, and placement analytics
- **Government Administrators** — district intelligence, skill demand forecasts, program impact scores, and AI-driven policy recommendations
- **Super Administrators** — full platform management

The platform's core differentiator is the **District Skill Digital Twin** — a unified, real-time intelligence view of every district's workforce, skills, training, employment, and industry demand.

---

## Key Features

| Feature | Details |
|---|---|
| JWT Authentication | Register / Login / Refresh / Logout with role-based access control |
| Employability Score | 7-factor weighted score: Skills, Assessment, Training, Certs, Experience, Demand, Profile |
| Skill Gap Engine | Deterministic Python calculation comparing trainee skills to target role requirements |
| Job Matching | 5-factor scoring: Skill Match 40%, Experience 20%, Education 10%, Location 10%, Role 20% |
| District Digital Twin | Unified district intelligence: workforce, skills, training, employment, forecast, AI recommendations |
| Skill Demand Analytics | Real-time demand vs supply with growth rate classification |
| Skill Forecasting | Linear projection model from historical demand data |
| Program Impact Score | Placement 30%, Retention 20%, Salary 15%, Skill Relevance 20%, Employer Satisfaction 15% |
| AI Career Advisor | OpenAI GPT-4o-mini with deterministic fallback when API key absent |
| AI Chat | Trainee-context-aware conversation with stored history |
| Government Analytics | MongoDB aggregation pipelines for employment, salary, retention, district KPIs |
| Assessment System | Skill assessments with auto-scoring and proficiency level calculation |

---

## Architecture

```
React Frontend (Vite + TypeScript)
        │  /api/*  (Vite proxy in dev)
        ▼
FastAPI Backend (Python 3.9+)
        │
        ├── Auth (JWT + bcrypt)
        ├── Routes (trainees, skills, jobs, training, employment, intelligence, analytics, AI)
        ├── Services (employability, skill_gap, job_matching)
        ├── Analytics (skill_demand, forecasting, district_intelligence, program_impact)
        └── AI (llm_service → OpenAI or deterministic fallback)
        │
        ▼
MongoDB (motor async driver)
  └── kaushalya_db
      ├── users, trainee_profiles, employers, training_institutes
      ├── skills, user_skills, skill_assessments, assessment_results
      ├── training_programs, enrollments, certifications
      ├── jobs, job_applications, employment_outcomes
      ├── skill_demand, district_data, program_impact
      └── ai_conversations, notifications
```

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 19.1 | UI framework |
| TypeScript | 5.9 | Type safety |
| Vite | 7.3 | Build tool + dev proxy |
| Tailwind CSS | 4.1 | Styling |
| Wouter | 3.3 | Client-side routing |
| TanStack Query | 5.9 | Data fetching + caching |
| Recharts | 2.15 | Charts |
| Lucide React | 0.545 | Icons |
| React Hook Form | 7.55 | Form management |
| Zod | 3.25 | Schema validation |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.9+ | Runtime |
| FastAPI | 0.115 | API framework |
| Uvicorn | 0.32 | ASGI server |
| Motor | 3.6+ | Async MongoDB driver |
| PyMongo | 4.9+ | MongoDB client |
| Pydantic | 2.10 | Data validation |
| python-jose | 3.3 | JWT |
| passlib + bcrypt | 1.7 / 4.2 | Password hashing |
| OpenAI | 1.57 | LLM integration |
| pandas + numpy | 2+ / 1.26+ | Data analysis |
| scikit-learn | 1.4+ | ML (forecasting) |

---

## Folder Structure

```
kaushalya/
├── artifacts/
│   └── kaushalya/              # React frontend
│       ├── src/
│       │   ├── pages/          # operations.tsx, trainee.tsx, roles.tsx, public.tsx
│       │   ├── components/     # kaushalya-ui.tsx, ui/*
│       │   ├── contexts/       # AuthContext.tsx
│       │   ├── lib/            # auth.ts
│       │   └── services/       # api.ts (direct API calls)
│       ├── .env
│       └── vite.config.ts
│
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config/settings.py
│   │   ├── database/connection.py, indexes.py
│   │   ├── auth/jwt.py, password.py, dependencies.py
│   │   ├── routes/             # auth, trainees, skills, jobs, training, employment,
│   │   │                       # employers, intelligence, analytics, ai, dashboard, compat
│   │   ├── services/           # employability.py, skill_gap.py, job_matching.py
│   │   ├── analytics/          # skill_demand.py, forecasting.py,
│   │   │                       # district_intelligence.py, program_impact.py
│   │   ├── schemas/            # auth, trainee, skill, job, training, employment, ai, intelligence
│   │   └── ai/llm_service.py
│   ├── scripts/seed_database.py
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
│
├── lib/
│   ├── api-spec/openapi.yaml   # Source-of-truth OpenAPI spec
│   ├── api-client-react/       # Generated TanStack Query hooks
│   ├── api-zod/                # Generated Zod validators
│   └── db/                     # Drizzle ORM (legacy PostgreSQL — not used by FastAPI backend)
│
├── pnpm-workspace.yaml
├── start.sh                    # Convenience startup script
└── README.md
```

---

## MongoDB Setup

### Option 1 — Local MongoDB (recommended for development)

**macOS (manual install):**
```bash
# Download and extract MongoDB 7
curl -fsSL -o /tmp/mongodb.tgz "https://fastdl.mongodb.org/osx/mongodb-macos-aarch64-7.0.14.tgz"
tar -xzf /tmp/mongodb.tgz -C ~
mv ~/mongodb-macos-aarch64-7.0.14 ~/mongodb
mkdir -p ~/mongodb/data/db ~/mongodb/logs

# Start MongoDB
~/mongodb/bin/mongod \
  --dbpath ~/mongodb/data/db \
  --logpath ~/mongodb/logs/mongod.log \
  --fork --bind_ip 127.0.0.1 --port 27017
```

**macOS (Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
```

### Option 2 — MongoDB Atlas (cloud)

1. Create a free cluster at [https://cloud.mongodb.com](https://cloud.mongodb.com)
2. Get your connection string: `mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/kaushalya_db`
3. Set it as `MONGODB_URI` in `backend/.env`

---

## Environment Variables

### Backend — `backend/.env`

```env
APP_NAME=KAUSHALYA
ENVIRONMENT=development

HOST=0.0.0.0
PORT=8000

# MongoDB — local or Atlas
MONGODB_URI=mongodb://localhost:27017/kaushalya_db
MONGODB_DB_NAME=kaushalya_db

# JWT — change in production
JWT_SECRET=kaushalya-sih-2026-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
FRONTEND_URL=http://localhost:5173

# LLM — leave blank to use deterministic fallback
LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

### Frontend — `artifacts/kaushalya/.env`

```env
PORT=5173
BASE_PATH=/
VITE_API_URL=http://localhost:8000
```

> **Note:** Never commit `.env` files. Both directories have `.gitignore` entries for them.

---

## LLM / AI Setup

The AI features work in two modes:

**With OpenAI API key** — uses GPT-4o-mini for career advice, skill gap explanations, district insights, and program recommendations.

**Without API key (default / demo)** — uses a deterministic fallback that generates responses from real database data. All responses are clearly labelled `[Deterministic — AI unavailable]`. The application never crashes and never pretends AI was used when it wasn't.

To enable AI:
```env
# In backend/.env
OPENAI_API_KEY=sk-...your-key...
OPENAI_MODEL=gpt-4o-mini
```

---

## Backend Installation

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate (macOS / Linux)
source venv/bin/activate

# Activate (Windows)
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Frontend Installation

The project uses **pnpm workspaces**. Install from the root:

```bash
# Install pnpm if not present
curl -fsSL https://get.pnpm.io/install.sh | sh -
source ~/.zshrc   # or restart your terminal

# Install all workspace dependencies
pnpm install
```

---

## Database Seeding

Start MongoDB first, then run:

```bash
cd backend
source venv/bin/activate
python scripts/seed_database.py
```

The seed script inserts:

| Collection | Count |
|---|---|
| Districts | 10 Maharashtra districts |
| Skills | 30 skills across 12 categories |
| Employers | 20 real Maharashtra companies |
| Training Institutes | 10 institutes |
| Training Programs | 20 programs |
| Jobs | 75 open positions |
| Trainees | 200 (including demo accounts) |
| Job Applications | 150 |
| Employment Outcomes | ~100 |
| Skill Demand Records | 300 (30 skills × 10 districts) |
| Assessments | 4 (Python, SQL, AWS, Cybersecurity) |

---

## Running the Application

### Quick Start (automated)

```bash
# From project root
./start.sh
```

### Manual (two terminals)

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
# From project root
PORT=5173 BASE_PATH=/ pnpm --filter @workspace/kaushalya run dev
```

### Access Points

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/api/healthz |

---

## Demo Accounts

All demo accounts use the password: **`Demo@1234`**

| Role | Email | Dashboard |
|---|---|---|
| Trainee | `trainee@kaushalya.demo` | `/trainee/dashboard` |
| Employer | `employer@kaushalya.demo` | `/employer/dashboard` |
| Training Institute | `institute1@maharashtradi.edu.in` | `/institute/dashboard` |
| Government Admin | `admin@kaushalya.demo` | `/admin/dashboard` |
| Super Admin | `superadmin@kaushalya.demo` | `/admin/dashboard` |

**Demo Trainee Profile (Aarav Kulkarni):**
- District: Pune
- Target Role: Cloud Engineer
- Employability Score: 82 / HIGH
- Skills: Python ✓, SQL ✓, React ✓, AWS ⚠ (gap), Docker ✗ (missing)

---

## API Documentation

Full interactive docs at `http://localhost:8000/docs`

### Authentication
| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/refresh` | Refresh token |
| POST | `/api/auth/logout` | Logout |

### Trainees
| Method | Path | Description |
|---|---|---|
| GET | `/api/trainees/me` | Get own profile |
| PUT | `/api/trainees/me` | Update own profile |
| GET | `/api/trainees/{id}` | Get trainee by ID |
| PATCH | `/api/trainees/{id}` | Patch trainee |
| GET | `/api/trainees/me/skills` | List own skills |
| POST | `/api/trainees/me/skills` | Add skill |
| PUT | `/api/trainees/me/skills/{skill_id}` | Update skill |
| DELETE | `/api/trainees/me/skills/{skill_id}` | Remove skill |

### Intelligence & Analytics
| Method | Path | Description |
|---|---|---|
| GET | `/api/intelligence/employability/me` | Employability score (7-factor) |
| GET | `/api/intelligence/skill-gap/me` | Skill gap vs target role |
| POST | `/api/intelligence/skill-gap/analyze` | Analyze gap for custom role |
| GET | `/api/intelligence/skill-demand` | Skill demand list |
| GET | `/api/intelligence/forecast` | 12-month demand forecast |
| GET | `/api/intelligence/districts` | All district snapshots |
| GET | `/api/intelligence/districts/{name}` | Single district |
| GET | `/api/intelligence/districts/{name}/digital-twin` | Full district digital twin |
| GET | `/api/intelligence/program-impact` | All program impact scores |
| GET | `/api/intelligence/program-impact/{id}` | Single program impact |

### AI
| Method | Path | Description |
|---|---|---|
| POST | `/api/assistant/career-advice` | Career advice (compat path) |
| POST | `/api/ai/chat` | AI chat with conversation history |
| POST | `/api/ai/explain-skill-gap` | Explain skill gap in plain language |
| POST | `/api/ai/district-insight` | District AI insight |
| POST | `/api/ai/program-insight` | Program impact explanation |
| GET | `/api/ai/conversations` | List conversations |

### Jobs
| Method | Path | Description |
|---|---|---|
| GET | `/api/jobs` | List jobs (search, location filters) |
| POST | `/api/jobs` | Create job posting |
| GET | `/api/jobs/{id}` | Get job |
| PUT | `/api/jobs/{id}` | Update job |
| DELETE | `/api/jobs/{id}` | Delete job |
| POST | `/api/jobs/{id}/apply` | Apply to job |
| GET | `/api/job-matches/{trainee_id}` | Ranked job matches |

### Dashboards
| Method | Path | Description |
|---|---|---|
| GET | `/api/dashboard/government` | Government KPI dashboard |
| GET | `/api/dashboard/trainee/{id}` | Trainee dashboard |

---

## Datasets and Data Import

KAUSHALYA comes with curated datasets that power the skill demand analysis, job matching, and workforce intelligence features.

### Available Datasets

| Dataset | Location | Size | Contents | Purpose |
|---|---|---|---|---|
| **Jobs** | `all_job_post.csv` | 4.7 MB | 1,167 job postings with skills, category, company data | Job search, matching, skill demand |
| **Professional Profiles** | `Dataset_1/india_professional_skills_intelligence.csv` | ~30 MB | 75,000+ professional profiles with skills, salary, industry, location, employability score | Workforce intelligence, skills taxonomy, salary benchmarking |
| **Assessment Q&A** | `Dataset_2/S08_question_answer_pairs.txt`, etc. | ~400 KB | Historical/factual Q&A pairs (Abraham Lincoln, etc.) | Optional enrichment for general knowledge |
| **Skills Taxonomy** | `Dataset_3/skills.csv` | ~3 MB | 75,000+ unique skills from professional profiles | Skill taxonomy, normalization, autocomplete |

### Dataset Inspection & Validation

Before importing, inspect the datasets:

```bash
cd backend

# Validate dataset files exist
python3 << 'EOF'
from pathlib import Path
for dataset in [
    Path("../Dataset_1/india_professional_skills_intelligence.csv"),
    Path("../Dataset_3/skills.csv"),
    Path("../all_job_post.csv"),
]:
    print(f"{'✓' if dataset.exists() else '✗'} {dataset.name} ({dataset.stat().st_size / 1_000_000:.1f} MB)")
EOF
```

### Importing Datasets

**Step 1: Import All Data**

```bash
# From backend/ directory
python3 scripts/import_datasets.py --dataset=all

# OR import selectively:
python3 scripts/import_datasets.py --dataset=jobs        # Only jobs
python3 scripts/import_datasets.py --dataset=skills      # Only skills
python3 scripts/import_datasets.py --dataset=profiles    # Only professional profiles

# Mode options:
python3 scripts/import_datasets.py --mode=upsert         # Default: update existing
python3 scripts/import_datasets.py --mode=replace        # Destructive: replace all
```

**Step 2: Seed Demo Assessments**

```bash
python3 scripts/seed_assessments.py
```

This creates 4 demo assessments with ~15 questions each, mapped to common skills:
- Python Fundamentals (5 questions)
- JavaScript Basics (3 questions)
- Data Structures (2 questions)
- React Fundamentals (2 questions)

**Step 3: Verify Import**

```bash
# Check backend MongoDB health
curl -s http://localhost:8000/api/healthz | jq

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "collections": {
#     "jobs": 1167,
#     "skills": 75000+,
#     "skill_assessments": 4,
#     "professional_profiles": 75000+
#   }
# }
```

### Dataset Provenance and Quality

All imported records include:
- `source_dataset` — where the record came from
- `imported_at` — timestamp of import
- `dataset_version` — version number for tracking

**Skills Normalization:**
- Duplicate/similar skills are deduplicated
- Skill names are normalized (e.g., "JS", "JavaScript" → canonical "JavaScript")
- Skills are tagged with `category` and `demand_score` (calculated from job occurrences)

**Job Data:**
- Job titles are normalized (e.g., "React JS Developer", "React Developer" → aligned)
- Skills are extracted and normalized from `job_skill_set` field
- Salary ranges (where available) are standardized to annual LPA (Lakh Per Annum)

---

## SIH Problem Statement Mapping

**Problem Statement ID: SIH26135**

| Requirement | Implementation |
|---|---|
| Skill inventory of trainees | `user_skills` collection, proficiency tracking, assessment verification |
| Training program linkage | `training_programs` → `enrollments` → `certifications` |
| Assessment & certification | `skill_assessments`, `assessment_results`, auto-scoring, proficiency levels |
| Employment outcome tracking | `employment_outcomes`: employer, salary, retention_6m, retention_12m, career progression |
| Industry demand data | `skill_demand` collection: 300+ records, growth rate, job count, supply vs demand |
| Skill gap analysis | `/api/intelligence/skill-gap/me` — Python deterministic calculation, no LLM dependency |
| Future skill prediction | `/api/intelligence/forecast` — linear projection model, growth rate extrapolation |
| District-level intelligence | `/api/intelligence/districts` — 10 Maharashtra districts with placement, salary, gap status |
| District Digital Twin (USP) | `/api/intelligence/districts/{name}/digital-twin` — unified workforce, skills, training, employment, forecast, recommendations |
| Government decision support | `/api/dashboard/government` — 8 KPIs, employment trend, district comparison, top gaps, insights |
| AI-powered recommendations | `/api/ai/career-advice`, `/api/ai/district-insight`, `/api/ai/program-insight` — OpenAI + deterministic fallback |
| Program impact measurement | Placement 30%, Retention 20%, Salary 15%, Skill Relevance 20%, Employer Satisfaction 15% |
| Role-based access | TRAINEE, EMPLOYER, TRAINING_INSTITUTE, GOVERNMENT_ADMIN, SUPER_ADMIN |
| Privacy / data protection | Role-scoped API responses, no PII in government aggregates, JWT-secured endpoints |

### SIH Demo Flow

**Government Admin (`admin@kaushalya.demo`):**
1. Login → `/admin/dashboard` — 8 live KPIs from MongoDB
2. `/admin/districts` — select Pune — placement rate, skill supply/demand, recommendation
3. Click district → District Digital Twin: workforce, skills, training, employment, forecast
4. `/admin/skill-demand` — Cloud Computing demand ↑42%, supply gap critical
5. `/admin/predictions` — AWS predicted 25,481 roles, +43% growth
6. `/admin/program-impact` — Applied Data Science impact score 82

**Trainee (`trainee@kaushalya.demo`):**
1. Login → `/trainee/dashboard` — KAUSHALYA Score: **82/100 HIGH**
2. `/trainee/skill-gap` — Python ✓, SQL ✓, React ✓, AWS ⚠ (priority), Docker ✗ (missing)
3. `/trainee/jobs` — 50 job matches, top: Cloud Engineer 89% match
4. `/trainee/recommendations` — Ask: *"What should I learn next?"*
   → AI responds using trainee's actual skills, district demand, and target role data

---

## Troubleshooting

### MongoDB won't start
```bash
# Check if already running
lsof -i :27017

# Kill existing process
kill $(lsof -t -i:27017)

# Start fresh
~/mongodb/bin/mongod --dbpath ~/mongodb/data/db --logpath ~/mongodb/logs/mongod.log --fork --bind_ip 127.0.0.1 --port 27017
```

### Backend fails with "MongoDB connection failed"
- Ensure MongoDB is running: `curl -s http://localhost:8000/api/healthz` — check `"database"` field
- Check `MONGODB_URI` in `backend/.env`
- For Atlas: ensure IP whitelist includes your machine

### Frontend shows "Intelligence is temporarily unavailable"
- Backend must be running on port 8000
- Check proxy in `vite.config.ts` — `target: 'http://localhost:8000'`
- Check CORS: `FRONTEND_URL=http://localhost:5173` in `backend/.env`

### pnpm install fails on macOS
```bash
# Make sure darwin-arm64 exclusions are removed from pnpm-workspace.yaml
# Then reinstall
pnpm install
```

### bcrypt warning "(trapped) error reading bcrypt version"
This is a harmless passlib/bcrypt compatibility warning. Passwords hash and verify correctly. Suppress it by pinning `bcrypt==4.0.1` if needed.

### AI shows "[Deterministic — AI unavailable]"
This is expected when `OPENAI_API_KEY` is not set. Add your key to `backend/.env` and restart the backend.

### Seed script inserts 0 employment outcomes
The script only inserts outcomes for trainees whose `employment_status` is `"Employed"`. Run the seed, then restart — the analytics will populate from the 39+ outcomes inserted.

### Port already in use
```bash
# Kill port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```
