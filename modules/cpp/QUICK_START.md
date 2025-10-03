# 🚀 Connect++ (CPP) - Quick Start Guide

## ⚠️ WAŻNE: Katalog Roboczy

**Wszystkie komendy muszą być uruchamiane z katalogu modułu CPP:**

```bash
cd /home/tom/github/zlecenia/c2002/modules/cpp
```

❌ **NIE uruchamiaj z głównego katalogu** `/home/tom/github/zlecenia/c2002`  
✅ **Zawsze z** `/home/tom/github/zlecenia/c2002/modules/cpp`

---

## 🐳 Docker Commands

### Start All Services
```bash
cd modules/cpp
docker-compose up -d
```

### Check Status
```bash
cd modules/cpp
docker-compose ps
```

Expected output:
```
NAME           STATUS
cpp-backend    Up (healthy)
cpp-frontend   Up
cpp-postgres   Up (healthy)
cpp-redis      Up (healthy)
```

### View Logs
```bash
cd modules/cpp
docker-compose logs -f
```

### Stop Services
```bash
cd modules/cpp
docker-compose down
```

### Restart Services
```bash
cd modules/cpp
docker-compose restart
```

---

## 🧪 Testing

### Run All Tests
```bash
cd modules/cpp
make test
```

### Test Endpoints
```bash
cd modules/cpp
./test-endpoints.sh
```

### Manual Test
```bash
curl http://localhost:8080/health | jq .
```

---

## 🌐 Access Points

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8080
- **API Docs:** http://localhost:8080/docs
- **Health Check:** http://localhost:8080/health

---

## 📊 Quick Health Check

```bash
# From modules/cpp directory
cd modules/cpp

# Check services
docker-compose ps

# Test API
curl http://localhost:8080/health

# Run tests
make test
```

---

## 🔧 Troubleshooting

### "No containers found"
➜ **Solution:** You're in wrong directory! Go to `modules/cpp`

### "Connection refused"
➜ **Solution:** Start services: `docker-compose up -d`

### "make test failed"
➜ **Solution:** Make sure you're in `modules/cpp` directory

---

## 📚 Full Documentation

- `README.md` - Full specification (80+ pages)
- `README_INSTALLATION.md` - Installation guide
- `TESTING_REPORT.md` - Test results
- `CHANGELOG.md` - Version history
- `FINAL_SUMMARY.md` - Project summary

---

## ✅ Verification Checklist

```bash
cd modules/cpp

# 1. Check Docker services
docker-compose ps
# All 4 services should be "Up"

# 2. Test API
curl http://localhost:8080/health
# Should return: {"status": "healthy", ...}

# 3. Run tests
make test
# Should show: 11 passed

# 4. Open frontend
open http://localhost:3000
# Should show login page
```

---

**Remember: Always run commands from `/modules/cpp` directory!** 🎯
