# KAUSHALYA Pre-Deployment Checklist

Use this checklist to verify all systems are working before going live.

## 🔧 Environment Setup

- [ ] MongoDB is running (local or Atlas)
  - Test: `curl -s http://localhost:8000/api/healthz | jq '.database'` should show `"connected"`
- [ ] Python 3.9+ installed
  - Test: `python3 --version`
- [ ] Node.js 18+ installed
  - Test: `node --version && npm --version`
- [ ] Backend dependencies installed
  - Test: `cd backend && python3 -c "import fastapi, motor, pydantic; print('OK')"`
- [ ] Frontend dependencies installed
  - Test: `cd frontend && npm list react react-dom | head -3`

## 🗄️ Database

- [ ] MongoDB connection works
  - Test: `python3 -c "from motor.motor_asyncio import AsyncIOMotorClient; AsyncIOMotorClient('mongodb://localhost:27017').close()"`
- [ ] Database `kaushalya_db` exists
  - Test: `mongosh --eval "db.listCollections()" kaushalya_db` (or via MongoDB Compass)
- [ ] Datasets imported (optional but recommended)
  ```bash
  cd backend
  python3 scripts/import_datasets.py --dataset=all
  ```
  - Verify: Check collections: `jobs`, `skills`, `professional_profiles`, `skill_assessments`
- [ ] Indexes created
  - Test: `mongosh --eval "db.jobs.getIndexes()" kaushalya_db`
- [ ] Demo assessments seeded (if using demo mode)
  ```bash
  python3 scripts/seed_assessments.py
  ```
  - Verify: `skill_assessments` collection has 4 documents

## 🔐 Configuration

### Backend `.env`
- [ ] `MONGODB_URI` set correctly
  - Example: `mongodb://localhost:27017` or `mongodb+srv://user:pass@cluster.mongodb.net`
- [ ] `MONGODB_DB_NAME=kaushalya_db`
- [ ] `JWT_SECRET` set to secure random value
  - ⚠️ **CRITICAL**: Change from default in production
- [ ] `JWT_ALGORITHM=HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=1440` (or desired expiry)
- [ ] Email configuration (at least one should work):
  - [ ] `SMTP_HOST=smtp.gmail.com`
  - [ ] `SMTP_PORT=587`
  - [ ] `SMTP_USERNAME=your-email@gmail.com`
  - [ ] `SMTP_PASSWORD=your-app-password` (Gmail: generate in Security settings)
  - [ ] `SMTP_FROM_EMAIL=your-email@gmail.com`
  - OR configure alternate email provider
- [ ] AI/LLM configuration (optional):
  - [ ] `GEMINI_API_KEY` (for Gemini models)
  - [ ] `GROQ_API_KEY` (for Groq models)
  - [ ] `OPENAI_API_KEY` (for OpenAI models)
- [ ] `FRONTEND_URL=http://localhost:5173` (dev) or `https://yourdomain.com` (prod)
- [ ] Google OAuth (for sign-in button):
  - [ ] `GOOGLE_CLIENT_ID=<from Google Console>`
  - [ ] `GOOGLE_CLIENT_SECRET=<from Google Console>`

### Frontend `.env`
- [ ] `VITE_API_URL=http://localhost:8000` (dev) or `https://api.yourdomain.com` (prod)
- [ ] `VITE_GOOGLE_CLIENT_ID=<from Google Console>`

## ✅ Backend API Endpoints

Test each category:

### Health Check
- [ ] `GET http://localhost:8000/api/healthz`
  - Expected: `{"status": "healthy", "database": "connected"}`

### Authentication
- [ ] `POST http://localhost:8000/api/auth/register`
  - Body: `{"email": "test@example.com", "password": "Test123!", "role": "TRAINEE"}`
- [ ] `POST http://localhost:8000/api/auth/login`
  - Body: `{"username": "test@example.com", "password": "Test123!"}`
- [ ] `POST http://localhost:8000/api/auth/google`
  - Body: `{"credential": "<google-token>", "role": "TRAINEE"}`
- [ ] `GET http://localhost:8000/api/auth/me` (with Bearer token)
  - Should return: `{"id": "...", "email": "...", "role": "TRAINEE"}`

### Assessments
- [ ] `GET http://localhost:8000/api/assessments`
  - Should return list of available assessments
- [ ] `POST http://localhost:8000/api/assessments/{id}/start` (with Bearer token)
  - Should return: `{"attempt_id": "...", "started_at": "...", "time_limit_minutes": 30}`
- [ ] `GET http://localhost:8000/api/assessments/attempts/{attempt_id}` (with Bearer token)
  - Should return: questions WITHOUT `correct_option_id`
- [ ] `POST http://localhost:8000/api/assessments/attempts/{attempt_id}/answer`
  - Body: `{"question_id": "q1", "selected_option_id": "opt1"}`
- [ ] `POST http://localhost:8000/api/assessments/attempts/{attempt_id}/submit`
  - Should return: `{"assessment_results_id": "...", "score": 82, "proficiency": "Advanced"}`
- [ ] `GET http://localhost:8000/api/assessments/results/{attempt_id}`
  - Should return full result with score breakdown

### Jobs
- [ ] `GET http://localhost:8000/api/jobs` (optional filter: `?skill=Python`)
  - Should return list of jobs
- [ ] `GET http://localhost:8000/api/jobs/{id}`
  - Should return single job with details

### Trainees
- [ ] `GET http://localhost:8000/api/trainees/me` (with Bearer token)
  - Should return trainee profile
- [ ] `PUT http://localhost:8000/api/trainees/me` (with Bearer token)
  - Update profile fields
- [ ] `GET http://localhost:8000/api/trainees/me/summary`
  - Should return dashboard data (KPIs, scores)

### Intelligence
- [ ] `GET http://localhost:8000/api/intelligence/skill-gap/me` (with Bearer token)
  - Should return skill gaps
- [ ] `GET http://localhost:8000/api/intelligence/job-matches/me` (with Bearer token)
  - Should return recommended jobs

## 🎨 Frontend Pages

Test each page loads without errors:

### Public Pages
- [ ] `http://localhost:5173/` → Landing page loads
- [ ] `http://localhost:5173/how-it-works` → Info page loads
- [ ] `http://localhost:5173/about` → About page loads

### Authentication Pages
- [ ] `http://localhost:5173/login` → Login form with Google button
- [ ] `http://localhost:5173/register` → Register form with Google button
- [ ] `http://localhost:5173/forgot-password` → Password recovery
- [ ] Can register new account → Verify email sends (check inbox)
- [ ] Can login with email/password
- [ ] Can login with Google (if configured)

### Trainee Pages (must be logged in)
- [ ] `http://localhost:5173/trainee/dashboard` → Loads with KPIs
- [ ] `http://localhost:5173/trainee/profile` → Can view/edit profile
- [ ] `http://localhost:5173/trainee/skills` → Shows skills or empty state
- [ ] `http://localhost:5173/trainee/skill-gap` → Shows gaps or empty state
- [ ] `http://localhost:5173/trainee/assessment` → Lists available assessments
- [ ] Can start an assessment → Timer displays
- [ ] Can answer questions → Answers auto-save
- [ ] Can submit assessment → Shows score and results
- [ ] `http://localhost:5173/trainee/assessment/history` → Shows past attempts
- [ ] `http://localhost:5173/trainee/jobs` → Shows job list/search
- [ ] `http://localhost:5173/trainee/training` → Shows programs (if available)
- [ ] `http://localhost:5173/trainee/recommendations` → AI chat loads

### Admin Pages (if admin account exists)
- [ ] `http://localhost:5173/admin/dashboard` → 8 KPIs display
- [ ] `http://localhost:5173/admin/districts` → District list loads
- [ ] `http://localhost:5173/admin/skill-demand` → Chart displays
- [ ] `http://localhost:5173/admin/predictions` → Forecast data shows
- [ ] `http://localhost:5173/admin/program-impact` → Impact metrics display

## 📧 Email Verification

- [ ] Can register new account
- [ ] Verification email arrives within 2 minutes
- [ ] Email contains verification link
- [ ] Clicking link verifies email
- [ ] Can request password reset
- [ ] Password reset email arrives
- [ ] Can reset password successfully

## 🚀 Performance & Security

- [ ] Backend responds in < 500ms for typical requests
- [ ] Frontend page loads in < 3 seconds
- [ ] No console errors in browser DevTools
- [ ] No API errors in backend logs
- [ ] JWT token correctly validates user identity
- [ ] User can't access other users' data
- [ ] Assessment answers hidden until submission
- [ ] Timer enforced server-side (not just frontend)

## 📱 Mobile & Browser Compatibility

- [ ] Works in Chrome/Edge (latest)
- [ ] Works in Firefox (latest)
- [ ] Works in Safari (latest)
- [ ] Responsive on mobile (320px+)
- [ ] Responsive on tablet (768px+)
- [ ] Responsive on desktop (1920px+)

## 🐛 Error Handling

- [ ] Network error → Shows friendly message
- [ ] Database down → Shows graceful error
- [ ] Invalid credentials → Shows validation error
- [ ] Expired token → Redirects to login
- [ ] 404 page → Shows for nonexistent routes

## 📊 Data Verification

- [ ] At least 1 assessment available (demo or real)
- [ ] At least 1 job available (if imported)
- [ ] At least 1 skill available (if imported)
- [ ] User can complete full flow: Register → Profile → Assessment → Results
- [ ] Assessment score updates user skills
- [ ] Job matching calculates match percentage

## 🔄 Deployment Readiness

### Before Deploying to Production:

- [ ] Change `JWT_SECRET` to secure random value
  - Generate: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Set `FRONTEND_URL` to production domain
- [ ] Set `VITE_API_URL` to production API domain
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure database backups
- [ ] Set up monitoring/logging
- [ ] Test recovery from database failure
- [ ] Review all `.env` values are correct
- [ ] Test with production MongoDB Atlas cluster
- [ ] Test email with production email account
- [ ] Test with production LLM keys (if using AI)
- [ ] Load test: Can system handle 100 concurrent users?
- [ ] Create admin account for government dashboard
- [ ] Backup database before deploying
- [ ] Have rollback plan ready
- [ ] Document deployment procedures

## 🎯 Demonstration Readiness

If presenting to SIH judges:

- [ ] Backend running without errors: `ps aux | grep uvicorn`
- [ ] Frontend running without errors: `ps aux | grep vite`
- [ ] Can complete end-to-end flow in < 5 minutes
- [ ] Prepared demo data or know how to generate it
- [ ] Database populated with at least:
  - 3 demo accounts (trainee, employer, admin)
  - 4+ assessments with questions
  - 10+ jobs with skills
  - 100+ unique skills
- [ ] Can explain architecture and design decisions
- [ ] Can show assessment taking flow
- [ ] Can show job matching algorithm
- [ ] Can show AI recommendations
- [ ] Can handle "what if" questions about scaling

## ✨ Final Sign-Off

- [ ] All checkboxes above are checked
- [ ] No blocking errors in logs
- [ ] All critical paths tested (auth → assessment → results → jobs)
- [ ] System is stable for 10+ minute continuous use
- [ ] Ready for production or demonstration

---

## Troubleshooting During Testing

| Issue | Solution |
|---|---|
| Backend won't start | Check port 8000 isn't in use: `lsof -i :8000` |
| MongoDB connection refused | Ensure MongoDB running: `mongod --version` |
| Email verification not sending | Check SMTP config and internet connection |
| Assessment timer not working | Backend must enforce; frontend timer is UI only |
| Frontend can't reach API | Check CORS config; ensure `FRONTEND_URL` in backend .env |
| Google Sign-In not working | Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in backend |
| Assessment shows correct answers | This is a BUG — answers should be hidden until submission |
| Page shows "Loading..." forever | Check browser console for errors; check API is running |

---

For questions or issues, check:
- Backend logs: `tail -f ~/mongodb/logs/mongod.log` (if local MongoDB)
- Frontend console: Open DevTools (F12) → Console tab
- API response: Use `curl` or Postman to test endpoints directly
- Full documentation: See `README.md` and `IMPLEMENTATION.md`
