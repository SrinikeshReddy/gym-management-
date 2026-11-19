-- =============================================================================
-- GYM MANAGEMENT SYSTEM - SQL QUERIES & ANALYTICS
-- =============================================================================

USE gym_management;

-- -----------------------------------------------------------------------------
-- 1. BASIC SELECT with WHERE and ORDER BY
-- Retrieve all active members ordered by their join date (newest first)
-- -----------------------------------------------------------------------------
SELECT 
    Member_ID, 
    Name, 
    Gender, 
    Age, 
    Phone, 
    Email, 
    Blood_Group, 
    Join_Date
FROM MEMBER
WHERE Status = 'Active'
ORDER BY Join_Date DESC;

-- -----------------------------------------------------------------------------
-- 2. INNER JOIN (MEMBER and MEMBERSHIP)
-- List each member along with their current membership plan and amount
-- -----------------------------------------------------------------------------
SELECT 
    m.Member_ID,
    m.Name,
    m.Phone,
    ms.Plan_Name,
    ms.Start_Date,
    ms.End_Date,
    ms.Amount,
    ms.Status AS Membership_Status
FROM MEMBER m
INNER JOIN MEMBERSHIP ms ON m.Member_ID = ms.Member_ID
ORDER BY ms.Start_Date DESC;

-- -----------------------------------------------------------------------------
-- 3. LEFT JOIN (TRAINER and WORKOUT)
-- Show all trainers and the workouts they manage (including trainers with no workouts)
-- -----------------------------------------------------------------------------
SELECT 
    t.Trainer_ID,
    t.Name AS Trainer_Name,
    t.Specialization,
    w.Workout_ID,
    w.Workout_Name,
    w.Difficulty_Level,
    w.Calories_Burn
FROM TRAINER t
LEFT JOIN WORKOUT w ON t.Trainer_ID = w.Trainer_ID
ORDER BY t.Trainer_ID, w.Workout_Name;

-- -----------------------------------------------------------------------------
-- 4. AGGREGATE FUNCTIONS (COUNT, SUM, AVG, MIN, MAX)
-- Calculate overall payment metrics for successful transactions
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(Payment_ID) AS Total_Transactions,
    SUM(Amount) AS Total_Revenue,
    AVG(Amount) AS Average_Payment,
    MIN(Amount) AS Minimum_Payment,
    MAX(Amount) AS Maximum_Payment
FROM PAYMENT
WHERE Status = 'Success';

-- -----------------------------------------------------------------------------
-- 5. GROUP BY with COUNT and SUM
-- Total revenue and count of payments grouped by payment method
-- -----------------------------------------------------------------------------
SELECT 
    Payment_Method,
    COUNT(*) AS Transaction_Count,
    SUM(Amount) AS Total_Collected
FROM PAYMENT
WHERE Status = 'Success'
GROUP BY Payment_Method
ORDER BY Total_Collected DESC;

-- -----------------------------------------------------------------------------
-- 6. GROUP BY with HAVING Clause
-- Find membership plans that generated more than 10,000 in total revenue
-- -----------------------------------------------------------------------------
SELECT 
    Plan_Name,
    COUNT(Membership_ID) AS Total_Subscribers,
    SUM(Amount) AS Plan_Revenue
FROM MEMBERSHIP
GROUP BY Plan_Name
HAVING Plan_Revenue > 10000
ORDER BY Plan_Revenue DESC;

-- -----------------------------------------------------------------------------
-- 7. MULTI-TABLE JOIN (N:M Relationship: MEMBER - PARTICIPATES_IN - WORKOUT)
-- Retrieve which member is enrolled in which workout routine
-- -----------------------------------------------------------------------------
SELECT 
    m.Member_ID,
    m.Name AS Member_Name,
    w.Workout_ID,
    w.Workout_Name,
    w.Difficulty_Level,
    t.Name AS Trainer_In_Charge
FROM MEMBER m
INNER JOIN PARTICIPATES_IN p ON m.Member_ID = p.Member_ID
INNER JOIN WORKOUT w ON p.Workout_ID = w.Workout_ID
LEFT JOIN TRAINER t ON w.Trainer_ID = t.Trainer_ID
ORDER BY m.Name, w.Workout_Name;

-- -----------------------------------------------------------------------------
-- 8. COMPOSITE KEY & 1:N MULTIVALUED JOIN (MEMBER and MEMBER_ADDRESS)
-- Display all registered addresses for each member
-- -----------------------------------------------------------------------------
SELECT 
    m.Member_ID,
    m.Name,
    m.Phone,
    ma.Address
FROM MEMBER m
INNER JOIN MEMBER_ADDRESS ma ON m.Member_ID = ma.Member_ID
ORDER BY m.Member_ID;

-- -----------------------------------------------------------------------------
-- 9. TRAINER & CERTIFICATIONS (1:N Multivalued relationship)
-- Display trainers with all their earned fitness certifications
-- -----------------------------------------------------------------------------
SELECT 
    t.Trainer_ID,
    t.Name,
    t.Specialization,
    tc.Certification
FROM TRAINER t
INNER JOIN TRAINER_CERTIFICATION tc ON t.Trainer_ID = tc.Trainer_ID
ORDER BY t.Name;

-- -----------------------------------------------------------------------------
-- 10. ATTENDANCE WITH REMARKS (1:N Relationship)
-- Daily attendance log joined with member, workout and coach remarks
-- -----------------------------------------------------------------------------
SELECT 
    a.Attendance_ID,
    a.Date,
    m.Name AS Member_Name,
    w.Workout_Name,
    a.Check_In_Time,
    a.Check_Out_Time,
    a.Workout_Duration AS Duration_Minutes,
    ar.Remarks
FROM ATTENDANCE a
INNER JOIN MEMBER m ON a.Member_ID = m.Member_ID
INNER JOIN WORKOUT w ON a.Workout_ID = w.Workout_ID
LEFT JOIN ATTENDANCE_REMARKS ar ON a.Attendance_ID = ar.Attendance_ID
ORDER BY a.Date DESC, a.Check_In_Time DESC;

-- -----------------------------------------------------------------------------
-- 11. SUBQUERY (Single-row Subquery)
-- Find the trainer(s) who earn the highest salary in the gym
-- -----------------------------------------------------------------------------
SELECT 
    Trainer_ID, 
    Name, 
    Specialization, 
    Salary
FROM TRAINER
WHERE Salary = (SELECT MAX(Salary) FROM TRAINER);

-- -----------------------------------------------------------------------------
-- 12. SUBQUERY with IN (Multi-row Subquery)
-- Find members who have never attended any workout
-- -----------------------------------------------------------------------------
SELECT 
    Member_ID, 
    Name, 
    Phone, 
    Join_Date
FROM MEMBER
WHERE Member_ID NOT IN (SELECT DISTINCT Member_ID FROM ATTENDANCE);

-- -----------------------------------------------------------------------------
-- 13. CORRELATED SUBQUERY
-- Find members whose total workout duration is greater than the average workout duration
-- -----------------------------------------------------------------------------
SELECT 
    m.Member_ID,
    m.Name,
    (SELECT SUM(a.Workout_Duration) 
     FROM ATTENDANCE a 
     WHERE a.Member_ID = m.Member_ID) AS Total_Workout_Minutes
FROM MEMBER m
WHERE (SELECT SUM(a.Workout_Duration) 
       FROM ATTENDANCE a 
       WHERE a.Member_ID = m.Member_ID) > (SELECT AVG(Workout_Duration) FROM ATTENDANCE);

-- -----------------------------------------------------------------------------
-- 14. COMPLEX REPORT: Trainer Workload Report
-- Number of workouts assigned and total members coached per trainer
-- -----------------------------------------------------------------------------
SELECT 
    t.Trainer_ID,
    t.Name AS Trainer_Name,
    t.Specialization,
    COUNT(DISTINCT w.Workout_ID) AS Workouts_Assigned,
    COUNT(DISTINCT p.Member_ID) AS Total_Members_Trained
FROM TRAINER t
LEFT JOIN WORKOUT w ON t.Trainer_ID = w.Trainer_ID
LEFT JOIN PARTICIPATES_IN p ON w.Workout_ID = p.Workout_ID
GROUP BY t.Trainer_ID, t.Name, t.Specialization
ORDER BY Total_Members_Trained DESC;
