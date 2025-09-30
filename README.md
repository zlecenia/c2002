# 🚀 Fleet Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Comprehensive Fleet Management System for testing device masks and fleet operations**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [API](#-api) • [Docker](#-docker-setup)

</div>

---

## 📋 Spis treści

- [Opis projektu](#-opis-projektu)
- [Features](#-features)
- [Wymagania](#-wymagania)
- [Quick Start](#-quick-start)
- [Docker Setup](#-docker-setup)
- [Konfiguracja](#-konfiguracja)
- [Użytkownicy i role](#-użytkownicy-i-role)
- [Moduły systemu](#-moduły-systemu)
- [API Documentation](#-api-documentation)
- [Struktura projektu](#-struktura-projektu)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Opis projektu

Fleet Management System to zaawansowana aplikacja webowa do zarządzania flotą urządzeń testujących, zbudowana w oparciu o polską specyfikację techniczną. System oferuje kompleksowe rozwiązanie dla przedsiębiorstw zajmujących się testowaniem masek i innych urządzeń medycznych.

**Główne zalety:**
- ✅ 5 wyspecjalizowanych modułów webGUI
- ✅ REST API z 50+ endpoints
- ✅ Multi-role authentication system z JWT
- ✅ Wizualne edytory JSON
- ✅ Responsywny design (desktop + mobile)
- ✅ PostgreSQL database
- ✅ Real-time dashboard z statystykami

---

## ✨ Features

### 🔐 Authentication & Authorization
- JWT token-based authentication
- QR code login support
- Multi-role system (6 ról)
- Role switching bez re-login
- Sidebar-based login interface

### 📊 Fleet Data Management
- Zarządzanie urządzeniami (CRUD)
- Zarządzanie klientami (CRUD)
- Przypisywanie urządzeń do klientów
- Filtrowanie i wyszukiwanie
- **Wizualny edytor JSON dla contact_info**

### ⚙️ Configuration Management
- System configuration (CRUD)
- Device configuration (CRUD)
- JSON templates management
- Backup & restore functionality
- Visual JSON tree editors

### 💾 Software Management
- Software packages (CRUD)
- Version management
- Installation tracking
- Dashboard with statistics

### 🧪 Test Scenarios
- Scenario creation with visual JSON editor
- Test flow configuration
- Device type filtering
- Template-based scenarios

### 🎨 User Interface
- 15% sidebar + 85% content layout
- Responsive design (@media queries)
- Color-coded modules
- Global navigation menu
- Real-time updates

---

## 📦 Wymagania

### System Requirements

- **Python:** 3.11 lub nowszy
- **PostgreSQL:** 15 lub nowszy
- **RAM:** minimum 2GB
- **Disk Space:** minimum 500MB

### Alternatywnie: Docker

- **Docker:** 20.10 lub nowszy
- **Docker Compose:** 2.0 lub nowszy

---

## 🚀 Quick Start

### Metoda 1: Lokalna instalacja (bez Docker)

#### 1. Klonowanie repozytorium

```bash
git clone https://github.com/your-org/fleet-management.git
cd fleet-management
```

#### 2. Instalacja zależności

```bash
pip install -r requirements.txt
```

#### 3. Konfiguracja bazy danych

Ustaw zmienną środowiskową `DATABASE_URL`:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/fleet_management"
```

Lub utwórz plik `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/fleet_management
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### 4. Inicjalizacja bazy danych

Baza danych zostanie automatycznie utworzona przy pierwszym uruchomieniu. Aby dodać przykładowe dane:

```bash
curl -X POST http://localhost:5000/api/v1/init-data
```

#### 5. Uruchomienie serwera

```bash
python main.py
```

Serwer uruchomi się na: **http://localhost:5000**

---

## 🐳 Docker Setup

### Szybkie uruchomienie z Docker Compose

#### 1. Build i uruchomienie

```bash
docker-compose up -d
```

#### 2. Sprawdź status

```bash
docker-compose ps
```

#### 3. Zobacz logi

```bash
docker-compose logs -f
```

#### 4. Zatrzymanie

```bash
docker-compose down
```

### Struktura Docker

```yaml
services:
  - api: Fleet Management API (Python FastAPI)
  - db: PostgreSQL 15
```

**Porty:**
- API: `5000:5000`
- PostgreSQL: `5432:5432`

**Volumes:**
- `postgres_data`: Persystentna baza danych

---

## ⚙️ Konfiguracja

### Zmienne środowiskowe

| Zmienna | Opis | Wartość domyślna | Wymagana |
|---------|------|------------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ Tak |
| `JWT_SECRET_KEY` | Secret key dla JWT tokenów | - | ✅ Tak |
| `JWT_ALGORITHM` | Algorytm JWT | `HS256` | ❌ Nie |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Czas wygaśnięcia tokenu (minuty) | `30` | ❌ Nie |

### Konfiguracja produkcyjna

Dla środowiska produkcyjnego:

1. **Zmień domyślne hasła** (patrz [USERS.md](USERS.md))
2. **Ustaw silny JWT_SECRET_KEY**:
   ```bash
   openssl rand -hex 32
   ```
3. **Konfiguruj HTTPS** (reverse proxy: nginx/caddy)
4. **Enable CORS** odpowiednio dla domeny
5. **Backup bazy danych** regularnie

---

## 👥 Użytkownicy i role

System posiada 6 ról z różnymi uprawnieniami:

| Rola | Username | Password | Moduł | Opis |
|------|----------|----------|-------|------|
| **Multi-role** | maker1 | pass | Wszystkie | Wszystkie 6 ról |
| Operator | operator1 | pass | Connect++ | Testy urządzeń |
| Superuser | admin | pass | Connect Manager | Scenariusze testowe |
| Manager | manager1 | pass | Fleet Data Manager | Dane floty |
| Configurator | configurator | pass | Fleet Config Manager | Konfiguracja |
| Maker | maker1 | pass | Fleet Software Manager | Oprogramowanie |

**📖 Więcej informacji:** [USERS.md](USERS.md)

### Przełączanie ról (maker1)

Użytkownik **maker1** może przełączać się między wszystkimi rolami bez ponownego logowania:

1. Zaloguj się jako `maker1` / `pass`
2. W sidebarze pojawi się dropdown **"🔄 Przełącz rolę"**
3. Wybierz rolę z listy
4. System automatycznie przełączy rolę i zaktualizuje token

---

## 📱 Moduły systemu

### 1. 🔗 Connect++ (Operator)
**URL:** `http://localhost:5000/connect-plus`

- Testowanie API endpoints
- Wykonywanie testów urządzeń
- Prosty interfejs operatora

### 2. ⚙️ Connect Manager (Superuser)
**URL:** `http://localhost:5000/connect-manager`

- Tworzenie scenariuszy testowych
- **Wizualny edytor JSON** dla test_flow
- Zarządzanie krokami testowymi
- Szablon-based scenarios

### 3. 📊 Fleet Data Manager (Manager)
**URL:** `http://localhost:5000/fleet-data-manager`

- Zarządzanie urządzeniami (CRUD)
- Zarządzanie klientami (CRUD)
- **Wizualny edytor JSON dla contact_info**
- Dashboard z statystykami
- Filtrowanie urządzeń

### 4. 🔧 Fleet Config Manager (Configurator)
**URL:** `http://localhost:5000/fleet-config-manager`

- Konfiguracja systemu
- Konfiguracja urządzeń
- Zarządzanie szablonami JSON
- Backup/Restore
- **Wizualne edytory JSON** (3 miejsca)

### 5. 💿 Fleet Software Manager (Maker)
**URL:** `http://localhost:5000/fleet-software-manager`

- Zarządzanie oprogramowaniem (CREATE funkcjonalny)
- Wersjonowanie (READ funkcjonalny)
- Instalacje (READ funkcjonalny)
- Dashboard statystyk (READ funkcjonalny)

**⚠️ Known Limitations:**
- `viewSoftware(id)` function not yet implemented - Cannot view software details
- `deleteSoftware(id)` function not yet implemented - Cannot delete software packages
- See [TODO.md](TODO.md) for planned improvements

---

## 📚 API Documentation

### Swagger UI

Pełna interaktywna dokumentacja API dostępna pod:

**http://localhost:5000/docs**

### Główne grupy endpoints:

#### 🔐 Authentication
- `POST /api/v1/auth/login` - Login (username/password)
- `POST /api/v1/auth/login/qr` - QR code login
- `POST /api/v1/auth/switch-role` - Przełączanie ról
- `GET /api/v1/auth/me` - Current user info

#### 📊 Fleet Data (Manager)
- `GET /api/v1/fleet-data/devices` - Lista urządzeń
- `POST /api/v1/fleet-data/devices` - Dodaj urządzenie
- `GET /api/v1/fleet-data/customers` - Lista klientów
- `POST /api/v1/fleet-data/customers` - Dodaj klienta
- `GET /api/v1/fleet-data/dashboard` - Dashboard stats

#### 🔧 Fleet Config (Configurator)
- `GET /api/v1/fleet-config/system-configs` - System configs
- `GET /api/v1/fleet-config/device-configs` - Device configs
- `GET /api/v1/fleet-config/json-templates` - JSON templates
- `POST /api/v1/fleet-config/backup` - Backup konfiguracji
- `POST /api/v1/fleet-config/restore` - Restore konfiguracji

#### 💾 Fleet Software (Maker)
- `GET /api/v1/fleet-software/software` - Lista oprogramowania
- `GET /api/v1/fleet-software/software/{id}/versions` - Wersje
- `GET /api/v1/fleet-software/installations` - Instalacje
- `GET /api/v1/fleet-software/dashboard/stats` - Statystyki

#### ⚙️ Test Scenarios (Superuser)
- `GET /api/v1/scenarios/` - Lista scenariuszy
- `POST /api/v1/scenarios/` - Utwórz scenariusz
- `PUT /api/v1/scenarios/{id}` - Aktualizuj scenariusz
- `DELETE /api/v1/scenarios/{id}` - Usuń scenariusz

---

## 📁 Struktura projektu

```
fleet-management/
├── backend/
│   ├── api/              # API routers
│   │   ├── auth_router.py
│   │   ├── fleet_config_router.py
│   │   ├── fleet_data_router.py
│   │   └── fleet_software_router.py
│   ├── auth/             # Authentication logic
│   │   └── auth.py
│   ├── core/             # Configuration
│   │   └── config.py
│   ├── db/               # Database connection
│   │   └── database.py
│   └── models/           # SQLAlchemy models
│       └── models.py
├── docs/                 # Dokumentacja projektu
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DATABASE.md
├── main.py               # FastAPI application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image
├── docker-compose.yml    # Docker services
├── .env.example          # Environment template
├── README.md             # Ten plik
├── USERS.md              # Dokumentacja użytkowników
├── CHANGELOG.md          # Historia zmian
└── TODO.md               # Lista zadań
```

---

## 🚀 Deployment

### Replit Autoscale

Projekt jest skonfigurowany dla Replit Autoscale deployment:

```bash
# Deploy button dostępny w interfejsie Replit
```

**Konfiguracja:**
- Deployment target: `autoscale`
- Run command: `python main.py`
- Port: `5000`

### Deployment produkcyjny

#### 1. Build Docker image

```bash
docker build -t fleet-management:latest .
```

#### 2. Push do registry

```bash
docker tag fleet-management:latest registry.example.com/fleet-management:latest
docker push registry.example.com/fleet-management:latest
```

#### 3. Deploy z docker-compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔧 Troubleshooting

### Problem: Serwer nie startuje

**Rozwiązanie:**
```bash
# Sprawdź czy port 5000 jest wolny
lsof -i :5000

# Zatrzymaj proces na porcie 5000
kill -9 $(lsof -t -i:5000)

# Uruchom ponownie
python main.py
```

### Problem: Błąd połączenia z bazą danych

**Rozwiązanie:**
```bash
# Sprawdź czy PostgreSQL działa
pg_isready -h localhost -p 5432

# Sprawdź DATABASE_URL
echo $DATABASE_URL

# Test połączenia
psql $DATABASE_URL
```

### Problem: JWT token wygasł

**Rozwiązanie:**
1. Wyloguj się (przycisk "Wyloguj" w sidebarze)
2. Zaloguj ponownie z aktualnymi danymi
3. Token zostanie odnowiony

### Problem: Nie widzę przełącznika ról

**Rozwiązanie:**
- Przełącznik ról pojawia się **tylko** dla użytkowników z wieloma rolami
- Zaloguj się jako **maker1** aby zobaczyć przełącznik
- Sprawdź czy użytkownik ma przypisane wiele ról w bazie:
  ```sql
  SELECT username, roles FROM users WHERE username = 'maker1';
  ```

### Problem: Docker compose nie działa

**Rozwiązanie:**
```bash
# Zatrzymaj wszystkie kontenery
docker-compose down

# Usuń volumes
docker-compose down -v

# Rebuild i uruchom
docker-compose up --build -d
```

---

## 📄 Licencja

MIT License - see [LICENSE](LICENSE) file for details

---

## 🤝 Contribution

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/your-org/fleet-management/issues)
- **Dokumentacja API:** http://localhost:5000/docs
- **Dokumentacja użytkowników:** [USERS.md](USERS.md)
- **Architektura systemu:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

<div align="center">

**Made with ❤️ for Fleet Management**

[⬆ Back to top](#-fleet-management-system)

</div>
