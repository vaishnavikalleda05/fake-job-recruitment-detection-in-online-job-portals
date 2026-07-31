-- ===========================================================
-- Fake Job Detection in Online Portals
-- SQL Queries
-- ===========================================================

USE fake_job_detection;

-- ===========================================================
-- BASIC QUERIES
-- ===========================================================

-- 1. Display all jobs
SELECT * FROM jobs;

-- 2. Display all predictions
SELECT * FROM predictions;

-- 3. Display all reports
SELECT * FROM reports;

-- 4. Display all users
SELECT * FROM users;

-- 5. Show only real jobs
SELECT *
FROM predictions
WHERE prediction='Real';

-- 6. Show only fake jobs
SELECT *
FROM predictions
WHERE prediction='Fake';

-- 7. Show suspicious jobs
SELECT *
FROM predictions
WHERE prediction='Suspicious';

-- 8. Jobs located in Hyderabad
SELECT *
FROM jobs
WHERE location='Hyderabad';

-- 9. Jobs having company logo
SELECT *
FROM jobs
WHERE has_company_logo=TRUE;

-- 10. Jobs without company logo
SELECT *
FROM jobs
WHERE has_company_logo=FALSE;

-- ===========================================================
-- AGGREGATE FUNCTIONS
-- ===========================================================

-- 11. Total jobs
SELECT COUNT(*) AS TotalJobs
FROM jobs;

-- 12. Total fake jobs
SELECT COUNT(*) AS FakeJobs
FROM predictions
WHERE prediction='Fake';

-- 13. Total real jobs
SELECT COUNT(*) AS RealJobs
FROM predictions
WHERE prediction='Real';

-- 14. Average risk score
SELECT AVG(risk_score) AS AverageRisk
FROM predictions;

-- 15. Maximum risk score
SELECT MAX(risk_score) AS HighestRisk
FROM predictions;

-- 16. Minimum risk score
SELECT MIN(risk_score) AS LowestRisk
FROM predictions;

-- ===========================================================
-- ORDER BY
-- ===========================================================

-- 17. Highest risk jobs
SELECT *
FROM predictions
ORDER BY risk_score DESC;

-- 18. Lowest risk jobs
SELECT *
FROM predictions
ORDER BY risk_score ASC;

-- ===========================================================
-- JOINS
-- ===========================================================

-- 19. Job title with prediction
SELECT
jobs.job_title,
predictions.prediction,
predictions.risk_score
FROM jobs
INNER JOIN predictions
ON jobs.job_id=predictions.job_id;

-- 20. Company with prediction
SELECT
company_name,
prediction,
risk_score
FROM jobs
JOIN predictions
ON jobs.job_id=predictions.job_id;

-- 21. Job reports
SELECT
jobs.job_title,
reports.report_reason
FROM jobs
JOIN reports
ON jobs.job_id=reports.job_id;

-- ===========================================================
-- GROUP BY
-- ===========================================================

-- 22. Jobs by company
SELECT
company_name,
COUNT(*) AS TotalJobs
FROM jobs
GROUP BY company_name;

-- 23. Jobs by location
SELECT
location,
COUNT(*) AS TotalJobs
FROM jobs
GROUP BY location;

-- 24. Prediction count
SELECT
prediction,
COUNT(*)
FROM predictions
GROUP BY prediction;

-- ===========================================================
-- HAVING
-- ===========================================================

-- 25. Companies having more than one job
SELECT
company_name,
COUNT(*) AS Jobs
FROM jobs
GROUP BY company_name
HAVING COUNT(*)>1;

-- ===========================================================
-- SUBQUERIES
-- ===========================================================

-- 26. Highest risk job
SELECT *
FROM predictions
WHERE risk_score=
(
SELECT MAX(risk_score)
FROM predictions
);

-- 27. Lowest risk job
SELECT *
FROM predictions
WHERE risk_score=
(
SELECT MIN(risk_score)
FROM predictions
);

-- ===========================================================
-- STRING FUNCTIONS
-- ===========================================================

-- 28. Company names in uppercase
SELECT
UPPER(company_name)
FROM jobs;

-- 29. Company names in lowercase
SELECT
LOWER(company_name)
FROM jobs;

-- 30. Length of job titles
SELECT
job_title,
LENGTH(job_title)
FROM jobs;

-- ===========================================================
-- DATE FUNCTIONS
-- ===========================================================

-- 31. Current Date
SELECT CURDATE();

-- 32. Current Time
SELECT NOW();

-- ===========================================================
-- LIKE
-- ===========================================================

-- 33. Companies starting with M
SELECT *
FROM jobs
WHERE company_name LIKE 'M%';

-- 34. Job title containing Developer
SELECT *
FROM jobs
WHERE job_title LIKE '%Developer%';

-- ===========================================================
-- BETWEEN
-- ===========================================================

-- 35. Risk score between 20 and 80
SELECT *
FROM predictions
WHERE risk_score
BETWEEN 20 AND 80;

-- ===========================================================
-- EXISTS
-- ===========================================================

-- 36. Jobs having prediction
SELECT *
FROM jobs j
WHERE EXISTS
(
SELECT 1
FROM predictions p
WHERE j.job_id=p.job_id
);

-- ===========================================================
-- CASE
-- ===========================================================

-- 37. Display Risk Level
SELECT
job_id,
risk_score,

CASE

WHEN risk_score<35 THEN 'Likely Real'

WHEN risk_score BETWEEN 35 AND 64
THEN 'Suspicious'

ELSE 'Likely Fake'

END AS RiskLevel

FROM predictions;

-- ===========================================================
-- WINDOW FUNCTIONS
-- ===========================================================

-- 38. Rank by risk score
SELECT

job_id,

risk_score,

RANK() OVER
(
ORDER BY risk_score DESC
)

AS RiskRank

FROM predictions;

-- 39. Dense Rank
SELECT

job_id,

risk_score,

DENSE_RANK() OVER
(
ORDER BY risk_score DESC
)

AS DenseRank

FROM predictions;

-- ===========================================================
-- VIEW
-- ===========================================================

-- 40. Fake Jobs View
SELECT *
FROM fake_jobs;

-- 41. High Risk View
SELECT *
FROM high_risk_jobs;

-- 42. Suspicious Jobs View
SELECT *
FROM suspicious_jobs;

-- ===========================================================
-- STORED PROCEDURE
-- ===========================================================

CALL TotalFakeJobs();

CALL AverageRisk();

-- ===========================================================
-- UPDATE
-- ===========================================================

UPDATE predictions
SET risk_score=95
WHERE prediction_id=3;

-- ===========================================================
-- DELETE
-- ===========================================================

DELETE FROM reports
WHERE report_id=2;

-- ===========================================================
-- INSERT
-- ===========================================================

INSERT INTO reports
(job_id,user_id,report_reason,comments)

VALUES

(
2,
1,
'Suspicious',
'Need manual verification'
);

-- ===========================================================
-- COMPLEX ANALYTICS
-- ===========================================================

-- Fake jobs by company

SELECT

jobs.company_name,

COUNT(*) AS FakeJobs

FROM jobs

JOIN predictions

ON jobs.job_id=predictions.job_id

WHERE prediction='Fake'

GROUP BY company_name

ORDER BY FakeJobs DESC;

-- Average Risk by Company

SELECT

jobs.company_name,

AVG(predictions.risk_score)

AS AvgRisk

FROM jobs

JOIN predictions

ON jobs.job_id=predictions.job_id

GROUP BY company_name

ORDER BY AvgRisk DESC;

-- Top 5 Highest Risk Jobs

SELECT

jobs.job_title,

jobs.company_name,

predictions.risk_score

FROM jobs

JOIN predictions

ON jobs.job_id=predictions.job_id

ORDER BY predictions.risk_score DESC

LIMIT 5;

-- ===========================================================
-- END
-- ===========================================================