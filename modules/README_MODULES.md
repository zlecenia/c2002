# 📦 Modules Overview

## Available Modules

### ✅ Connect++ (CPP) - v1.0.0
**Status:** Fully Functional & Tested  
**Location:** `modules/cpp/`  
**Description:** Operator testing module for device quality control

#### Quick Access
```bash
cd modules/cpp

# Start services
docker-compose up -d

# Run tests
make test

# View docs
cat README.md
```

#### Features
- ✅ FastAPI Backend (15+ endpoints)
- ✅ React Frontend (6 pages)
- ✅ PostgreSQL + Redis
- ✅ Docker deployment
- ✅ 24/24 tests passing
- ✅ Complete documentation

#### Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- API Docs: http://localhost:8080/docs

#### Documentation
See `modules/cpp/` for complete documentation:
- `README.md` - Full specification
- `QUICK_START.md` - Quick start guide
- `TESTING_REPORT.md` - Test results
- `CHANGELOG.md` - Version history

---

### 🔧 Other Modules

#### Fleet Data Manager (FDM)
**Location:** `modules/fdm/`  
**Status:** Active

#### Fleet Config Manager (FCM)
**Location:** `modules/fcm/`  
**Status:** Active

#### Connect Manager (CM)
**Location:** `modules/cm/`  
**Status:** Active

#### Fleet Software Manager (FSM)
**Location:** `modules/fsm/`  
**Status:** Active

---

## 📚 Module-Specific Commands

### Connect++ (CPP)
```bash
cd modules/cpp
docker-compose up -d    # Start
make test              # Test
docker-compose down    # Stop
```

### Other Modules
See respective module README files for specific instructions.

---

## ⚠️ Important Notes

1. **Always navigate to module directory first**
   ```bash
   cd modules/cpp  # or fdm, fcm, cm, fsm
   ```

2. **Each module has its own docker-compose**
   - Don't run from root directory
   - Each module is independent

3. **Port Allocation**
   - CPP: 8080 (backend), 3000 (frontend)
   - Other modules may use different ports

---

**Last Updated:** 2025-10-03
