

CREATE DATABASE IF NOT EXISTS gym_management;
USE gym_management;

DROP TABLE IF EXISTS PARTICIPATES_IN;
DROP TABLE IF EXISTS ATTENDANCE_REMARKS;
DROP TABLE IF EXISTS ATTENDANCE;
DROP TABLE IF EXISTS PAYMENT;
DROP TABLE IF EXISTS MEMBERSHIP;
DROP TABLE IF EXISTS WORKOUT;
DROP TABLE IF EXISTS TRAINER_CERTIFICATION;
DROP TABLE IF EXISTS TRAINER;
DROP TABLE IF EXISTS MEMBER_ADDRESS;
DROP TABLE IF EXISTS MEMBER;


CREATE TABLE MEMBER (
    Member_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Gender ENUM('Male', 'Female', 'Other') NOT NULL,
    Date_of_Birth DATE NOT NULL,
    Age INT NOT NULL,
    Phone VARCHAR(15) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Emergency_Contact VARCHAR(15) NOT NULL,
    Join_Date DATE NOT NULL,
    Status ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    Blood_Group VARCHAR(5) NOT NULL,
    Password VARCHAR(255) DEFAULT 'member123',
    INDEX idx_member_name (Name),
    INDEX idx_member_phone (Phone),
    INDEX idx_member_status (Status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE MEMBER_ADDRESS (
    Member_ID INT NOT NULL,
    Address VARCHAR(255) NOT NULL,
    PRIMARY KEY (Member_ID, Address),
    CONSTRAINT fk_member_address_member
        FOREIGN KEY (Member_ID) REFERENCES MEMBER (Member_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE TRAINER (
    Trainer_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Phone VARCHAR(15) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Specialization VARCHAR(100) NOT NULL,
    Experience_Years INT NOT NULL DEFAULT 0,
    Salary DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    INDEX idx_trainer_name (Name),
    INDEX idx_trainer_specialization (Specialization)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE TRAINER_CERTIFICATION (
    Trainer_ID INT NOT NULL,
    Certification VARCHAR(100) NOT NULL,
    PRIMARY KEY (Trainer_ID, Certification),
    CONSTRAINT fk_trainer_cert_trainer
        FOREIGN KEY (Trainer_ID) REFERENCES TRAINER (Trainer_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE WORKOUT (
    Workout_ID INT AUTO_INCREMENT PRIMARY KEY,
    Workout_Name VARCHAR(100) NOT NULL,
    Description TEXT,
    Calories_Burn INT NOT NULL DEFAULT 0,
    Duration_Minutes INT NOT NULL DEFAULT 0,
    Difficulty_Level ENUM('Easy', 'Medium', 'Hard') NOT NULL DEFAULT 'Medium',
    Trainer_ID INT NULL,
    INDEX idx_workout_name (Workout_Name),
    INDEX idx_workout_difficulty (Difficulty_Level),
    CONSTRAINT fk_workout_trainer
        FOREIGN KEY (Trainer_ID) REFERENCES TRAINER (Trainer_ID)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE MEMBERSHIP (
    Membership_ID INT AUTO_INCREMENT PRIMARY KEY,
    Member_ID INT NOT NULL,
    Plan_Name ENUM('Monthly', 'Quarterly', 'Half-Yearly', 'Yearly') NOT NULL,
    Plan_Description TEXT,
    Start_Date DATE NOT NULL,
    End_Date DATE NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    Status ENUM('Active', 'Expired') NOT NULL DEFAULT 'Active',
    Duration_Days INT NOT NULL DEFAULT 0,
    INDEX idx_membership_status (Status),
    INDEX idx_membership_plan (Plan_Name),
    CONSTRAINT fk_membership_member
        FOREIGN KEY (Member_ID) REFERENCES MEMBER (Member_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE PAYMENT (
    Payment_ID INT AUTO_INCREMENT PRIMARY KEY,
    Membership_ID INT NULL,
    Trainer_ID INT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    Payment_Method ENUM('Cash', 'Card', 'UPI', 'NetBanking') NOT NULL,
    Payment_Date DATE NOT NULL,
    Due_Date DATE NULL,
    Status ENUM('Success', 'Pending', 'Failed') NOT NULL DEFAULT 'Success',
    Transaction_ID VARCHAR(100) NULL UNIQUE,
    Invoice_Number VARCHAR(50) NOT NULL UNIQUE,
    INDEX idx_payment_date (Payment_Date),
    INDEX idx_payment_status (Status),
    CONSTRAINT fk_payment_membership
        FOREIGN KEY (Membership_ID) REFERENCES MEMBERSHIP (Membership_ID)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_payment_trainer
        FOREIGN KEY (Trainer_ID) REFERENCES TRAINER (Trainer_ID)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE ATTENDANCE (
    Attendance_ID INT AUTO_INCREMENT PRIMARY KEY,
    Member_ID INT NOT NULL,
    Workout_ID INT NOT NULL,
    Date DATE NOT NULL,
    Check_In_Time TIME NOT NULL,
    Check_Out_Time TIME NULL,
    Workout_Duration INT NOT NULL DEFAULT 0,
    INDEX idx_attendance_date (Date),
    CONSTRAINT fk_attendance_member
        FOREIGN KEY (Member_ID) REFERENCES MEMBER (Member_ID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_attendance_workout
        FOREIGN KEY (Workout_ID) REFERENCES WORKOUT (Workout_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE ATTENDANCE_REMARKS (
    Attendance_ID INT NOT NULL,
    Remarks VARCHAR(255) NOT NULL,
    PRIMARY KEY (Attendance_ID, Remarks),
    CONSTRAINT fk_remarks_attendance
        FOREIGN KEY (Attendance_ID) REFERENCES ATTENDANCE (Attendance_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE PARTICIPATES_IN (
    Member_ID INT NOT NULL,
    Workout_ID INT NOT NULL,
    PRIMARY KEY (Member_ID, Workout_ID),
    CONSTRAINT fk_participates_member
        FOREIGN KEY (Member_ID) REFERENCES MEMBER (Member_ID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_participates_workout
        FOREIGN KEY (Workout_ID) REFERENCES WORKOUT (Workout_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
