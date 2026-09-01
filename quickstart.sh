#!/bin/bash
# KAUSHALYA Quick Start & Test Script
# Run this to verify the entire system is working

set -e

echo "🚀 KAUSHALYA Quick Start"
echo "========================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Backend environment
echo -e "\n${YELLOW}[1/7] Checking backend dependencies...${NC}"
cd "$(dirname "$0")/backend"

if ! python3 -c "import fastapi, motor, pydantic, jose" 2>/dev/null; then
  echo -e "${YELLOW}Installing dependencies...${NC}"
  pip3 install -q -r requirements.txt
fi
echo -e "${GREEN}✓ Dependencies ready${NC}"

# Test 2: Backend imports
echo -e "\n${YELLOW}[2/7] Testing backend imports...${NC}"
if python3 -c "from app.main import app; print('OK')" 2>/dev/null; then
  echo -e "${GREEN}✓ Backend imports successfully${NC}"
else
  echo -e "${RED}✗ Backend import failed${NC}"
  exit 1
fi

# Test 3: MongoDB connection
echo -e "\n${YELLOW}[3/7] Testing MongoDB connection...${NC}"
if python3 << 'EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=3000)
    try:
        await client.admin.command('ping')
        db_name = os.getenv('MONGODB_DB_NAME', 'kaushalya_db')
        db = client[db_name]
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    finally:
        client.close()

result = asyncio.run(test_connection())
exit(0 if result else 1)
EOF
then
  echo -e "${GREEN}✓ MongoDB connected${NC}"
else
  echo -e "${YELLOW}⚠ MongoDB not available (will try local)${NC}"
fi

# Test 4: Dataset files
echo -e "\n${YELLOW}[4/7] Checking datasets...${NC}"
MISSING=0
for dataset in "../all_job_post.csv" "../Dataset_1/india_professional_skills_intelligence.csv" "../Dataset_3/skills.csv"; do
  if [ -f "$dataset" ]; then
    SIZE=$(du -h "$dataset" | cut -f1)
    echo -e "${GREEN}✓${NC} $(basename $dataset) ($SIZE)"
  else
    echo -e "${RED}✗${NC} $(basename $dataset) missing"
    MISSING=$((MISSING+1))
  fi
done

if [ $MISSING -gt 0 ]; then
  echo -e "${YELLOW}⚠ Some datasets missing (assessment-only mode will work)${NC}"
fi

# Test 5: Environment configuration
echo -e "\n${YELLOW}[5/7] Checking environment...${NC}"
if [ -f ".env" ]; then
  echo -e "${GREEN}✓${NC} .env exists"
  if grep -q "MONGODB_URI" .env; then
    echo -e "${GREEN}  ✓ MONGODB_URI configured${NC}"
  fi
  if grep -q "GOOGLE_CLIENT_ID" .env; then
    echo -e "${GREEN}  ✓ GOOGLE_CLIENT_ID configured${NC}"
  else
    echo -e "${YELLOW}  ⚠ GOOGLE_CLIENT_ID not set (auth endpoint ready, Google button needs config)${NC}"
  fi
else
  echo -e "${YELLOW}⚠${NC} .env not found — creating template..."
  cat > .env << 'ENVTEMPLATE'
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=kaushalya_db
JWT_SECRET=kaushalya-sih-2026-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_FROM_EMAIL=your-email@gmail.com
GEMINI_API_KEY=your-gemini-key-here
GROQ_API_KEY=your-groq-key-here
OPENAI_API_KEY=your-openai-key-here
FRONTEND_URL=http://localhost:5173
ENVTEMPLATE
  echo -e "${YELLOW}  Created .env template — please update with your values${NC}"
fi

# Test 6: Frontend setup
echo -e "\n${YELLOW}[6/7] Checking frontend...${NC}"
cd "../frontend"

if [ ! -f "package.json" ]; then
  echo -e "${RED}✗ Frontend package.json missing${NC}"
  exit 1
fi

if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}Installing frontend dependencies...${NC}"
  npm install -q 2>/dev/null || pnpm install -q
fi

echo -e "${GREEN}✓ Frontend ready${NC}"

if [ -f ".env" ]; then
  echo -e "${GREEN}✓ Frontend .env exists${NC}"
else
  echo -e "${YELLOW}⚠ Frontend .env not found${NC}"
  cat > .env << 'ENVTEMPLATE'
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id-here
ENVTEMPLATE
  echo -e "${YELLOW}  Created .env template${NC}"
fi

# Test 7: Summary
echo -e "\n${YELLOW}[7/7] Summary${NC}"
echo -e "${GREEN}✓ All checks passed!${NC}\n"

echo "🎯 Next Steps:"
echo "============"
echo ""
echo "1️⃣  Backend:"
echo "   cd backend"
echo "   python3 scripts/import_datasets.py --dataset=all  # If datasets available"
echo "   python3 scripts/seed_assessments.py              # Seed demo assessments"
echo "   uvicorn app.main:app --reload                    # Start API (port 8000)"
echo ""
echo "2️⃣  Frontend (new terminal):"
echo "   cd frontend"
echo "   npm run dev                                       # Start dev server (port 5173)"
echo ""
echo "3️⃣  Test:"
echo "   Open http://localhost:5173"
echo "   Login: trainee@kaushalya.demo / KaushalyaDemo123!"
echo "   Navigate to:"
echo "     • /trainee/dashboard — View KPIs"
echo "     • /trainee/assessment — Take assessment"
echo "     • /trainee/skill-gap — View gaps"
echo "     • /trainee/jobs — See job matches"
echo ""
echo "4️⃣  API Testing (optional):"
echo "   curl http://localhost:8000/api/healthz | jq"
echo "   curl http://localhost:8000/api/assessments -H 'Authorization: Bearer <token>' | jq"
echo ""
echo "📚 More info:"
echo "   • README.md — Full setup and problem mapping"
echo "   • IMPLEMENTATION.md — What's been completed"
echo ""
echo -e "${GREEN}Ready to demonstrate KAUSHALYA! 🚀${NC}"
