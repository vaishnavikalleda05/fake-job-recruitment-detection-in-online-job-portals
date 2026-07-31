-- ===========================================================
-- Fake Job Detection in Online Portals
-- Sample Data
-- ===========================================================

USE fake_job_detection;

-- ===========================================================
-- USERS
-- ===========================================================

INSERT INTO users
(full_name,email,password_hash)
VALUES

('Vaishnavi Kalleda',
'vaishnavi@gmail.com',
'hashed_password'),

('Admin',
'admin@fakejobdetector.com',
'admin_password');

-- ===========================================================
-- JOBS
-- ===========================================================

INSERT INTO jobs
(
company_name,
job_title,
location,
salary_range,
employment_type,
required_experience,
required_education,
industry,
company_profile,
job_description,
requirements,
benefits,
contact_email,
contact_phone,
has_company_logo,
has_questions
)

VALUES

(
'Infosys',
'Python Developer',
'Hyderabad',
'6 LPA - 8 LPA',
'Full-Time',
'1-3 Years',
'B.Tech',
'IT Services',
'Leading IT company',
'Develop scalable Python applications.',
'Python, SQL, Flask',
'Medical Insurance',
'hr@infosys.com',
'9876543210',
TRUE,
TRUE
),

(
'TCS',
'Data Analyst',
'Bangalore',
'5 LPA - 7 LPA',
'Full-Time',
'Fresher',
'B.Tech',
'IT Services',
'Tata Consultancy Services',
'Analyse business data and create reports.',
'Python, SQL',
'Health Insurance',
'careers@tcs.com',
'9123456780',
TRUE,
TRUE
),

(
'ABC Pvt Ltd',
'Work From Home',
'Unknown',
'Earn 1 Lakh Per Month',
'Part-Time',
'No Experience',
'Any',
'Unknown',
'',
'URGENT HIRING!! Earn money from home. WhatsApp us now.',
'None',
'Unlimited Income',
'abcjobs@gmail.com',
'9988776655',
FALSE,
FALSE
),

(
'XYZ Online Jobs',
'Data Entry Operator',
'Remote',
'50000 Per Week',
'Part-Time',
'No Experience',
'10th Pass',
'Unknown',
'',
'Work from home and earn huge money instantly.',
'No Requirements',
'Weekly Payment',
'xyzcareer@yahoo.com',
'9876501234',
FALSE,
FALSE
),

(
'Microsoft',
'Software Engineer',
'Hyderabad',
'18 LPA',
'Full-Time',
'2 Years',
'B.Tech',
'Software',
'Microsoft Corporation',
'Develop cloud-based applications.',
'Java, SQL, Azure',
'Insurance, Bonus',
'careers@microsoft.com',
'9876512345',
TRUE,
TRUE
);

-- ===========================================================
-- PREDICTIONS
-- ===========================================================

INSERT INTO predictions
(
job_id,
prediction,
risk_score,
ml_probability,
rule_score
)

VALUES

(1,'Real',8.50,4.20,12.80),

(2,'Real',15.30,18.00,12.60),

(3,'Fake',95.40,98.20,92.60),

(4,'Fake',88.75,90.00,87.50),

(5,'Real',6.80,5.00,8.50);

-- ===========================================================
-- FRAUD RULES
-- ===========================================================

INSERT INTO fraud_rules
(
job_id,
rule_name,
severity,
description
)

VALUES

(
3,
'Suspicious Keywords',
'HIGH',
'Contains Work From Home and Earn Money'
),

(
3,
'Free Email Domain',
'HIGH',
'Uses Gmail instead of official domain'
),

(
3,
'WhatsApp Number',
'HIGH',
'Contact through WhatsApp'
),

(
3,
'Unrealistic Salary',
'HIGH',
'Earn 1 Lakh Per Month'
),

(
4,
'Yahoo Email',
'HIGH',
'Uses Yahoo email'
),

(
4,
'No Company Logo',
'LOW',
'Company logo missing'
),

(
4,
'No Requirements',
'MEDIUM',
'Requirements section is empty'
);

-- ===========================================================
-- REPORTS
-- ===========================================================

INSERT INTO reports
(
job_id,
user_id,
report_reason,
comments
)

VALUES

(
3,
1,
'Fraudulent Job',
'Requested money before interview.'
),

(
4,
1,
'Fake Company',
'Company profile not available.'
);

-- ===========================================================
-- PREDICTION HISTORY
-- ===========================================================

INSERT INTO prediction_history
(
job_id,
prediction_id,
analysed_by
)

VALUES

(1,1,'System'),

(2,2,'System'),

(3,3,'System'),

(4,4,'System'),

(5,5,'System');

-- ===========================================================
-- Verify Records
-- ===========================================================

SELECT * FROM users;

SELECT * FROM jobs;

SELECT * FROM predictions;

SELECT * FROM fraud_rules;

SELECT * FROM reports;

SELECT * FROM prediction_history;

-- ===========================================================
-- End of Sample Data
-- ===========================================================