# Vaccine Scheduler

A command-line application for managing COVID-19 vaccine appointment scheduling, built with Python and SQLite.

Patients can search for available caregivers, reserve vaccine appointments, and manage bookings. Caregivers can upload their availability, add vaccine doses, and view scheduled appointments.

## Tech Stack

- **Language:** Python 3
- **Database:** SQLite
- **Authentication:** PBKDF2-HMAC-SHA256 with salted hashing

## Project Structure

```
src/main/
├── resources/
│   └── sqlite/
│       └── create.sql            # DDL for all tables
└── scheduler/
    ├── Scheduler.py              # Main CLI entry point
    ├── db/
    │   └── ConnectionManager.py  # SQLite connection handler
    ├── model/
    │   ├── Caregiver.py          # Caregiver model & DB operations
    │   ├── Patient.py            # Patient model & DB operations
    │   └── Vaccine.py            # Vaccine model & DB operations
    └── util/
        └── Util.py               # Password hashing utilities
```

## Database Schema

| Table | Description |
|---|---|
| **Caregivers** | Caregiver accounts with salted password hashes |
| **Patients** | Patient accounts with salted password hashes |
| **Vaccines** | Vaccine inventory (name → available doses) |
| **Availabilities** | Caregiver availability by date |
| **Appointments** | Scheduled appointments linking patient, caregiver, vaccine, and date |

## Setup

1. **Initialize the database**

   ```bash
   sqlite3 scheduler.db < src/main/resources/sqlite/create.sql
   ```

2. **Set the database path**

   ```bash
   export DBPATH=scheduler.db
   ```

3. **Run the application**

   ```bash
   cd src/main/scheduler
   python Scheduler.py
   ```

## Supported Commands

| Command | Description |
|---|---|
| `create_patient <username> <password>` | Register a new patient account |
| `create_caregiver <username> <password>` | Register a new caregiver account |
| `login_patient <username> <password>` | Log in as a patient |
| `login_caregiver <username> <password>` | Log in as a caregiver |
| `search_caregiver_schedule <date>` | View available caregivers and vaccines for a given date |
| `reserve <date> <vaccine>` | Reserve a vaccine appointment (patient only) |
| `upload_availability <date>` | Mark a date as available (caregiver only) |
| `cancel <appointment_id>` | Cancel an existing appointment |
| `add_doses <vaccine> <number>` | Add vaccine doses to inventory (caregiver only) |
| `show_appointments` | View all appointments for the logged-in user |
| `logout` | Log out of the current session |
| `quit` | Exit the application |

> Dates use `YYYY-MM-DD` format.

## Password Policy

Passwords must meet all of the following:

- At least 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character from `!`, `@`, `#`, `?`

## Design Highlights

- **Single-session model:** Only one user (patient or caregiver) may be logged in at a time.
- **Automatic caregiver assignment:** `reserve` assigns the first available caregiver alphabetically and removes that availability slot.
- **Inventory management:** Reserving an appointment decrements vaccine doses; canceling restores them.
- **Secure authentication:** Passwords are never stored in plaintext — only 16-byte salted PBKDF2 hashes.
