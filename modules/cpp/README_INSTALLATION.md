# Connect++ (CPP) - Installation & Setup Guide

## 🚀 Quick Start with Docker

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- Ports available: 8080 (backend), 3000 (frontend), 5433 (postgres), 6380 (redis)

### 1. Clone and Navigate
```bash
cd modules/cpp
```

### 2. Create Environment File
```bash
cp .env.example .env
# Edit .env if needed
```

### 3. Start All Services
```bash
docker-compose up -d
```

### 4. Check Status
```bash
docker-compose ps
```

Expected output:
```
NAME                IMAGE              STATUS
cpp-backend         cpp-backend        Up (healthy)
cpp-frontend        cpp-frontend       Up
cpp-postgres        postgres:15        Up (healthy)
cpp-redis           redis:7            Up (healthy)
```

### 5. Access Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8080
- **API Docs:** http://localhost:8080/docs
- **Health Check:** http://localhost:8080/health

### 6. Default Login (Demo)
```
Username: operator
Password: demo
```
Or press Enter in the scanner field on login page.

---

## 🛠️ Development Setup (Without Docker)

### Backend Setup

1. **Create Virtual Environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup Database**
```bash
# Install PostgreSQL 15
# Create database
createdb cppdb

# Set environment
export DATABASE_URL="postgresql://user:pass@localhost:5432/cppdb"
```

4. **Run Backend**
```bash
uvicorn app.main:socket_app --host 0.0.0.0 --port 8080 --reload
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Run Development Server**
```bash
npm run dev
```

3. **Build for Production**
```bash
npm run build
```

---

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

---

## 📊 Database Migrations

### Create Migration
```bash
cd backend
alembic revision --autogenerate -m "description"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8080
# Kill the process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check postgres is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Frontend Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Backend Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 🐳 Docker Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes (Clean Slate)
```bash
docker-compose down -v
```

### Rebuild Images
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Execute Commands in Container
```bash
# Backend shell
docker-compose exec backend bash

# Database shell
docker-compose exec postgres psql -U cppuser -d cppdb
```

---

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://cppuser:cpppass@postgres:5432/cppdb
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8080/api/v1
VITE_SOCKET_URL=http://localhost:8080
```

---

## 🔒 Security Notes

⚠️ **IMPORTANT for Production:**

1. Change `JWT_SECRET` to a strong random key
2. Use environment-specific `.env` files
3. Enable HTTPS/SSL
4. Restrict CORS origins
5. Use strong database passwords
6. Enable database SSL connections
7. Implement rate limiting
8. Enable firewall rules

---

## 📚 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

### Key Endpoints

**System**
- `POST /api/v1/tests/system/start` - Start system
- `POST /api/v1/tests/system/diagnostic` - Run diagnostic

**Tests**
- `POST /api/v1/tests/initialize` - Initialize test
- `GET /api/v1/tests/{id}` - Get test session
- `POST /api/v1/tests/{id}/step/{step_id}` - Submit step
- `POST /api/v1/tests/{id}/complete` - Complete test
- `GET /api/v1/tests/{id}/report` - Get report

**WebSocket**
- `WS /api/v1/tests/ws/{test_id}` - Real-time updates

---

## 🎯 Features Implemented

✅ **Backend (FastAPI)**
- RESTful API with 15+ endpoints
- WebSocket for real-time sensor data
- JWT authentication
- PostgreSQL database with SQLAlchemy
- Redis caching
- Docker containerization

✅ **Frontend (React + TypeScript)**
- Modern React 18 with hooks
- TypeScript for type safety
- Tailwind CSS for styling
- React Query for data fetching
- Zustand for state management
- Socket.IO client for real-time
- Responsive design (PC & Device)

✅ **Features**
- User authentication (QR/Keyboard)
- Test menu (4-level selection)
- Test execution (7-step workflow)
- Real-time sensor monitoring
- Workshop management
- Test reports & statistics
- Dashboard with metrics

---

## 📱 Device Support

### PC Version (1920x1080+)
- Full keyboard & mouse support
- Multi-window capability
- Advanced visualizations

### ConnectDisplay (800x480)
- Touch-optimized interface
- Virtual keyboard
- Simplified navigation
- Offline mode support

---

## 🤝 Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review this documentation
3. Check API docs: http://localhost:8080/docs
4. Contact development team

---

## 📄 License

Proprietary - All rights reserved

---

**Status:** ✅ Fully Functional Development Environment
**Version:** 1.0.0
**Last Updated:** 2025-10-03
