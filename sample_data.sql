

USE gym_management;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE ATTENDANCE_REMARKS;
TRUNCATE TABLE ATTENDANCE;
TRUNCATE TABLE PARTICIPATES_IN;
TRUNCATE TABLE PAYMENT;
TRUNCATE TABLE MEMBERSHIP;
TRUNCATE TABLE WORKOUT;
TRUNCATE TABLE TRAINER_CERTIFICATION;
TRUNCATE TABLE TRAINER;
TRUNCATE TABLE MEMBER_ADDRESS;
TRUNCATE TABLE MEMBER;
SET FOREIGN_KEY_CHECKS = 1;


INSERT INTO MEMBER (Member_ID, Name, Gender, Date_of_Birth, Age, Phone, Email, Emergency_Contact, Join_Date, Status, Blood_Group) VALUES
(1, 'Rahul Sharma', 'Male', '1998-05-14', 28, '9876543210', 'rahul.sharma@gmail.com', '9876543200', '2025-01-10', 'Active', 'O+'),
(2, 'Priya Patel', 'Female', '2001-08-22', 25, '9812345678', 'priya.patel@gmail.com', '9812345600', '2025-02-01', 'Active', 'B+'),
(3, 'Amit Verma', 'Male', '1995-11-30', 31, '9823456789', 'amit.verma@yahoo.com', '9823456700', '2025-03-15', 'Active', 'A+'),
(4, 'Sneha Rao', 'Female', '2002-03-19', 24, '9834567890', 'sneha.rao@outlook.com', '9834567800', '2025-04-10', 'Active', 'AB+'),
(5, 'Vikram Singh', 'Male', '1992-07-25', 34, '9845678901', 'vikram.singh@gmail.com', '9845678900', '2025-05-05', 'Inactive', 'O-'),
(6, 'Ananya Iyer', 'Female', '2000-09-12', 26, '9856789012', 'ananya.iyer@gmail.com', '9856789000', '2025-06-20', 'Active', 'B-'),
(7, 'Rohan Gupta', 'Male', '1999-12-05', 27, '9867890123', 'rohan.gupta@hotmail.com', '9867890100', '2025-07-11', 'Active', 'A-'),
(8, 'Kavita Reddy', 'Female', '1997-04-18', 29, '9878901234', 'kavita.reddy@gmail.com', '9878901200', '2025-08-01', 'Active', 'O+'),
(9, 'Arjun Nair', 'Male', '1994-01-29', 32, '9889012345', 'arjun.nair@gmail.com', '9889012300', '2025-09-15', 'Active', 'B+'),
(10, 'Pooja Joshi', 'Female', '2003-06-15', 23, '9890123456', 'pooja.joshi@gmail.com', '9890123400', '2025-10-01', 'Active', 'AB-');


INSERT INTO MEMBER_ADDRESS (Member_ID, Address) VALUES
(1, 'Flat 402, Sunshine Heights, MG Road, Bengaluru'),
(2, 'House No. 12, Rose Villa, Indiranagar, Bengaluru'),
(2, 'Office: 5th Floor, Cyber Park, Electronic City, Bengaluru'),
(3, 'B-304, Green Meadows, Whitefield, Bengaluru'),
(4, 'Plot 88, 3rd Cross, Koramangala 4th Block, Bengaluru');


INSERT INTO TRAINER (Trainer_ID, Name, Phone, Email, Specialization, Experience_Years, Salary) VALUES
(1, 'Karan Malhotra', '9711122233', 'karan.trainer@gym.com', 'Bodybuilding & Hypertrophy', 7, 55000.00),
(2, 'Deepika Sen', '9722233344', 'deepika.sen@gym.com', 'CrossFit & Functional Training', 5, 48000.00),
(3, 'Manoj Kumar', '9733344455', 'manoj.kumar@gym.com', 'Cardio & Weight Loss', 6, 50000.00),
(4, 'Pooja Hegde', '9744455566', 'pooja.hegde@gym.com', 'Yoga & Flexibility', 4, 42000.00),
(5, 'Suresh Raina', '9755566677', 'suresh.raina@gym.com', 'Strength & Powerlifting', 8, 60000.00);


INSERT INTO TRAINER_CERTIFICATION (Trainer_ID, Certification) VALUES
(1, 'ACE Certified Personal Trainer'),
(1, 'ISSA Strength and Conditioning Specialist'),
(2, 'CrossFit Level 2 Trainer'),
(2, 'Kettlebell Master Instructor'),
(3, 'NSCA Certified Cardio Specialist'),
(4, 'Registered Yoga Teacher (RYT 500)'),
(4, 'Pilates Mat Certification'),
(5, 'IPF Level 1 Powerlifting Coach');


INSERT INTO WORKOUT (Workout_ID, Workout_Name, Description, Calories_Burn, Duration_Minutes, Difficulty_Level, Trainer_ID) VALUES
(1, 'Chest & Triceps Blast', 'Heavy barbell presses and tricep supersets for muscle hypertrophy', 450, 60, 'Hard', 1),
(2, 'Back & Biceps Annihilation', 'Deadlifts, pull-ups and bent-over rows for back thickness', 480, 60, 'Hard', 1),
(3, 'Leg Day Destroyer', 'High intensity squats, leg presses, lunges and calf raises', 600, 75, 'Hard', 5),
(4, 'High Intensity CrossFit', 'Metabolic conditioning circuits combining box jumps, burpees and cleans', 550, 45, 'Hard', 2),
(5, 'Kettlebell Core Conditioning', 'Full body kettlebell flows focusing on core strength and balance', 380, 40, 'Medium', 2),
(6, 'Fat Burn HIIT Cardio', 'Tabata style treadmill sprints and rowing intervals', 500, 45, 'Medium', 3),
(7, 'Low Impact Aerobics', 'Steady state cycling and brisk elliptical cardio for endurance', 320, 50, 'Easy', 3),
(8, 'Power Yoga & Stretch', 'Vinyasa flow sequence focusing on posture, breath and mobility', 220, 60, 'Easy', 4),
(9, 'Pilates Mat Sculpt', 'Core stabilization and spine alignment mat workout', 260, 45, 'Easy', 4),
(10, 'Olympic Powerlifting Prep', 'Technique drills for snatch, clean & jerk and power pulls', 520, 70, 'Medium', 5);

INSERT INTO MEMBERSHIP (Membership_ID, Member_ID, Plan_Name, Plan_Description, Start_Date, End_Date, Amount, Status, Duration_Days) VALUES
(1, 1, 'Yearly', 'Full gym access + locker + 2 personal training sessions/month', '2025-01-10', '2026-01-10', 18000.00, 'Active', 365),
(2, 2, 'Half-Yearly', 'Full access to weight room and cardio equipment', '2025-02-01', '2025-08-01', 10500.00, 'Expired', 181),
(3, 3, 'Quarterly', 'Peak hours access with group fitness classes', '2025-03-15', '2025-06-15', 6000.00, 'Expired', 92),
(4, 4, 'Monthly', 'Standard monthly workout access with gym floor support', '2025-09-01', '2025-10-01', 2500.00, 'Active', 30),
(5, 5, 'Quarterly', 'Off-peak membership plan', '2025-05-05', '2025-08-05', 5500.00, 'Expired', 92),
(6, 6, 'Yearly', 'VIP membership: 24/7 access, sauna, all classes included', '2025-06-20', '2026-06-20', 20000.00, 'Active', 365),
(7, 7, 'Half-Yearly', 'Standard semester fitness plan with locker facility', '2025-07-11', '2026-01-11', 11000.00, 'Active', 184),
(8, 8, 'Monthly', 'Trial monthly access with fitness assessment', '2025-09-10', '2025-10-10', 2500.00, 'Active', 30),
(9, 9, 'Yearly', 'Annual strength athlete pass with unlimited coach access', '2025-09-15', '2026-09-15', 19000.00, 'Active', 365),
(10, 10, 'Quarterly', 'Student discount quarterly fitness package', '2025-10-01', '2026-01-01', 5000.00, 'Active', 92);


INSERT INTO PAYMENT (Payment_ID, Membership_ID, Trainer_ID, Amount, Payment_Method, Payment_Date, Due_Date, Status, Transaction_ID, Invoice_Number) VALUES
(1, 1, 1, 18000.00, 'Card', '2025-01-10', '2025-01-10', 'Success', 'TXN-20250110-001', 'INV-2025-001'),
(2, 2, 2, 10500.00, 'UPI', '2025-02-01', '2025-02-01', 'Success', 'TXN-20250201-002', 'INV-2025-002'),
(3, 3, 3, 6000.00, 'Cash', '2025-03-15', '2025-03-15', 'Success', 'TXN-20250315-003', 'INV-2025-003'),
(4, 4, 4, 2500.00, 'UPI', '2025-09-01', '2025-09-01', 'Success', 'TXN-20250901-004', 'INV-2025-004'),
(5, 5, 5, 5500.00, 'NetBanking', '2025-05-05', '2025-05-05', 'Success', 'TXN-20250505-005', 'INV-2025-005'),
(6, 6, 1, 20000.00, 'Card', '2025-06-20', '2025-06-20', 'Success', 'TXN-20250620-006', 'INV-2025-006'),
(7, 7, 2, 11000.00, 'UPI', '2025-07-11', '2025-07-11', 'Success', 'TXN-20250711-007', 'INV-2025-007'),
(8, 8, 4, 2500.00, 'Cash', '2025-09-10', '2025-09-10', 'Success', 'TXN-20250910-008', 'INV-2025-008'),
(9, 9, 5, 19000.00, 'NetBanking', '2025-09-15', '2025-09-15', 'Success', 'TXN-20250915-009', 'INV-2025-009'),
(10, 10, 3, 5000.00, 'UPI', '2025-10-01', '2025-10-01', 'Success', 'TXN-20251001-010', 'INV-2025-010'),
(11, 4, 4, 2500.00, 'UPI', '2025-10-02', '2025-10-05', 'Pending', 'TXN-20251002-011', 'INV-2025-011'),
(12, 1, 1, 1500.00, 'Card', '2025-04-12', '2025-04-12', 'Success', 'TXN-20250412-012', 'INV-2025-012'),
(13, 2, 2, 2000.00, 'NetBanking', '2025-05-18', '2025-05-20', 'Failed', 'TXN-20250518-013', 'INV-2025-013'),
(14, 7, 3, 1200.00, 'UPI', '2025-08-25', '2025-08-25', 'Success', 'TXN-20250825-014', 'INV-2025-014'),
(15, 10, 5, 2500.00, 'Cash', '2025-10-04', '2025-10-10', 'Pending', 'TXN-20251004-015', 'INV-2025-015');


INSERT INTO ATTENDANCE (Attendance_ID, Member_ID, Workout_ID, Date, Check_In_Time, Check_Out_Time, Workout_Duration) VALUES
(1, 1, 1, '2025-10-01', '06:00:00', '07:15:00', 75),
(2, 2, 4, '2025-10-01', '07:30:00', '08:20:00', 50),
(3, 3, 6, '2025-10-01', '17:00:00', '17:55:00', 55),
(4, 4, 8, '2025-10-01', '18:15:00', '19:20:00', 65),
(5, 6, 2, '2025-10-02', '06:30:00', '07:45:00', 75),
(6, 7, 3, '2025-10-02', '07:00:00', '08:20:00', 80),
(7, 8, 7, '2025-10-02', '16:45:00', '17:35:00', 50),
(8, 9, 10, '2025-10-02', '18:00:00', '19:15:00', 75),
(9, 1, 2, '2025-10-03', '06:10:00', '07:15:00', 65),
(10, 2, 5, '2025-10-03', '07:45:00', '08:35:00', 50),
(11, 4, 9, '2025-10-03', '17:15:00', '18:05:00', 50),
(12, 10, 6, '2025-10-03', '18:30:00', '19:20:00', 50),
(13, 6, 1, '2025-10-04', '06:00:00', '07:10:00', 70),
(14, 7, 4, '2025-10-04', '07:30:00', '08:25:00', 55),
(15, 8, 8, '2025-10-04', '17:00:00', '18:00:00', 60),
(16, 9, 3, '2025-10-04', '18:10:00', '19:35:00', 85),
(17, 1, 3, '2025-10-05', '06:15:00', '07:35:00', 80),
(18, 2, 4, '2025-10-05', '07:20:00', '08:10:00', 50),
(19, 3, 6, '2025-10-05', '17:30:00', '18:25:00', 55),
(20, 10, 8, '2025-10-05', '18:00:00', '19:05:00', 65);


INSERT INTO ATTENDANCE_REMARKS (Attendance_ID, Remarks) VALUES
(1, 'Great energy and completed all working sets for bench press.'),
(2, 'Struggled on box jumps; advised knee warmup.'),
(3, 'Cardio heart rate maintained above 140 bpm target.'),
(4, 'Improved shoulder flexibility significantly.'),
(5, 'Form correction advised on heavy barbell rows.'),
(6, 'Squats form was pristine; hit PR on final set.'),
(7, 'Completed brisk aerobic walking session without fatigue.'),
(8, 'Clean and jerk technique improved.'),
(16, 'High volume leg training; reported slight soreness in quads.'),
(17, 'Great endurance today; finished workout within target time.');


INSERT INTO PARTICIPATES_IN (Member_ID, Workout_ID) VALUES
(1, 1),
(1, 2),
(1, 3),
(2, 4),
(2, 5),
(3, 6),
(4, 8),
(4, 9),
(6, 1),
(6, 2),
(7, 3),
(7, 4),
(8, 7),
(8, 8),
(9, 3);
