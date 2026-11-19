# GYM MANAGEMENT SYSTEM

A modern, clean, and comprehensive Gym Management System web application built with Python Flask and Relational Database Architecture.

---

## 1. Project Introduction & Overview

The **Gym Management System** is a full-stack web application built to manage gym operations, member registrations, certified fitness instructors, customized workout programs, membership subscription plans, billing/offline receipts, and daily attendance tracking.

---

## 2. Key Features

- **Admin Dashboard**:
  - Live metric cards: Total Members, Active Members, Certified Trainers, Workouts Offered, Active Subscriptions, Total Revenue, and Today's Attendance.
  - Interactive Chart.js visualizations for Membership Plan Distribution, Payment Status Breakdown, and 7-Day Attendance Trends.
  - Quick-access tables for recent members, recent payment transactions, and today's attendance logs.
- **Member Management (`/members`)**:
  - Complete CRUD operations.
  - Real-time search by Member ID, Name, Phone, and Email; filter by Active/Inactive status.
  - Multivalued address support using composite key table `MEMBER_ADDRESS`.
  - Comprehensive member profile page showing membership history, attendance history, and enrolled workout routines.
- **Trainer Management (`/trainers`)**:
  - Complete CRUD operations.
  - Search by Trainer ID, Name, and Specialization.
  - Multivalued professional certifications support via composite key table `TRAINER_CERTIFICATION`.
  - Trainer profile displaying managed workout routines and related payments/commissions.
- **Workout Management (`/workouts`)**:
  - Complete CRUD operations.
  - Search by Workout Name; filter by Difficulty Level (Easy, Medium, Hard) and Assigned Trainer.
  - Trainer selection via relational dropdown from MySQL.
  - Workout details showing assigned coach, enrolled trainees, and attendance history.
- **Participation Interface (`/workouts/assign`)**:
  - Dedicated Many-to-Many (`M:N`) junction management between `MEMBER` and `WORKOUT` via `PARTICIPATES_IN`.
  - Prevents duplicate `(Member_ID, Workout_ID)` enrollments.
- **Membership Management (`/memberships`)**:
  - Complete CRUD operations.
  - Member selection dropdown from MySQL.
  - Plan options: Monthly, Quarterly, Half-Yearly, Yearly.
  - **Automatic duration calculation** (`Duration_Days` derived from `Start_Date` and `End_Date`).
  - Validation: End Date cannot be before Start Date; fee amount cannot be negative.
- **Payment & Invoicing (`/payments`)**:
  - Complete CRUD operations.
  - Multi-attribute filtering (Status: Success/Pending/Failed, Payment Method: Cash/Card/UPI/NetBanking, Date range).
  - Auto-generated or custom `Transaction_ID` and `Invoice_Number`.
  - **Professional Printable Tax Invoice** (`/payments/<id>/invoice`) with company header, member billing address, line items, and print/PDF support.
- **Attendance Tracking (`/attendance`)**:
  - Daily check-in and check-out tracking.
  - **Automatic calculation of `Workout_Duration`** in minutes.
  - Multivalued coach remarks and notes stored in composite key table `ATTENDANCE_REMARKS`.
  - Filter by Attendance Date, Member, and Workout routine.
- **Database Reports (`/reports`)**:
  - 9 Real MySQL database reports with aggregate calculations:
    1. Active Members
    2. Expired Memberships
    3. Membership Revenue (grouped by Plan Name)
    4. Payment Status Breakdown
    5. Trainer Workload (workouts managed & unique trainees coached)
    6. Workout Popularity & Participation (ranked by enrolled members)
    7. Daily Attendance Breakdown (with date range filters)
    8. Monthly Attendance Aggregation
    9. Member Attendance History & Engagement

---

## 3. Technology Stack

- **Frontend**:
  - HTML5 & CSS3
  - Bootstrap 5.3 (Responsive Grid, Cards, Tables, Modals, Forms)
  - Bootstrap Icons 1.11
  - JavaScript (Vanilla JS for dynamic rows & client validation)
  - Jinja2 Template Engine
  - Chart.js 4.4 (Data visualization)
- **Backend**:
  - Python 3.10+ / Python 3.13
  - Flask (Web Framework)
  - Flask Blueprints (Modular routing architecture)
  - Flask-SQLAlchemy (ORM & relational query engine)
  - PyMySQL (MySQL driver)
  - python-dotenv (Environment configuration)
- **Database**:
  - MySQL 8.x (Relational DBMS)
  - Database Name: `gym_management`
  - InnoDB Storage Engine with utf8mb4 encoding

---

## 4. Database Structure (Exact 10 Tables)

```
                            +-------------------+
                            |      TRAINER      |
                            +-------------------+
                            | PK: Trainer_ID    |
                            | Name, Phone, ...  |
                            +---------+---------+
                                      | 1:N
                     +----------------+----------------+
                     | 1:N                             | 1:N
           +---------v---------+             +---------v---------+
           |      WORKOUT      |             | TRAINER_CERT...   |
           +-------------------+             +-------------------+
           | PK: Workout_ID    |             | PK: (Trainer_ID,  |
           | FK: Trainer_ID    |             |      Certification)|
           +----+---------+----+             +-------------------+
                |         |
      1:N       |         | N:M (via PARTICIPATES_IN)
  +-------------+         |
  |                       v
  |            +-------------------+             +-------------------+
  |            |  PARTICIPATES_IN  |             |  MEMBER_ADDRESS   |
  |            +-------------------+             +-------------------+
  |            | PK: (Member_ID,   |             | PK: (Member_ID,   |
  |            |      Workout_ID)  |             |      Address)     |
  |            +---------^---------+             +---------^---------+
  |                      |                                 | 1:N
  |                      +----------------+----------------+
  |                                       | 1:N
  |                               +-------+-------+
  |                               |    MEMBER     |
  |                               +---------------+
  |                               | PK: Member_ID |
  |                               +-------+-------+
  |                                       | 1:N
  |         +-----------------------------+---------------------+
  |         | 1:N                                               | 1:N
  |  +------v------+                                     +------v------+
  |  | ATTENDANCE  |                                     | MEMBERSHIP  |
  |  +-------------+                                     +-------------+
  |  | PK: Att_ID  |                                     | PK: Mshp_ID |
  +->| FK: Wk_ID   |                                     | FK: Mem_ID  |
     | FK: Mem_ID  |                                     +------+------+
     +------+------+                                            | 1:N
            | 1:N                                               v
     +------v------+                                     +-------------+
     | ATT_REMARKS |                                     |   PAYMENT   |
     +-------------+                                     +-------------+
     | PK: (Att_ID,|                                     | PK: Pay_ID  |
     |      Remarks|                                     | FK: Mshp_ID |
     +-------------+                                     | FK: Trn_ID  |
                                                         +-------------+
```

### Table Definitions & Keys:

1. **`MEMBER`**:
   - `Member_ID` (INT AUTO_INCREMENT, **Primary Key**)
   - `Name`, `Gender`, `Date_of_Birth`, `Age`, `Phone`, `Email` (UNIQUE), `Emergency_Contact`, `Join_Date`, `Status`, `Blood_Group`
2. **`MEMBER_ADDRESS`** *(Multivalued Address representation)*:
   - `Member_ID` (INT, **Foreign Key** &rarr; `MEMBER.Member_ID`)
   - `Address` (VARCHAR(255))
   - **Composite Primary Key**: `(Member_ID, Address)`
3. **`TRAINER`**:
   - `Trainer_ID` (INT AUTO_INCREMENT, **Primary Key**)
   - `Name`, `Phone`, `Email` (UNIQUE), `Specialization`, `Experience_Years`, `Salary`
4. **`TRAINER_CERTIFICATION`** *(Multivalued Certification representation)*:
   - `Trainer_ID` (INT, **Foreign Key** &rarr; `TRAINER.Trainer_ID`)
   - `Certification` (VARCHAR(100))
   - **Composite Primary Key**: `(Trainer_ID, Certification)`
5. **`WORKOUT`**:
   - `Workout_ID` (INT AUTO_INCREMENT, **Primary Key**)
   - `Workout_Name`, `Description`, `Calories_Burn`, `Duration_Minutes`, `Difficulty_Level`
   - `Trainer_ID` (INT, **Foreign Key** &rarr; `TRAINER.Trainer_ID`, `ON DELETE SET NULL`)
6. **`MEMBERSHIP`**:
   - `Membership_ID` (INT AUTO_INCREMENT, **Primary Key**)
   - `Member_ID` (INT, **Foreign Key** &rarr; `MEMBER.Member_ID`, `ON DELETE CASCADE`)
   - `Plan_Name`, `Plan_Description`, `Start_Date`, `End_Date`, `Amount`, `Status`, `Duration_Days`
7. **`PAYMENT`**:
   - `Payment_ID` (INT AUTO_INCREMENT, **Primary Key**)
   - `Membership_ID` (INT, **Foreign Key** &rarr; `MEMBERSHIP.Membership_ID`)
   - `Trainer_ID` (INT, **Foreign Key** &rarr; `TRAINER.Trainer_ID`)
   - `Amount`, `Payment_Method`, `Payment_Date`, `Due_Date`, `Status`, `Transaction_ID`, `Invoice_Number`
8. **`ATTENDANCE`**:
   - `Attendance_ID` (INT AUTO_INCREMENT, **Primary Key**)
   - `Member_ID` (INT, **Foreign Key** &rarr; `MEMBER.Member_ID`)
   - `Workout_ID` (INT, **Foreign Key** &rarr; `WORKOUT.Workout_ID`)
   - `Date`, `Check_In_Time`, `Check_Out_Time`, `Workout_Duration`
9. **`ATTENDANCE_REMARKS`** *(Multivalued remarks representation)*:
   - `Attendance_ID` (INT, **Foreign Key** &rarr; `ATTENDANCE.Attendance_ID`)
   - `Remarks` (VARCHAR(255))
   - **Composite Primary Key**: `(Attendance_ID, Remarks)`
10. **`PARTICIPATES_IN`** *(Many-to-Many relationship table)*:
    - `Member_ID` (INT, **Foreign Key** &rarr; `MEMBER.Member_ID`)
    - `Workout_ID` (INT, **Foreign Key** &rarr; `WORKOUT.Workout_ID`)
    - **Composite Primary Key**: `(Member_ID, Workout_ID)`

---

## 5. ER Relationships Explanation

| Entity 1 | Cardinality | Entity 2 | Junction / Foreign Key | Practical Real-World Meaning |
| :--- | :---: | :--- | :--- | :--- |
| `MEMBER` | **1 : N** | `MEMBERSHIP` | `MEMBERSHIP.Member_ID` | A member can subscribe to multiple membership terms over time. |
| `MEMBER` | **N : M** | `WORKOUT` | `PARTICIPATES_IN` | A member can participate in multiple workout routines, and each routine has multiple enrolled members. |
| `TRAINER` | **1 : N** | `WORKOUT` | `WORKOUT.Trainer_ID` | A trainer designs and coaches multiple workout routines. |
| `MEMBERSHIP` | **1 : N** | `PAYMENT` | `PAYMENT.Membership_ID` | A membership subscription can have one or more payment transactions/installments. |
| `TRAINER` | **1 : N** | `PAYMENT` | `PAYMENT.Trainer_ID` | Direct personal training commission or session fees paid to a trainer. |
| `MEMBER` | **1 : N** | `ATTENDANCE` | `ATTENDANCE.Member_ID` | A member checks into the gym on various dates. |
| `WORKOUT` | **1 : N** | `ATTENDANCE` | `ATTENDANCE.Workout_ID` | Each attendance log specifies which workout was performed. |
| `ATTENDANCE` | **1 : N** | `ATTENDANCE_REMARKS` | `(Attendance_ID, Remarks)` | Multiple coach observations or notes per attendance session. |
| `MEMBER` | **1 : N** | `MEMBER_ADDRESS` | `(Member_ID, Address)` | A member can register home, office, or permanent addresses. |
| `TRAINER` | **1 : N** | `TRAINER_CERTIFICATION` | `(Trainer_ID, Certification)` | A trainer can hold multiple fitness certifications. |

---

## 6. Installation & Setup Guide

### Prerequisites
- Python 3.10 or higher
- MySQL Server 8.x
- Git (optional)

### Step 1: Clone or Navigate to Project
```bash
cd gym
```

### Step 2: Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database Environment Variables
Create or edit your `.env` file in the project root:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=gym_management
SECRET_KEY=college_dbms_mini_project_secret_key_2025
```
*(Replace `your_mysql_password` with your local MySQL root password.)*

### Step 5: Initialize MySQL Database & Load Sample Data
Run the automated initialization script:
```bash
python init_db.py
```
This script will:
1. Connect to your MySQL server.
2. Execute `CREATE DATABASE IF NOT EXISTS gym_management;`.
3. Run `schema.sql` to build the 10 relational tables with indexes and foreign keys.
4. Run `sample_data.sql` to populate realistic records (10 Members, 5 Addresses, 5 Trainers, 8 Certifications, 10 Workouts, 10 Memberships, 15 Payments, 20 Attendances, 10 Remarks, 15 Participates_In).
5. Print a verification summary.

*(Note: If MySQL is not running or credentials are unavailable, you can test via SQLite fallback using `python init_db.py --sqlite`.)*

### Step 6: Run the Flask Web Application
```bash
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 7. Project Structure

```
gym/
├── app.py                     # Main Flask application entrypoint & error handlers
├── config.py                  # Database & environment configuration
├── init_db.py                 # Automated MySQL/SQLite setup & sample data loader
├── requirements.txt           # Python package dependencies
├── .env.example               # Template environment configuration file
├── .env                       # Active environment credentials (git-ignored)
├── schema.sql                 # MySQL DDL script creating all 10 tables
├── sample_data.sql            # MySQL DML script inserting sample records
├── database_queries.sql       # Demonstration queries for viva/DBMS lab
├── README.md                  # Project documentation & viva guide
│
├── models/                    # SQLAlchemy database models
│   ├── __init__.py            # DB instance and model exports
│   ├── member.py              # Member & MemberAddress models
│   ├── trainer.py             # Trainer & TrainerCertification models
│   ├── workout.py             # Workout & ParticipatesIn models
│   ├── membership.py          # Membership model
│   ├── payment.py             # Payment model
│   └── attendance.py          # Attendance & AttendanceRemarks models
│
├── routes/                    # Flask blueprints (controller routes)
│   ├── __init__.py            # Blueprint registration
│   ├── dashboard.py           # /dashboard metrics & Chart.js aggregates
│   ├── members.py             # /members CRUD & address management
│   ├── trainers.py            # /trainers CRUD & certifications
│   ├── workouts.py            # /workouts CRUD & ParticipatesIn N:M
│   ├── memberships.py         # /memberships CRUD & duration calculation
│   ├── payments.py            # /payments CRUD & tax invoice generator
│   ├── attendance.py          # /attendance CRUD & remarks
│   └── reports.py             # /reports 9 real database reports
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Master layout with responsive navbar & sidebar
│   ├── dashboard.html         # Admin dashboard with stats & charts
│   ├── reports.html           # 9 analytical database reports
│   ├── members/               # Member index, add, edit, show templates
│   ├── trainers/              # Trainer index, add, edit, show templates
│   ├── workouts/              # Workout index, add, edit, show, assign templates
│   ├── memberships/           # Membership index, add, edit, show templates
│   ├── payments/              # Payment index, add, edit, show, invoice templates
│   └── attendance/            # Attendance index, add, edit, show templates
│
└── static/                    # Static assets
    ├── css/
    │   └── style.css          # Bootstrap 5 enhancements & print styles
    └── js/
        └── script.js          # Dynamic input rows & duration calculations
```

---

## 8. Sample Database Queries for Viva & Evaluation

The file [`database_queries.sql`](database_queries.sql) contains full executable queries. Below are key highlights demonstrating required DBMS syllabus topics:

### 1. Inner Join: Members & Current Subscriptions
```sql
SELECT 
    m.Member_ID, m.Name, m.Phone, 
    ms.Plan_Name, ms.Start_Date, ms.End_Date, ms.Amount
FROM MEMBER m
INNER JOIN MEMBERSHIP ms ON m.Member_ID = ms.Member_ID
WHERE ms.Status = 'Active';
```

### 2. Many-to-Many (`N:M`) Join: Member Workout Participation
```sql
SELECT 
    m.Name AS Member_Name, 
    w.Workout_Name, 
    w.Difficulty_Level,
    t.Name AS Trainer_Name
FROM MEMBER m
INNER JOIN PARTICIPATES_IN p ON m.Member_ID = p.Member_ID
INNER JOIN WORKOUT w ON p.Workout_ID = w.Workout_ID
LEFT JOIN TRAINER t ON w.Trainer_ID = t.Trainer_ID;
```

### 3. Aggregate Functions with `GROUP BY` and `HAVING`
```sql
SELECT 
    Plan_Name,
    COUNT(Membership_ID) AS Total_Subscribers,
    SUM(Amount) AS Total_Revenue,
    AVG(Amount) AS Average_Amount
FROM MEMBERSHIP
GROUP BY Plan_Name
HAVING Total_Revenue > 10000;
```

### 4. Correlated Subquery
```sql
SELECT m.Member_ID, m.Name
FROM MEMBER m
WHERE (
    SELECT SUM(a.Workout_Duration) 
    FROM ATTENDANCE a 
    WHERE a.Member_ID = m.Member_ID
) > (SELECT AVG(Workout_Duration) FROM ATTENDANCE);
```

---

## 9. Screenshot Placeholders for Project Report

- `[Screenshot 1: Admin Dashboard with Real-Time Counters & Chart.js Visualizations]`
- `[Screenshot 2: Member Management with Search and Multivalued Addresses]`
- `[Screenshot 3: Member Profile showing Participated Workouts and Attendance]`
- `[Screenshot 4: Workout Routine Definition and Trainer Relational Dropdown]`
- `[Screenshot 5: Many-to-Many Workout Participation Assignment Interface]`
- `[Screenshot 6: Membership Creation with Automatic Duration Calculation]`
- `[Screenshot 7: Printable Official Tax Invoice View]`
- `[Screenshot 8: Daily Attendance Logs with Check-in Duration & Remarks]`
- `[Screenshot 9: Analytical Database Reports Page with 9 Pre-Built Reports]`

---

## 10. Architecture Summary

- **Backend**: Python 3.x with Flask framework
- **Database**: Relational Database with SQLAlchemy ORM
- **Frontend**: Bootstrap 5 with responsive CSS and JavaScript
- **Security**: Session-based authentication with role-based access control (Admin & Member)
