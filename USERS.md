# 👥 Użytkownicy i System Ról - Fleet Management System

## 📋 Spis treści
- [Użytkownicy domyślni](#użytkownicy-domyślni)
- [System ról](#system-ról)
- [Przełączanie ról](#przełączanie-ról)
- [Konfiguracja użytkowników](#konfiguracja-użytkowników)

---

## 🔐 Użytkownicy domyślni

System jest dostarczany z zestawem predefiniowanych użytkowników testowych. **Hasło dla wszystkich użytkowników testowych to: `pass`**

| Username | Password | Domyślna Rola | Email | Opis |
|----------|----------|---------------|-------|------|
| **maker1** | `pass` | maker | maker1@fleetmanagement.com | **Super użytkownik** z dostępem do wszystkich 6 ról |
| **admin** | `pass` | superuser | admin@fleetmanagement.com | Administrator systemu - zarządza scenariuszami testowymi |
| **operator1** | `pass` | operator | operator1@fleetmanagement.com | Operator - obsługa testów urządzeń |
| **manager1** | `pass` | manager | manager1@fleetmanagement.com | Manager - zarządzanie danymi floty |
| **configurator** | `pass` | configurator | configurator@fleetmanagement.com | Konfigurator - konfiguracja systemu |

### ⚠️ Bezpieczeństwo

**WAŻNE:** Domyślne hasła są przeznaczone **TYLKO DO CELÓW DEWELOPERSKICH I TESTOWYCH**!

W środowisku produkcyjnym:
- Natychmiast zmień wszystkie domyślne hasła
- Usuń lub dezaktywuj nieużywane konta testowe
- Implementuj politykę silnych haseł
- Rozważ dodanie dwuskładnikowej autoryzacji (2FA)

---

## 🎭 System Ról

System Fleet Management używa zaawansowanego systemu ról z możliwością przypisania **wielu ról do jednego użytkownika**. Każda rola daje dostęp do określonych modułów i funkcji.

### Dostępne role:

#### 1. **Operator** (`operator`)
- **Moduł:** Connect++
- **Funkcje:**
  - Obsługa testów urządzeń
  - Testowanie API endpoints
  - Wykonywanie podstawowych operacji testowych

#### 2. **Superuser** (`superuser`)
- **Moduł:** Connect Manager
- **Funkcje:**
  - Tworzenie i zarządzanie scenariuszami testowymi
  - Konfiguracja przepływów testowych (test_flow)
  - Zarządzanie szablonami JSON
  - Definiowanie kroków testowych

#### 3. **Manager** (`manager`)
- **Moduł:** Fleet Data Manager
- **Funkcje:**
  - Zarządzanie urządzeniami (CRUD)
  - Zarządzanie klientami (CRUD)
  - Przypisywanie urządzeń do klientów
  - Przeglądanie dashboardu floty
  - Filtrowanie i wyszukiwanie urządzeń

#### 4. **Configurator** (`configurator`)
- **Moduł:** Fleet Config Manager
- **Funkcje:**
  - Konfiguracja systemu (system configs)
  - Konfiguracja urządzeń (device configs)
  - Zarządzanie scenariuszami testowymi
  - Backup i restore konfiguracji
  - Zarządzanie szablonami JSON

#### 5. **Maker** (`maker`)
- **Moduł:** Fleet Software Manager
- **Funkcje:**
  - Zarządzanie oprogramowaniem (CRUD)
  - Zarządzanie wersjami oprogramowania
  - Instalacja i aktualizacja oprogramowania
  - Monitorowanie instalacji
  - Dashboard statystyk oprogramowania

#### 6. **Admin** (`admin`)
- **Moduł:** (dostęp administracyjny)
- **Funkcje:**
  - Zarządzanie użytkownikami
  - Pełny dostęp do API
  - Zarządzanie systemem logów
  - Konfiguracja zaawansowana

---

## 🔄 Przełączanie Ról

### Multi-Role System

Użytkownik **maker1** ma **specjalne uprawnienia** - posiada wszystkie 6 ról i może przełączać się między nimi **bez ponownego logowania**.

### Jak przełączać role:

1. **Zaloguj się jako maker1**
   ```
   Username: maker1
   Password: pass
   ```

2. **Sidebar - Przełącznik Ról**
   - Po zalogowaniu, w sidebarze (lewy panel) pojawi się sekcja **"🔄 Przełącz rolę:"**
   - Dropdown pokazuje wszystkie dostępne role użytkownika

3. **Wybierz nową rolę**
   - Kliknij dropdown i wybierz rolę (np. `Manager`, `Operator`, `Configurator`)
   - System automatycznie:
     - Przełączy aktywną rolę
     - Zaktualizuje JWT token
     - Odświeży dane modułu
     - Wyświetli komunikat: *"✅ Przełączono na rolę: [NAZWA_ROLI]"*

4. **Korzystaj z modułu**
   - Przejdź do odpowiedniego modułu przez górne menu nawigacji
   - Wszystkie API calls będą wykonywane z nową aktywną rolą

### Przykładowy flow:

```
1. Zaloguj: maker1 / pass
   → Aktywna rola: maker

2. Przełącz na: manager
   → Aktywna rola: manager
   → Dostęp do: Fleet Data Manager

3. Przełącz na: superuser
   → Aktywna rola: superuser
   → Dostęp do: Connect Manager

4. Przełącz na: operator
   → Aktywna rola: operator
   → Dostęp do: Connect++
```

### API Endpoint dla przełączania ról:

```http
POST /api/v1/auth/switch-role
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "new_role": "manager"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "username": "maker1",
    "role": "manager",
    "roles": ["maker", "operator", "admin", "superuser", "manager", "configurator"],
    "active_role": "manager"
  }
}
```

---

## ⚙️ Konfiguracja Użytkowników

### Dodawanie nowego użytkownika

#### 1. Przez API:

```http
POST /api/v1/users
Authorization: Bearer <ADMIN_JWT_TOKEN>
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "role": "operator",
  "roles": ["operator"],
  "is_active": true
}
```

#### 2. Przez bazę danych (psql):

```sql
-- Podłącz się do bazy danych
psql $DATABASE_URL

-- Dodaj użytkownika
INSERT INTO users (username, email, password_hash, role, roles, qr_code, is_active)
VALUES (
  'newuser',
  'newuser@example.com',
  '<HASHED_PASSWORD>',  -- użyj funkcji hashującej (bcrypt)
  'operator',
  '["operator"]'::json,
  'QR_CODE_STRING',
  true
);
```

### Przypisywanie wielu ról użytkownikowi

Aby użytkownik mógł przełączać role jak maker1, zaktualizuj pole `roles`:

```sql
UPDATE users 
SET roles = '["maker", "operator", "admin", "superuser", "manager", "configurator"]'::json
WHERE username = 'username';
```

### Zmiana hasła użytkownika

```python
from backend.auth.auth import get_password_hash

# W Python shell lub skrypcie:
new_password_hash = get_password_hash("NewSecurePassword123!")

# Następnie w SQL:
UPDATE users 
SET password_hash = '<new_password_hash>'
WHERE username = 'username';
```

---

## 🔐 JWT Token Structure

System używa JWT (JSON Web Tokens) do autoryzacji. Token zawiera:

```json
{
  "sub": "maker1",
  "username": "maker1",
  "role": "manager",
  "active_role": "manager",
  "roles": ["maker", "operator", "admin", "superuser", "manager", "configurator"],
  "exp": 1735589732
}
```

**Pola:**
- `sub` / `username` - identyfikator użytkownika
- `role` - domyślna rola użytkownika (backward compatibility)
- `active_role` - aktualnie aktywna rola
- `roles` - lista wszystkich dostępnych ról użytkownika
- `exp` - data wygaśnięcia tokenu (timestamp)

---

## 📚 Dodatkowe zasoby

- [README.md](README.md) - Instrukcja uruchomienia projektu
- [API Documentation](http://localhost:5000/docs) - Swagger UI z pełną dokumentacją API
- [CHANGELOG.md](CHANGELOG.md) - Historia zmian w projekcie
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architektura systemu

---

## 🆘 Pomoc i wsparcie

**Problem z logowaniem?**
- Sprawdź czy używasz poprawnego hasła: `pass` dla wszystkich użytkowników testowych
- Sprawdź czy serwer działa: `http://localhost:5000`
- Sprawdź logi serwera: `docker-compose logs -f api`

**Problem z przełączaniem ról?**
- Upewnij się że użytkownik ma wiele ról przypisanych w polu `roles`
- Sprawdź czy dropdown "Przełącz rolę" jest widoczny w sidebarze (pojawia się tylko dla użytkowników z >1 rolą)
- Sprawdź response z `/api/v1/auth/switch-role` endpoint

**Potrzebujesz pomocy?**
- Otwórz issue na GitHub
- Skontaktuj się z zespołem deweloperskim
- Sprawdź dokumentację API: `http://localhost:5000/docs`
