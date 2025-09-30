# 🗄️ Database Initialization

## 📁 Struktura katalogów

```
db/
├── init-scripts/
│   ├── 01-create-tables.sql    # Tworzenie tabel i indeksów  
│   └── 02-initial-data.sql     # Dane inicjalizacyjne
└── README.md                   # Ta dokumentacja
```

## 🚀 Automatyczna inicjalizacja

Pliki SQL w katalogu `init-scripts/` są **automatycznie wykonywane** przez PostgreSQL podczas pierwszego uruchomienia kontenera Docker.

### Kolejność wykonania:
1. **01-create-tables.sql** - Tworzy wszystkie tabele, indeksy i triggery
2. **02-initial-data.sql** - Wstawia dane inicjalizacyjne (użytkowników, urządzenia, konfiguracje)

## 👥 Domyślni użytkownicy

| Username | Email | Role | Roles Array | Password | Status |
|----------|-------|------|-------------|----------|---------|
| `maker1` | maker1@fleet.com | superuser | `["maker", "operator", "admin", "superuser", "manager", "configurator"]` | `password123` | ✅ Active |
| `admin1` | admin1@fleet.com | admin | `["admin", "configurator"]` | `password123` | ✅ Active |
| `manager1` | manager1@fleet.com | manager | `["manager", "operator"]` | `password123` | ✅ Active |
| `operator1` | operator1@fleet.com | operator | `["operator"]` | `password123` | ✅ Active |
| `operator2` | operator2@fleet.com | operator | `["operator"]` | `password123` | ✅ Active |
| `configurator1` | config1@fleet.com | configurator | `["configurator", "operator"]` | `password123` | ✅ Active |
| `testuser` | test@fleet.com | operator | `["operator"]` | `password123` | ❌ Inactive |

## 🏢 Domyślni klienci

- **ACME Manufacturing** - Główny klient z Warszawy
- **TechCorp Solutions** - Klient korporacyjny z Krakowa  
- **MedDevice Inc** - Producent sprzętu medycznego z USA

## 🖥️ Domyślne urządzenia

- **MT-001** - Mask Tester (ACME Manufacturing)
- **PS-002** - Pressure Sensor (ACME Manufacturing)
- **FM-003** - Flow Meter (TechCorp Solutions)
- **TS-004** - Temperature Sensor (TechCorp Solutions) - w konserwacji
- **HS-005** - Humidity Sensor (MedDevice Inc)

## ⚙️ Inicjalizacja przy pierwszym uruchomieniu

```bash
# Uruchom Docker Compose
docker-compose up -d

# Sprawdź logi inicjalizacji bazy danych
docker-compose logs db

# Sprawdź czy tabele zostały utworzone
docker-compose exec db psql -U fleetuser -d fleet_management -c "\dt"

# Sprawdź użytkowników
docker-compose exec db psql -U fleetuser -d fleet_management -c "SELECT username, role, is_active FROM users;"
```

## 🔄 Re-inicjalizacja bazy danych

Aby przywrócić bazę do stanu początkowego:

```bash
# Zatrzymaj kontenery
docker-compose down

# Usuń volume z danymi PostgreSQL
docker volume rm c2002_postgres_data

# Uruchom ponownie (automatycznie wykona init scripts)
docker-compose up -d
```

## 📊 Co zostanie utworzone

### Tabele (14):
- `users` - Konta użytkowników z wielorolowym dostępem
- `customers` - Informacje o klientach z JSON contact_info
- `devices` - Inwentarz urządzeń ze statusem
- `software` - Katalog oprogramowania
- `software_versions` - Historia wersji oprogramowania  
- `device_software` - Mapowanie urządzenie-oprogramowanie
- `software_installations` - Historia instalacji oprogramowania
- `configurations` - Ustawienia systemowe i urządzeń
- `json_templates` - Szablony konfiguracji JSON
- `test_scenarios` - Scenariusze testowe z JSON test_flow
- `test_steps` - Kroki testowe (legacy)
- `test_reports` - Raporty wykonania testów
- `system_logs` - Logi systemowe i audyt
- `translations` - Tłumaczenia wielojęzyczne

### Dane inicjalizacyjne:
- **7 użytkowników** z różnymi rolami i uprawnieniami
- **3 klientów** z pełnymi informacjami kontaktowymi
- **5 urządzeń** różnych typów z konfiguracjami JSON
- **4 pakiety oprogramowania** z wersjami
- **6 konfiguracji systemowych** dla komponentów FMS
- **2 szablony JSON** do konfiguracji
- **2 scenariusze testowe** z przepływami JSON
- **10 tłumaczeń** (angielski/polski)

## 🔐 Bezpieczeństwo

⚠️ **WAŻNE**: Domyślne hasło `password123` jest używane tylko do celów rozwoju. 

**W środowisku produkcyjnym:**
1. Zmień wszystkie hasła użytkowników
2. Użyj mocnych haseł z bcrypt hash
3. Skonfiguruj właściwe zmienne środowiskowe
4. Usuń nieaktywne konta testowe

## 🧪 Testowanie inicjalizacji

```bash
# Sprawdź czy wszystkie tabele zostały utworzone
docker-compose exec db psql -U fleetuser -d fleet_management -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;"

# Sprawdź liczbę rekordów w każdej tabeli
docker-compose exec db psql -U fleetuser -d fleet_management -c "
SELECT 
  schemaname,
  tablename,
  n_tup_ins as inserted_rows
FROM pg_stat_user_tables 
ORDER BY tablename;"

# Test logowania dla maker1
docker-compose exec db psql -U fleetuser -d fleet_management -c "
SELECT username, role, roles, is_active 
FROM users 
WHERE username = 'maker1';"
```

---

**Utworzono:** 30 września 2025  
**Wersja:** 1.0.0  
**Kompatybilność:** PostgreSQL 15+, Docker Compose 2.0+
