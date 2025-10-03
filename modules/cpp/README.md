# CONNECT++ (CPP) - Port 8080
## Specyfikacja Modułu Operatorskiego dla Obsługi Testów

---

## 1. PRZEGLĄD MODUŁU

### 1.1 Informacje Podstawowe
- **Nazwa:** Connect++ (CPP)
- **Port:** 8080
- **Domena:** https://cpp.yourdomain.com lub http://192.168.1.100:8080
- **Główni użytkownicy:** Operatorzy warsztatów testowych
- **Cel:** Kompleksowa obsługa testów urządzeń ochrony osobistej

### 1.2 Tryby Pracy
System działa w trzech głównych trybach:

```
DEVICE MODE → USER MODE → TEST MODE
     ↓            ↓            ↓
 Re(start)   Tryb operatora   Wybór urządzenia
 Diagnostyka  Zdalny dostęp   Typ urządzenia
 Praca                        Pneumatyka
```

---

## 2. ARCHITEKTURA INTERFEJSU

### 2.1 Layout Uniwersalny (PC & Device)

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER BAR                                                   │
│ CONNECT 500         MASKTRONIC        Status: ● ONLINE      │
└─────────────────────────────────────────────────────────────┘
┌──────────────┬───────────────────────────┬─────────────────┐
│              │                           │                 │
│    MENU      │      INTERACTION          │  DATA SENSORS   │
│   (Nawigacja)│      (Główny ekran)       │  (Real-time)    │
│              │                           │                 │
│              │                           │  PRESSURE       │
│              │                           │  Low: --- mbar  │
│              │                           │  Med: --- bar   │
│              │                           │  High: --- bar  │
│              │                           │                 │
│              │                           │                 │
│              │                           │  [Photo/QR]     │
│              │                           │                 │
│              │                           │                 │
└──────────────┴───────────────────────────┴─────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ STATUS BAR                                                   │
│ OPERATOR: r.arendt  |  12.12.2025 - 12:05:26  |             │
│ 192.168.1.10:8080   |  Device Status: Ready                 │
│ Info/Help/Warnings                                          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Proporcje Ekranu

**Wersja PC (1920x1080):**
- Menu: 20% (384px)
- Interaction: 55% (1056px)
- Data Sensors: 25% (480px)

**Wersja Device - ConnectDisplay (800x480):**
- Menu: 25% (200px)
- Interaction: 50% (400px)
- Data Sensors: 25% (200px)

---

## 3. FUNKCJE MODUŁU - SZCZEGÓŁOWA SPECYFIKACJA

### 3.1 System Initialization

#### 3.1.1 Start System (10s)
**Endpoint:** `POST /api/system/start`

**Request:**
```json
{
  "device_ip": "192.168.1.100",
  "autostart": true
}
```

**Response:**
```json
{
  "status": "starting",
  "progress": 0,
  "estimated_time": 10,
  "message": "System starting in Progress..."
}
```

**UI Proces:**
1. Wyświetl logo MASKTRONIC
2. Progress bar (0-100%)
3. Real-time komunikaty:
    - "Initializing hardware..."
    - "Calibrating sensors..."
    - "Loading configurations..."
    - "System ready!"

**Baza danych:**
```sql
INSERT INTO system_logs (log_level, action, details)
VALUES ('INFO', 'System started', '{"duration": 10.2, "status": "success"}');
```

---

#### 3.1.2 Autodiagnostic (6s)
**Endpoint:** `POST /api/system/diagnostic`

**Testy wykonywane:**
1. **Pressure Sensors Test** (2s)
    - Low pressure sensor: -20 do 0 mbar
    - Medium pressure sensor: 0 do 50 bar
    - High pressure sensor: 0 do 300 bar

2. **Pneumatic System Test** (2s)
    - Valve operation
    - Leak detection
    - Pressure stability

3. **Communication Test** (1s)
    - USB scanner connectivity
    - Network connection
    - Database connection

4. **Hardware Test** (1s)
    - Display
    - Buttons/Touch
    - LED indicators

**Response:**
```json
{
  "status": "completed",
  "duration": 6.2,
  "results": {
    "pressure_sensors": {
      "low": {"status": "ok", "value": 10},
      "medium": {"status": "ok", "value": 20},
      "high": {"status": "ok", "value": 30}
    },
    "pneumatic": {"status": "ok"},
    "communication": {"status": "ok"},
    "hardware": {"status": "ok"}
  },
  "issues": []
}
```

**UI Display:**
```
AUTODIAGNOSTIC [6s]

✓ Pressure Sensors    [████████████] 100%
✓ Pneumatic System    [████████████] 100%
✓ Communication       [████████████] 100%
✓ Hardware            [████████████] 100%

System calibration in Progress...
```

---

### 3.2 Authentication Module

#### 3.2.1 Login - Scanner (QR/Barcode)
**Endpoint:** `POST /api/auth/login/qr`

**UI Layout:**
```
┌─────────────────────────────────────────┐
│         LOGIN MENU                      │
│                                         │
│  User Login By QR-CODE / BARCODE       │
│                                         │
│         [Scanner Icon]                  │
│                                         │
│  Podłącz czytnik kodów do portu USB    │
│                                         │
│  Wskazówki:                            │
│  1. Test podłączenia skanera           │
│  2. Test wprowadzonych danych          │
│  3. Informacja zwrotna o znalezieniu   │
│                                         │
│  [Switch to Keyboard Login]            │
└─────────────────────────────────────────┘
```

**Request:**
```json
{
  "qr_code": "OP-RARENDT-2025-001",
  "device_id": 1
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "user": {
    "id": 15,
    "username": "r.arendt",
    "role": "operator",
    "full_name": "Robert Arendt",
    "photo_url": "/photos/rarendt.jpg"
  },
  "workshop": {
    "id": 3,
    "name": "Workshop Poznań",
    "location": "PL-POZ-01"
  }
}
```

**Error Handling:**
```json
{
  "error": "scanner_not_detected",
  "message": "Skaner nie został wykryty",
  "action": "CHECK_USB"
}

{
  "error": "code_invalid",
  "message": "Kod nie został poprawnie sczytany",
  "action": "RETRY_SCAN"
}

{
  "error": "user_not_found",
  "message": "Zeskanowany kod użytkownika nie został znaleziony",
  "action": "CONTACT_ADMIN"
}
```

---

#### 3.2.2 Login - Keyboard
**Endpoint:** `POST /api/auth/login`

**UI Layout:**
```
┌─────────────────────────────────────────┐
│         LOGIN MENU                      │
│                                         │
│  User Login By Keyboard                │
│                                         │
│  Username: [___________________]       │
│                                         │
│  Password: [___________________]       │
│                                         │
│  ┌───────────────────────────────┐    │
│  │  1  2  3  4  5  6  7  8  9  0 │    │
│  │  Q  W  E  R  T  Y  U  I  O  P │    │
│  │  A  S  D  F  G  H  J  K  L    │    │
│  │  Z  X  C  V  B  N  M  < > ?   │    │
│  │      [Space]    [←]   [Enter] │    │
│  └───────────────────────────────┘    │
│                                         │
│  [Switch to Scanner Login]             │
└─────────────────────────────────────────┘
```

**Virtual Keyboard (dla ConnectDisplay):**
- On-screen keyboard dla urządzeń bez fizycznej klawiatury
- Obsługa touch events
- Podświetlenie aktywnego pola

---

### 3.3 User Menu

#### 3.3.1 Main User Menu
**Layout:**
```
MENU                    INTERACTION              DATA SENSORS
─────────────────────────────────────────────────────────────
... Logout             Welcome, r.arendt!        PRESSURE
                                                 
Test Menu              [Test Icon]               Low: 10 mbar
User Data              Start Testing             Med: 20 bar
Setup Test                                       High: 30 bar
Device Data            [Device Icon]
                       Browse Devices            [Photo]
Test Reports           
                       [Reports Icon]            CONNECT 500
Workshop               View Reports              Status: Ready

                       Wyszukaj urządzenie
                       przez kod QR / Barcode
```

**Funkcje przycisków:**

**Test Menu** → Przejście do wyboru testu
**User Data** → Dane zalogowanego operatora
**Setup Test** → Konfiguracja parametrów testowych
**Device Data** → Informacje o testowanym urządzeniu
**Test Reports** → Historia testów i raporty
**Workshop** → Zarządzanie warsztatem
**Logout** → Wylogowanie

---

#### 3.3.2 User Data Screen
**Endpoint:** `GET /api/users/me`

```
┌─────────────────────────────────────────┐
│ USER DATA                               │
│                                         │
│  [Photo]  OPERATOR: Robert Arendt      │
│           Username: r.arendt            │
│           Role: Operator                │
│           ID: OP-RARENDT-2025-001      │
│                                         │
│  Workshop: Workshop Poznań              │
│  Location: PL-POZ-01                   │
│                                         │
│  Tests Today:        15                │
│  Tests This Month:   324               │
│  Total Tests:        2,847             │
│                                         │
│  Last Login: 12.12.2025 - 08:15:22    │
│                                         │
│  Certifications:                       │
│  ✓ PP Mask Tester - Valid to 2026     │
│  ✓ SCBA Tester - Valid to 2025        │
│                                         │
│  [Change Password] [View History]      │
└─────────────────────────────────────────┘
```

---

### 3.4 Test Menu - Kompleksowy Przepływ

#### 3.4.1 Struktura Test Menu
```
TEST MENU
├── Kind of Device (Rodzaj urządzenia)
│   ├── PP Mask (Maska nadciśnieniowa)
│   ├── NP Mask (Maska podciśnieniowa)
│   ├── SCBA (Aparat powietrzny)
│   └── CPS Protection Suit (Kombinezon ochronny)
│
├── Device Type (Typ urządzenia)
│   ├── Ultra Elite
│   ├── G1
│   ├── FPS 7000
│   ├── OptiPro
│   ├── M1
│   └── PSS 5000/7000
│
├── Kind of Test (Rodzaj testu)
│   ├── Po użyciu
│   ├── Co 1/3 roku
│   ├── Co 1 rok
│   ├── Co 2 lata
│   ├── Co 4 lata
│   └── Co 6 lat
│
├── Test Flow (Scenariusz testowy)
│   ├── Scenariusz 1: Test szczelności
│   ├── Scenariusz 2: Test zaworów
│   ├── Scenariusz 3: Pełen przegląd
│   ├── Scenariusz 4: Test pneumatyki
│   └── Scenariusz 5: Test awaryjny
│
└── Test Steps (Kroki testowe)
    ├── Step 1: Kontrola wzrokowa
    ├── Step 2: Wytworzenie podciśnienia
    ├── Step 3: Stabilizacja
    ├── Step 4: Ustawienie parametrów
    ├── Step 5: Test szczelności
    └── ...
```

---

#### 3.4.2 Screen: Kind of Device
**Endpoint:** `GET /api/devices/kinds`

```
┌─────────────────────────────────────────────────────────┐
│ TEST MENU > Kind of Device                              │
│                                                          │
│ Wybierz rodzaj urządzenia do testu:                    │
│                                                          │
│ ┌─────────────────┐  ┌─────────────────┐              │
│ │   [PP Mask]     │  │   [NP Mask]     │              │
│ │   [Photo]       │  │   [Photo]       │              │
│ │ Maska           │  │ Maska           │              │
│ │ nadciśnieniowa  │  │ podciśnieniowa  │              │
│ └─────────────────┘  └─────────────────┘              │
│                                                          │
│ ┌─────────────────┐  ┌─────────────────┐              │
│ │   [SCBA]        │  │ [CPS Suit]      │              │
│ │   [Photo]       │  │   [Photo]       │              │
│ │ Aparat          │  │ Kombinezon      │              │
│ │ powietrzny      │  │ ochronny        │              │
│ └─────────────────┘  └─────────────────┘              │
│                                                          │
│ Do czego służy test: Wybór rodzaju urządzenia          │
│ ochrony osobistej determinuje dostępne procedury       │
│ testowe.                                                │
│                                                          │
│ [Help / Follow Me]                                      │
└─────────────────────────────────────────────────────────┘
```

**Response:**
```json
{
  "device_kinds": [
    {
      "id": 1,
      "name": "PP Mask",
      "full_name": "Positive Pressure Mask",
      "description": "Maska nadciśnieniowa",
      "photo_url": "/images/devices/pp-mask.jpg",
      "available_types": [1, 2, 3]
    },
    {
      "id": 2,
      "name": "NP Mask",
      "full_name": "Negative Pressure Mask",
      "description": "Maska podciśnieniowa",
      "photo_url": "/images/devices/np-mask.jpg",
      "available_types": [4, 5]
    }
  ]
}
```

---

#### 3.4.3 Screen: Device Type
**Endpoint:** `GET /api/devices/types?kind_id=1`

```
┌─────────────────────────────────────────────────────────┐
│ TEST MENU > PP Mask > Device Type                       │
│                                                          │
│ Wybierz typ maski nadciśnieniowej:                      │
│                                                          │
│ ┌──────────────────────────────────────┐               │
│ │ ● Ultra Elite                         │               │
│ │   [Photo]                             │               │
│ │   Maska pełnotwarzowa, klasa A1B2E2K2│               │
│ └──────────────────────────────────────┘               │
│                                                          │
│ ┌──────────────────────────────────────┐               │
│ │ ○ G1                                  │               │
│ │   [Photo]                             │               │
│ │   Maska pełnotwarzowa, klasa ABEK    │               │
│ └──────────────────────────────────────┘               │
│                                                          │
│ ┌──────────────────────────────────────┐               │
│ │ ○ FPS 7000                            │               │
│ │   [Photo]                             │               │
│ │   Maska profesjonalna, multi-gas     │               │
│ └──────────────────────────────────────┘               │
│                                                          │
│ Scan QR/Barcode na urządzeniu:                         │
│ [________________]  [Scan Button]                      │
│                                                          │
│ [Help / Follow Me]                                      │
└─────────────────────────────────────────────────────────┘
```

---

#### 3.4.4 Screen: Kind of Test
**Endpoint:** `GET /api/tests/kinds?device_type_id=2`

```
┌─────────────────────────────────────────────────────────┐
│ TEST MENU > PP Mask > G1 > Kind of Test                │
│                                                          │
│ Wybierz częstotliwość/typ testu:                       │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │ ● Co 12 miesięcy                   │ 🔄 RECOMMENDED │
│ │   Pełny przegląd okresowy          │                 │
│ │   Czas: ~45 min                    │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │ ○ Po użyciu                        │ ⚡ QUICK       │
│ │   Szybki test funkcjonalny         │                 │
│ │   Czas: ~10 min                    │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │ ○ Co 1/3 roku (4 miesiące)         │                 │
│ │   Test kontrolny                   │                 │
│ │   Czas: ~20 min                    │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │ ○ Co 2 lata                        │ 🔧 EXTENDED   │
│ │   Przegląd główny z wymianą części│                 │
│ │   Czas: ~90 min                    │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ Ostatni test: 15.11.2024 (28 dni temu)                │
│ Następny test: 15.11.2025 (337 dni)                   │
└─────────────────────────────────────────────────────────┘
```

---

#### 3.4.5 Screen: Test Flow
**Endpoint:** `GET /api/test-scenarios?test_kind_id=3&device_type_id=2`

```
┌─────────────────────────────────────────────────────────┐
│ TEST MENU > G1 > Co 12 m-cy > Test Flow                │
│                                                          │
│ Wybierz scenariusz testowy:                            │
│                                                          │
│ ┌────────────────────────────────────────┐             │
│ │ ● Scenariusz 1: Test standardowy       │             │
│ │   7 kroków | ~45 min                   │             │
│ │   ├─ Kontrola wzrokowa                 │             │
│ │   ├─ Wytworzenie podciśnienia          │             │
│ │   ├─ Stabilizacja                      │             │
│ │   ├─ Test szczelności (60s)            │             │
│ │   ├─ Test zaworu wydechowego           │             │
│ │   ├─ Test przepływu                    │             │
│ │   └─ Raport końcowy                    │             │
│ └────────────────────────────────────────┘             │
│                                                          │
│ ┌────────────────────────────────────────┐             │
│ │ ○ Scenariusz 2: Test przyśpieszony     │             │
│ │   4 kroki | ~20 min                    │             │
│ │   (pominięte testy opcjonalne)         │             │
│ └────────────────────────────────────────┘             │
│                                                          │
│ ┌────────────────────────────────────────┐             │
│ │ ○ Scenariusz 3: Test po naprawie       │             │
│ │   9 kroków | ~60 min                   │             │
│ │   (rozszerzona weryfikacja)            │             │
│ └────────────────────────────────────────┘             │
│                                                          │
│ [View Details]  [Start Test]                           │
└─────────────────────────────────────────────────────────┘
```

---

### 3.5 Test Execution - Szczegółowy Przepływ

#### 3.5.1 Pre-Test Setup
**Endpoint:** `POST /api/tests/initialize`

**Request:**
```json
{
  "device_kind_id": 1,
  "device_type_id": 2,
  "test_kind_id": 3,
  "scenario_id": 1,
  "device_serial": "G1-2024-001234",
  "customer_id": 45,
  "operator_id": 15,
  "workshop_id": 3
}
```

**Response:**
```json
{
  "test_session_id": "TEST-2025-001234",
  "status": "initialized",
  "estimated_duration": 45,
  "total_steps": 7,
  "current_step": 0,
  "device": {
    "id": 234,
    "serial": "G1-2024-001234",
    "last_test_date": "2024-11-15",
    "last_test_result": "PASSED",
    "maintenance_history": []
  },
  "required_tools": [
    "Czujnik ciśnienia",
    "Manometr",
    "Klucz montażowy 8mm"
  ],
  "safety_notes": [
    "Sprawdź połączenia pneumatyczne",
    "Upewnij się że zawór jest zamknięty",
    "Załóż rękawice ochronne"
  ]
}
```

**UI Display:**
```
┌─────────────────────────────────────────────────────────┐
│ TEST PREPARATION                                        │
│                                                          │
│ Test ID: TEST-2025-001234                              │
│ Device: G1-2024-001234                                 │
│ Scenario: Test standardowy (7 kroków, ~45 min)        │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │ ℹ️  REQUIRED TOOLS                  │                 │
│ │                                     │                 │
│ │ ☑ Czujnik ciśnienia                │                 │
│ │ ☑ Manometr                          │                 │
│ │ ☐ Klucz montażowy 8mm               │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │ ⚠️  SAFETY NOTES                    │                 │
│ │                                     │                 │
│ │ • Sprawdź połączenia pneumatyczne  │                 │
│ │ • Upewnij się że zawór zamknięty   │                 │
│ │ • Załóż rękawice ochronne          │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ Device History:                                         │
│ Last Test: 15.11.2024 - PASSED                        │
│ Tests Performed: 12                                     │
│ Issues Found: 0                                         │
│                                                          │
│ [Cancel]  [Scan Device QR]  [Start Test]              │
└─────────────────────────────────────────────────────────┘
```

---

#### 3.5.2 Test Steps Execution

**Step 1: Kontrola Wzrokowa**
**Endpoint:** `POST /api/tests/{test_id}/step/1`

```
┌─────────────────────────────────────────────────────────┐
│ TEST IN PROGRESS [Step 1 of 7]                         │
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░ 14%                  │
│                                                          │
│ STEP 1: KONTROLA WZROKOWA                              │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │ Sprawdź wizualnie:                 │                 │
│ │                                     │                 │
│ │ ☐ Brak uszkodzeń mechanicznych     │                 │
│ │ ☐ Brak pęknięć wizjera             │                 │
│ │ ☐ Maski elastomerowe nieuszkodzone │                 │
│ │ ☐ Zaciski i paski w dobrym stanie │                 │
│ │ ☐ Zawory działają płynnie          │                 │
│ │ ☐ Brak zanieczyszczeń              │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ Uwagi operatora:                                        │
│ ┌────────────────────────────────────┐                 │
│ │ [Text area for notes]              │                 │
│ │                                     │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ [Take Photo]  [Add Note]                               │
│                                                          │
│ Result: ○ PASSED  ○ FAILED  ○ WARNING                 │
│                                                          │
│ [Previous]  [Save & Next]  [Abort Test]                │
└─────────────────────────────────────────────────────────┘
```

**Request:**
```json
{
  "test_session_id": "TEST-2025-001234",
  "step_id": 1,
  "step_name": "Kontrola wzrokowa",
  "result": "PASSED",
  "operator_checks": {
    "mechanical_damage": false,
    "visor_cracks": false,
    "elastomer_condition": "good",
    "straps_condition": "good",
    "valves_operation": "smooth",
    "contamination": false
  },
  "operator_notes": "Wszystko w porządku, brak usterek",
  "photos": [
    "/uploads/test-001234-step1-photo1.jpg",
    "/uploads/test-001234-step1-photo2.jpg"
  ],
  "duration": 120
}
```

---

**Step 2: Wytworzenie Podciśnienia (-14 mbar)**
**Endpoint:** `POST /api/tests/{test_id}/step/2`

```
┌─────────────────────────────────────────────────────────┐
│ TEST IN PROGRESS [Step 2 of 7]                         │
│ ████████████████░░░░░░░░░░░░░░░░ 28%                  │
│                                                          │
│ STEP 2: WYTWORZENIE PODCIŚNIENIA                       │
│                                                          │
│ Target: -14 mbar                                        │
│ Tolerance: ±0.5 mbar                                    │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │   REAL-TIME PRESSURE                │                 │
│ │                                     │                 │
│ │   ┌─────────────────────────────┐  │                 │
│ │   │                             │  │                 │
│ │   │        -13.8 mbar           │  │                 │
│ │   │                             │  │                 │
│ │   │   [Pressure Gauge Graphic]  │  │                 │
│ │   │                             │  │                 │
│ │   └─────────────────────────────┘  │                 │
│ │                                     │                 │
│ │   Status: ✓ IN RANGE               │                 │
│ │   Time: 00:15 / 00:30              │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ Automatic Test: ● IN PROGRESS                          │
│                                                          │
│ [Manual Override]  [Stop]                              │
│                                                          │
│ [Previous]  [Save & Next]  [Abort Test]                │
└─────────────────────────────────────────────────────────┘
```

**WebSocket Real-time Updates:**
```javascript
// Client subscribes to test updates
socket.on('test_pressure_update', (data) => {
  /*
  {
    "test_session_id": "TEST-2025-001234",
    "step_id": 2,
    "pressure": -13.8,
    "target": -14,
    "tolerance": 0.5,
    "status": "in_range",
    "timestamp": "2025-09-29T10:30:45Z"
  }
  */
});
```

**Step Completion:**
```json
{
  "test_session_id": "TEST-2025-001234",
  "step_id": 2,
  "step_name": "Wytworzenie podciśnienia",
  "result": "PASSED",
  "automatic": true,
  "measurements": {
    "target_pressure": -14,
    "achieved_pressure": -13.8,
    "tolerance": 0.5,
    "time_to_achieve": 15,
    "stability": "stable"
  },
  "sensor_data": [
    {"time": 0, "pressure": 0},
    {"time": 5, "pressure": -7.2},
    {"time": 10, "pressure": -12.5},
    {"time": 15, "pressure": -13.8}
  ],
  "duration": 30
}
```

---

**Step 5: Test Szczelności Maski (60s)**
```
┌─────────────────────────────────────────────────────────┐
│ TEST IN PROGRESS [Step 5 of 7]                         │
│ ████████████████████████████░░░░ 71%                   │
│                                                          │
│ STEP 5: TEST SZCZELNOŚCI MASKI (60s)                   │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │ Pressure Drop Test                  │                 │
│ │                                     │                 │
│ │ Initial Pressure: -14.0 mbar       │                 │
│ │ Current Pressure: -13.6 mbar       │                 │
│ │ Pressure Drop:     0.4 mbar        │                 │
│ │ Max Allowed:       1.4 mbar (10%)  │                 │
│ │                                     │                 │
│ │ ┌─────────────────────────────────┐│                 │
│ │ │  📊 Pressure Graph              ││                 │
│ │ │  -14.0 ┤───────────────\        ││                 │
│ │ │        │                 \       ││                 │
│ │ │  -13.6 ┤                  ──────││                 │
│ │ │        │                         ││                 │
│ │ │        └──────────────────────── ││                 │
│ │ │        0s    30s    60s          ││                 │
│ │ └─────────────────────────────────┘│                 │
│ │                                     │                 │
│ │ Time Remaining: 23s                │                 │
│ │ Status: ✓ PASSING                  │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ Criteria: Pressure drop < 10% in 60s                   │
│                                                          │
│ [Stop Early]                                            │
│                                                          │
│ [Previous]  [Waiting...]  [Abort Test]                 │
└─────────────────────────────────────────────────────────┘
```

---

#### 3.5.3 Test Completion & Report

```
┌─────────────────────────────────────────────────────────┐
│ TEST COMPLETED ✓                                        │
│                                                          │
│ Test ID: TEST-2025-001234                              │
│ Device: G1-2024-001234                                 │
│ Duration: 42 min 35 sec                                │
│ Result: PASSED                                          │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │ TEST SUMMARY                        │                 │
│ │                                     │                 │
│ │ ✓ Step 1: Kontrola wzrokowa        │ PASSED          │
│ │ ✓ Step 2: Wytworzenie podciśnienia │ PASSED          │
│ │ ✓ Step 3: Stabilizacja             │ PASSED          │
│ │ ✓ Step 4: Ustawienie parametrów    │ PASSED          │
│ │ ✓ Step 5: Test szczelności         │ PASSED          │
│ │ ✓ Step 6: Test zaworu              │ PASSED          │
│ │ ✓ Step 7: Test przepływu           │ PASSED          │
│ └────────────────────────────────────┘                 │
│                                                          │
│ ┌────────────────────────────────────┐                 │
│ │ KEY MEASUREMENTS                    │                 │
│ │                                     │                 │
│ │ Pressure achieved: -13.8 mbar      │                 │
│ │ Pressure drop: 0.4 mbar (2.8%)     │                 │
│ │ Valve pressure: 3.2 bar            │                 │
│ │ Flow rate: 10.2 l/min              │                 │
│ └────────────────────────────────────┘                 │
│                                                          │
│ Next test due: 29.09.2026                              │
│                                                          │
│ [Print Label]  [View Full Report]  [Export PDF]       │
│ [Start New Test]  [Return to Menu]                     │
└─────────────────────────────────────────────────────────┘
```

**Report Generation:**
**Endpoint:** `GET /api/tests/{test_id}/report`

---

### 3.6 Workshop Management

#### 3.6.1 Equipment List
**Endpoint:** `GET /api/workshop/equipment`

```
┌─────────────────────────────────────────────────────────┐
│ WORKSHOP > Equipment List                              │
│                                                          │
│ [Filter: All] [Search: _______]  [+ Add Equipment]    │
│                                                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ Device Serial    Type      Status    Last Test   │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ G1-2024-001234  PP Mask    ● Active  15.11.2024 │   │
│ │ G1-2024-001235  PP Mask    ● Active  20.11.2024 │   │
│ │ PSS-2023-00567  SCBA       ⚠ Warning 01.09.2024 │   │
│ │ FPS-2024-00123  NP Mask    ● Active  25.11.2024 │   │
│ │ G1-2022-000789  PP Mask    🔴 Expired 15.01.2024│   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Legend:                                                  │
│ ● Active - Device in use, test valid                   │
│ ⚠ Warning - Test due within 30 days                    │
│ 🔴 Expired - Test overdue, device unusable             │
│                                                          │
│ Total Equipment: 247                                    │
│ Tests Due (30 days): 23                                │
│ Expired: 5                                              │
│                                                          │
│ [Export List]  [Generate Schedule]                     │
└─────────────────────────────────────────────────────────┘
```

---

#### 3.6.2 Maintenance Schedule
**Endpoint:** `GET /api/workshop/schedule`

```
┌─────────────────────────────────────────────────────────┐
│ WORKSHOP > Maintenance Schedule                        │
│                                                          │
│ ┌────────────┬────────────┬────────────┬────────────┐  │
│ │    This    │    Week    │   Month    │   Quarter  │  │
│ │    Week    │     2      │     2      │     3      │  │
│ └────────────┴────────────┴────────────┴────────────┘  │
│                                                          │
│ OVERDUE (5):                                            │
│ ┌──────────────────────────────────────────────────┐   │
│ │ 🔴 G1-2022-000789  | Due: 15.01.2024 | 289 days │   │
│ │ 🔴 PSS-2022-00134  | Due: 20.02.2024 | 253 days │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ THIS WEEK (8):                                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ ⚠ G1-2024-002341  | Due: 02.10.2025 | 3 days    │   │
│ │ ⚠ FPS-2024-00567  | Due: 04.10.2025 | 5 days    │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ NEXT 30 DAYS (23):                                      │
│ [View All]                                              │
│                                                          │
│ [Send Reminders]  [Export Schedule]  [Print]          │
└─────────────────────────────────────────────────────────┘
```

---

#### 3.6.3 Spare Parts Management
**Endpoint:** `GET /api/workshop/spare-parts`

```
┌─────────────────────────────────────────────────────────┐
│ WORKSHOP > Spare Parts                                 │
│                                                          │
│ [Category: All ▼]  [Search: _______]  [+ Add Part]    │
│                                                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ Part Name        SKU         Stock   Min   Status│   │
│ ├──────────────────────────────────────────────────┤   │
│ │ Zawór wydechowy  ZW-001      45      10    ✓ OK │   │
│ │ Wizjer G1        WZ-G1-001   8       15    ⚠ Low│   │
│ │ Maska elastomer  ME-001      3       10    🔴 Crit│   │
│ │ Pasek głowowy    PG-001      125     20    ✓ OK │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Parts Below Minimum: 2                                  │
│ Total Value: 12,450 PLN                                │
│                                                          │
│ [Create Order]  [Import CSV]  [Export Inventory]      │
└─────────────────────────────────────────────────────────┘
```

---

### 3.7 Test Reports Module

#### 3.7.1 Current Reports
**Endpoint:** `GET /api/reports/current?days=30`

```
┌─────────────────────────────────────────────────────────┐
│ TEST REPORTS > Current Reports (Last 30 days)         │
│                                                          │
│ [Date Range: Last 30 days ▼]  [Search: _______]       │
│                                                          │
│ Statistics:                                             │
│ Total Tests: 324  | Passed: 318 | Failed: 4 | Warn: 2 │
│ Pass Rate: 98.1%                                        │
│                                                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ Date       Device      Operator  Result  Time   │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ 29.09 12:05 G1-001234  r.arendt  ✓ PASS  42min │   │
│ │ 29.09 10:30 PSS-00567  j.kowal   ✓ PASS  58min │   │
│ │ 28.09 15:20 FPS-00123  r.arendt  ⚠ WARN  35min │   │
│ │ 28.09 14:10 G1-002341  m.nowak   ✓ PASS  40min │   │
│ │ 28.09 11:45 G1-000789  r.arendt  🔴 FAIL 25min │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ [View Report]  [Export All]  [Generate Summary]       │
└─────────────────────────────────────────────────────────┘
```

---

## 4. BAZA DANYCH - ROZSZERZONA SPECYFIKACJA

### 4.1 Tabele Specyficzne dla Connect++

#### 4.1.1 Test Sessions
```sql
CREATE TABLE test_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    device_id INTEGER REFERENCES devices(id),
    scenario_id INTEGER REFERENCES test_scenarios(id),
    operator_id INTEGER REFERENCES users(id),
    customer_id INTEGER REFERENCES customers(id),
    workshop_id INTEGER REFERENCES workshops(id),
    
    status VARCHAR(50) NOT NULL, -- initialized, in_progress, completed, aborted, failed
    
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    estimated_duration INTEGER, -- minutes
    actual_duration INTEGER,
    
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER,
    
    result VARCHAR(50), -- PASSED, FAILED, WARNING
    
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_sessions_status ON test_sessions(status);
CREATE INDEX idx_test_sessions_operator ON test_sessions(operator_id);
CREATE INDEX idx_test_sessions_date ON test_sessions(start_time);
```

#### 4.1.2 Test Step Results
```sql
CREATE TABLE test_step_results (
    id SERIAL PRIMARY KEY,
    test_session_id INTEGER REFERENCES test_sessions(id),
    step_id INTEGER,
    step_name VARCHAR(255) NOT NULL,
    step_order INTEGER NOT NULL,
    
    status VARCHAR(50), -- pending, in_progress, completed, skipped, failed
    result VARCHAR(50), -- PASSED, FAILED, WARNING, N/A
    
    automatic BOOLEAN DEFAULT FALSE,
    operator_participation BOOLEAN DEFAULT TRUE,
    
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration INTEGER, -- seconds
    
    measurements JSONB,
    operator_checks JSONB,
    operator_notes TEXT,
    photos TEXT[], -- array of photo URLs
    
    criteria JSONB,
    criteria_met BOOLEAN,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.1.3 Sensor Data (Time Series)
```sql
CREATE TABLE sensor_readings (
    id BIGSERIAL PRIMARY KEY,
    test_session_id INTEGER REFERENCES test_sessions(id),
    step_id INTEGER,
    
    sensor_type VARCHAR(50), -- pressure_low, pressure_medium, pressure_high, flow, temperature
    sensor_id VARCHAR(100),
    
    value DECIMAL(10, 3),
    unit VARCHAR(20),
    
    timestamp TIMESTAMP NOT NULL,
    
    metadata JSONB
);

CREATE INDEX idx_sensor_test_session ON sensor_readings(test_session_id);
CREATE INDEX idx_sensor_timestamp ON sensor_readings(timestamp);
```

#### 4.1.4 Workshop
```sql
CREATE TABLE workshops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    address TEXT,
    contact_info JSONB,
    
    capacity INTEGER,
    active_devices INTEGER DEFAULT 0,
    
    configuration JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.1.5 Equipment Inventory
```sql
CREATE TABLE equipment_inventory (
    id SERIAL PRIMARY KEY,
    workshop_id INTEGER REFERENCES workshops(id),
    device_id INTEGER REFERENCES devices(id),
    
    status VARCHAR(50), -- active, warning, expired, maintenance, retired
    location VARCHAR(255),
    
    last_test_date DATE,
    next_test_date DATE,
    test_interval INTEGER, -- days
    
    maintenance_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_workshop ON equipment_inventory(workshop_id);
CREATE INDEX idx_equipment_status ON equipment_inventory(status);
CREATE INDEX idx_equipment_next_test ON equipment_inventory(next_test_date);
```

#### 4.1.6 Spare Parts
```sql
CREATE TABLE spare_parts (
    id SERIAL PRIMARY KEY,
    workshop_id INTEGER REFERENCES workshops(id),
    
    part_name VARCHAR(255) NOT NULL,
    part_number VARCHAR(100) UNIQUE NOT NULL,
    sku VARCHAR(100),
    
    category VARCHAR(100),
    compatible_devices TEXT[], -- array of device types
    
    stock_quantity INTEGER DEFAULT 0,
    min_quantity INTEGER DEFAULT 10,
    unit_price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'PLN',
    
    supplier_info JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 4.2 Przykładowe Zapytania SQL

#### 4.2.1 Pobierz aktywną sesję testową
```sql
SELECT 
    ts.*,
    d.device_number,
    d.device_type,
    sc.name as scenario_name,
    u.username as operator_name,
    w.name as workshop_name
FROM test_sessions ts
JOIN devices d ON ts.device_id = d.id
JOIN test_scenarios sc ON ts.scenario_id = sc.id
JOIN users u ON ts.operator_id = u.id
JOIN workshops w ON ts.workshop_id = w.id
WHERE ts.status IN ('initialized', 'in_progress')
    AND ts.operator_id = $1
ORDER BY ts.start_time DESC
LIMIT 1;
```

#### 4.2.2 Harmonogram testów (następne 30 dni)
```sql
SELECT 
    ei.*,
    d.device_number,
    d.device_type,
    w.name as workshop_name,
    EXTRACT(DAY FROM (ei.next_test_date - CURRENT_DATE)) as days_until_test
FROM equipment_inventory ei
JOIN devices d ON ei.device_id = d.id
JOIN workshops w ON ei.workshop_id = w.id
WHERE ei.next_test_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
    AND ei.status = 'active'
ORDER BY ei.next_test_date ASC;
```

#### 4.2.3 Statystyki operatora
```sql
SELECT 
    u.username,
    COUNT(ts.id) as total_tests,
    COUNT(CASE WHEN ts.result = 'PASSED' THEN 1 END) as passed,
    COUNT(CASE WHEN ts.result = 'FAILED' THEN 1 END) as failed,
    AVG(ts.actual_duration) as avg_duration,
    MAX(ts.end_time) as last_test_date
FROM test_sessions ts
JOIN users u ON ts.operator_id = u.id
WHERE ts.status = 'completed'
    AND ts.start_time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.id, u.username
ORDER BY total_tests DESC;
```

---

## 5. PC vs DEVICE (ConnectDisplay) - RÓŻNICE

### 5.1 Wersja PC (Desktop/Laptop)

**Rozdzielczość:** 1920x1080 lub wyższa
**Przeglądarka:** Chrome, Firefox, Edge (modern browsers)
**Input:** Mysz + Klawiatura

**Cechy:**
- Pełny interfejs z wszystkimi funkcjami
- Większe elementy graficzne
- Zaawansowane wykresy i wizualizacje
- Multi-window support
- Keyboard shortcuts
- Drag & drop
- Hover effects
- Right-click context menus

**Przykładowy layout (1920x1080):**
```
Menu: 384px (20%)
Interaction: 1056px (55%)
Sensors: 480px (25%)
```

---

### 5.2 Wersja Device - ConnectDisplay (800x480)

**Hardware:**
- Raspberry Pi lub podobny
- 7" Touchscreen Display
- USB ports dla skanerów
- Physical buttons (opcjonalnie)

**Cechy:**
- Touch-optimized interface
- Larger touch targets (min 48x48px)
- Simplified navigation
- On-screen keyboard
- Swipe gestures
- Offline mode support
- Auto-reconnect
- Power-saving mode

**Przykładowy layout (800x480):**
```
Menu: 200px (25%)
Interaction: 400px (50%)
Sensors: 200px (25%)
```

**Różnice funkcjonalne:**

| Funkcja | PC | ConnectDisplay |
|---------|----|----|
| Multi-window | ✓ | ✗ |
| Keyboard shortcuts | ✓ | ✗ |
| Drag & drop | ✓ | ✗ |
| Touch gestures | ✗ | ✓ |
| Physical buttons | ✗ | ✓ (opcjonalnie) |
| Offline mode | Limited | ✓ |
| Quick actions | Toolbar | Bottom buttons |
| Scanner integration | USB | USB + dedicated port |

---

### 5.3 Responsive Design Breakpoints

```css
/* Mobile First Approach */

/* ConnectDisplay - 800x480 */
@media (max-width: 800px) {
  .menu { width: 25%; font-size: 14px; }
  .interaction { width: 50%; }
  .sensors { width: 25%; font-size: 12px; }
  .touch-target { min-width: 48px; min-height: 48px; }
}

/* Tablet - 1024x768 */
@media (min-width: 801px) and (max-width: 1280px) {
  .menu { width: 22%; }
  .interaction { width: 53%; }
  .sensors { width: 25%; }
}

/* Desktop - 1920x1080+ */
@media (min-width: 1281px) {
  .menu { width: 20%; }
  .interaction { width: 55%; }
  .sensors { width: 25%; }
}
```

---

## 6. TECHNOLOGIE I IMPLEMENTACJA

### 6.1 Frontend Stack

**Core:**
- React 18+ / Vue 3+
- TypeScript
- Tailwind CSS

**UI Components:**
- Headless UI / Radix UI
- Chart.js / Recharts (wykresy)
- React Hook Form (formularze)
- Zod (walidacja)

**State Management:**
- Redux Toolkit / Zustand
- React Query (cache & sync)

**Real-time:**
- Socket.io-client
- WebRTC (dla remote control)

**PWA Support:**
- Service Workers
- Offline storage (IndexedDB)
- Push notifications

---

### 6.2 Przykładowy Kod - Test Step Component

```typescript
// TestStepComponent.tsx
import React, { useState, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { PressureGauge } from '@/components/PressureGauge';

interface TestStepProps {
  testSessionId: string;
  stepId: number;
  stepData: TestStep;
}

export const TestStepComponent: React.FC<TestStepProps> = ({
  testSessionId,
  stepId,
  stepData
}) => {
  const [stepResult, setStepResult] = useState<StepResult | null>(null);
  const [pressure, setPressure] = useState<number>(0);
  const socket = useWebSocket();

  useEffect(() => {
    // Subscribe to real-time pressure updates
    socket.on('test_pressure_update', (data) => {
      if (data.test_session_id === testSessionId && data.step_id === stepId) {
        setPressure(data.pressure);
      }
    });

    return () => {
      socket.off('test_pressure_update');
    };
  }, [socket, testSessionId, stepId]);

  const handleStepComplete = async () => {
    const result = {
      test_session_id: testSessionId,
      step_id: stepId,
      result: 'PASSED',
      measurements: {
        final_pressure: pressure
      }
    };

    await fetch(`/api/tests/${testSessionId}/step/${stepId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result)
    });
  };

  return (
    <div className="test-step-container">
      <div className="step-header">
        <h2>{stepData.name}</h2>
        <div className="progress-bar">
          {/* Progress visualization */}
        </div>
      </div>

      <div className="step-content">
        {stepData.automatic ? (
          <AutomaticTestView 
            pressure={pressure}
            target={stepData.target_pressure}
          />
        ) : (
          <ManualTestView 
            checklist={stepData.operator_checks}
            onComplete={handleStepComplete}
          />
        )}
      </div>

      <PressureGauge 
        value={pressure}
        min={-20}
        max={300}
        unit="mbar"
      />
    </div>
  );
};
```

---

### 6.3 Backend Endpoints - Szczegóły

#### Start Test Session
```python
# app/api/tests.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/tests/initialize")
async def initialize_test(
    test_data: TestInitialize,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate device availability
    device = db.query(Device).filter(Device.id == test_data.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check if device has active test
    active_test = db.query(TestSession).filter(
        TestSession.device_id == test_data.device_id,
        TestSession.status.in_(['initialized', 'in_progress'])
    ).first()
    
    if active_test:
        raise HTTPException(
            status_code=400, 
            detail="Device already has an active test session"
        )
    
    # Create test session
    test_session = TestSession(
        session_id=generate_test_id(),
        device_id=test_data.device_id,
        scenario_id=test_data.scenario_id,
        operator_id=current_user.id,
        customer_id=test_data.customer_id,
        workshop_id=current_user.workshop_id,
        status='initialized',
        start_time=datetime.utcnow(),
        total_steps=get_scenario_steps_count(test_data.scenario_id)
    )
    
    db.add(test_session)
    db.commit()
    db.refresh(test_session)
    
    return {
        "test_session_id": test_session.session_id,
        "status": "initialized",
        "device": device.to_dict(),
        "estimated_duration": calculate_duration(test_data.scenario_id)
    }
```

---

## 7. DEPLOYMENT & CONFIGURATION

### 7.1 Docker Configuration

```dockerfile
# Dockerfile.cpp
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist ./static

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 7.2 Environment Variables

```bash
# .env.cpp
APP_NAME="Connect++ CPP"
APP_PORT=8080
APP_VERSION=1.0.0

DATABASE_URL=postgresql://user:pass@localhost:5432/fleetdb
REDIS_URL=redis://localhost:6379/0

JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

CORS_ORIGINS=["http://localhost:3000", "http://192.168.1.100:8080"]

# WebSocket
WS_PING_INTERVAL=30
WS_PING_TIMEOUT=10

# Device Settings
DEVICE_MODE=production
ENABLE_OFFLINE_MODE=true
SYNC_INTERVAL=300

# Sensor Configuration
PRESSURE_LOW_MIN=-20
PRESSURE_LOW_MAX=0
PRESSURE_MEDIUM_MIN=0
PRESSURE_MEDIUM_MAX=50
PRESSURE_HIGH_MIN=0
PRESSURE_HIGH_MAX=300
```

---

## 8. TESTING & QUALITY ASSURANCE

### 8.1 Unit Tests Example

```python
# tests/test_test_session.py
import pytest
from app.services.test_service import TestService
from app.models import TestSession, Device, User

@pytest.fixture
def test_service(db_session):
    return TestService(db_session)

def test_initialize_test_session(test_service, mock_device, mock_user):
    result = test_service.initialize_test(
        device_id=mock_device.id,
        scenario_id=1,
        operator_id=mock_user.id
    )
    
    assert result is not None
    assert result.status == 'initialized'
    assert result.device_id == mock_device.id

def test_cannot_start_duplicate_test(test_service, mock_device, mock_user):
    # Start first test
    test_service.initialize_test(
        device_id=mock_device.id,
        scenario_id=1,
        operator_id=mock_user.id
    )
    
    # Try to start second test on same device
    with pytest.raises(ValueError, match="Device already has active test"):
        test_service.initialize_test(
            device_id=mock_device.id,
            scenario_id=1,
            operator_id=mock_user.id
        )
```

---

## 9. DOKUMENTACJA UŻYTKOWNIKA

### 9.1 Quick Start Guide dla Operatorów

**Krok 1: Logowanie**
1. Włącz urządzenie ConnectDisplay lub otwórz przeglądarkę na PC
2. Poczekaj na autodiagnostykę (6s)
3. Zeskanuj swój kod QR lub wpisz login/hasło
4. Potwierdź dane użytkownika

**Krok 2: Rozpoczęcie testu**
1. Wybierz "Test Menu" z menu głównego
2. Zeskanuj kod QR urządzenia do testowania
3. Wybierz rodzaj testu (np. "Co 12 miesięcy")
4. Potwierdź scenariusz testowy
5. Kliknij "Start Test"

**Krok 3: Wykonanie testu**
1. Postępuj zgodnie z instrukcjami na ekranie
2. Dla testów automatycznych - monitoruj czujniki
3. Dla kontroli wizualnych - zaznacz checkboxy
4. Dodaj notatki jeśli potrzeba
5. Przejdź do kolejnego kroku

**Krok 4: Zakończenie**
1. Przejrzyj podsumowanie testu
2. Wydrukuj etykietę dla urządzenia
3. Eksportuj raport PDF
4. Rozpocznij kolejny test lub wyloguj się

---

## 10. PRZYSZŁE ROZSZERZENIA

### 10.1 Faza 2 Features
- ✓ AI-powered anomaly detection
- ✓ Predictive maintenance alerts
- ✓ Mobile app (iOS/Android)
- ✓ Voice commands
- ✓ AR instructions dla operatorów
- ✓ Blockchain dla certyfikatów
- ✓ Integration z ERP systems

### 10.2 Metryki Sukcesu
- Czas testu: reduce by 25%
- Test accuracy: > 99.5%
- User adoption: > 90%
- System uptime: > 99.9%
- Customer satisfaction: > 4.5/5

---

## PODSUMOWANIE

Connect++ (CPP) jest kompleksowym modułem operatorskim zaprojektowanym dla warsztatów testowych. System oferuje:

✅ **Intuicyjny interfejs** dla operatorów na PC i dedykowanych urządzeniach
✅ **Real-time monitoring** czujników i postępu testów
✅ **Automatyzację** większości kroków testowych
✅ **Kompleksowe raportowanie** z możliwością eksportu
✅ **Zarządzanie warsztatem** i harmonogramami
✅ **Offline mode** dla urządzeń ConnectDisplay
✅ **Multi-platform support** z responsywnym designem

System gotowy do wdrożenia z pełną dokumentacją techniczną i użytkową!