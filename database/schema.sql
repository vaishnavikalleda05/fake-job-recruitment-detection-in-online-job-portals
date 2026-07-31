-- ===========================================================
-- Fake Job Detection in Online Portals
-- Database Schema
-- Author: Kalleda Vaishnavi
-- ===========================================================

-- Drop database if already exists
DROP DATABASE IF EXISTS fake_job_detection;

-- Create Database
CREATE DATABASE fake_job_detection;

USE fake_job_detection;

-- ===========================================================
-- Table 1 : Users
-- ===========================================================

CREATE TABLE users (

    user_id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(120) UNIQUE NOT NULL,

    password_hash VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- ===========================================================
-- Table 2 : Jobs
-- Stores all uploaded / analysed jobs
-- ===========================================================

CREATE TABLE jobs (

    job_id INT AUTO_INCREMENT PRIMARY KEY,

    company_name VARCHAR(150),

    job_title VARCHAR(200) NOT NULL,

    location VARCHAR(150),

    salary_range VARCHAR(100),

    employment_type VARCHAR(50),

    required_experience VARCHAR(100),

    required_education VARCHAR(100),

    industry VARCHAR(100),

    company_profile TEXT,

    job_description LONGTEXT,

    requirements TEXT,

    benefits TEXT,

    contact_email VARCHAR(150),

    contact_phone VARCHAR(30),

    has_company_logo BOOLEAN DEFAULT FALSE,

    has_questions BOOLEAN DEFAULT FALSE,

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- ===========================================================
-- Table 3 : Predictions
-- Stores ML Prediction Results
-- ===========================================================

CREATE TABLE predictions (

    prediction_id INT AUTO_INCREMENT PRIMARY KEY,

    job_id INT NOT NULL,

    prediction ENUM('Real','Fake','Suspicious') NOT NULL,

    risk_score DECIMAL(5,2),

    ml_probability DECIMAL(5,2),

    rule_score DECIMAL(5,2),

    predicted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(job_id)
    REFERENCES jobs(job_id)
    ON DELETE CASCADE

);

-- ===========================================================
-- Table 4 : Fraud Rules Triggered
-- Stores which rules were triggered
-- ===========================================================

CREATE TABLE fraud_rules (

    rule_id INT AUTO_INCREMENT PRIMARY KEY,

    job_id INT,

    rule_name VARCHAR(200),

    severity ENUM('LOW','MEDIUM','HIGH'),

    description TEXT,

    FOREIGN KEY(job_id)
    REFERENCES jobs(job_id)
    ON DELETE CASCADE

);

-- ===========================================================
-- Table 5 : User Reports
-- User manually reports suspicious jobs
-- ===========================================================

CREATE TABLE reports (

    report_id INT AUTO_INCREMENT PRIMARY KEY,

    job_id INT,

    user_id INT,

    report_reason VARCHAR(255),

    comments TEXT,

    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(job_id)
    REFERENCES jobs(job_id)
    ON DELETE CASCADE,

    FOREIGN KEY(user_id)
    REFERENCES users(user_id)
    ON DELETE SET NULL

);

-- ===========================================================
-- Table 6 : Prediction History
-- Keeps track of all analyses
-- ===========================================================

CREATE TABLE prediction_history (

    history_id INT AUTO_INCREMENT PRIMARY KEY,

    job_id INT,

    prediction_id INT,

    analysed_by VARCHAR(100),

    analysed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(job_id)
    REFERENCES jobs(job_id)
    ON DELETE CASCADE,

    FOREIGN KEY(prediction_id)
    REFERENCES predictions(prediction_id)
    ON DELETE CASCADE

);

-- ===========================================================
-- Indexes
-- ===========================================================

CREATE INDEX idx_company
ON jobs(company_name);

CREATE INDEX idx_location
ON jobs(location);

CREATE INDEX idx_prediction
ON predictions(prediction);

CREATE INDEX idx_risk
ON predictions(risk_score);

CREATE INDEX idx_email
ON jobs(contact_email);

-- ===========================================================
-- Views
-- ===========================================================

CREATE VIEW fake_jobs AS

SELECT

j.job_id,
j.company_name,
j.job_title,
j.location,
p.prediction,
p.risk_score

FROM jobs j

JOIN predictions p

ON j.job_id = p.job_id

WHERE p.prediction='Fake';

-- ===========================================================

CREATE VIEW high_risk_jobs AS

SELECT

j.job_title,
j.company_name,
p.risk_score

FROM jobs j

JOIN predictions p

ON j.job_id=p.job_id

WHERE p.risk_score>=80;

-- ===========================================================

CREATE VIEW suspicious_jobs AS

SELECT

j.job_title,
j.company_name,
p.risk_score

FROM jobs j

JOIN predictions p

ON j.job_id=p.job_id

WHERE p.prediction='Suspicious';

-- ===========================================================
-- Procedure
-- Returns total fake jobs
-- ===========================================================

DELIMITER $$

CREATE PROCEDURE TotalFakeJobs()

BEGIN

SELECT COUNT(*) AS Total_Fake_Jobs

FROM predictions

WHERE prediction='Fake';

END $$

DELIMITER ;

-- ===========================================================
-- Procedure
-- Average Risk Score
-- ===========================================================

DELIMITER $$

CREATE PROCEDURE AverageRisk()

BEGIN

SELECT AVG(risk_score)

AS Average_Risk

FROM predictions;

END $$

DELIMITER ;

-- ===========================================================
-- Trigger
-- Prevent invalid Risk Score
-- ===========================================================

DELIMITER $$

CREATE TRIGGER check_risk_score

BEFORE INSERT

ON predictions

FOR EACH ROW

BEGIN

IF NEW.risk_score <0 OR NEW.risk_score>100 THEN

SIGNAL SQLSTATE '45000'

SET MESSAGE_TEXT='Risk Score must be between 0 and 100';

END IF;

END $$

DELIMITER ;

-- ===========================================================
-- Trigger
-- Automatically create prediction history
-- ===========================================================

DELIMITER $$

CREATE TRIGGER prediction_history_trigger

AFTER INSERT

ON predictions

FOR EACH ROW

BEGIN

INSERT INTO prediction_history

(job_id,prediction_id,analysed_by)

VALUES

(NEW.job_id,NEW.prediction_id,'System');

END $$

DELIMITER ;

-- ===========================================================
-- End of Schema
-- ===========================================================