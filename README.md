# Fake Job Recruitment Detection in Online Job Portals

## Overview

Fake Job Recruitment Detection in Online Job Portals is a Machine Learning-based web application that detects fraudulent job postings using Natural Language Processing (NLP), Random Forest classification, Rule-Based Analysis, and MySQL database integration.

The system analyzes a job description, extracts important information, predicts whether the job is Real, Fake, or Suspicious, calculates a risk score, and stores the results in a MySQL database for future analysis.

---

## Features

- Detect fake job postings using Machine Learning
- TF-IDF text feature extraction
- Random Forest Classification
- Rule-Based Fraud Detection
- Risk Score Calculation
- Company Email Validation
- Salary Validation
- Prediction Dashboard
- Report Suspicious Jobs
- MySQL Database Integration
- Prediction History Storage

---

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- Pandas
- NumPy
- Scikit-learn
- Random Forest
- TF-IDF Vectorizer
- MySQL
- SQL

---

## Project Structure

```
Fake-job-recruitment-detection-in-online-job-portals
│
├── app.py
├── train.py
├── model.py
├── extractor.py
├── explainer.py
├── validators.py
├── reporter.py
│
├── database
│   ├── db_config.py
│   ├── schema.sql
│   ├── queries.sql
│   └── sample_data.sql
│
├── models
│
├── data
│
├── reports
│
├── templates
│
├── static
│
└── README.md
```

---

## Machine Learning Workflow

1. User submits a job posting.
2. Text is preprocessed.
3. Important job information is extracted.
4. TF-IDF converts text into numerical features.
5. Random Forest predicts whether the job is genuine or fake.
6. Rule Engine calculates additional fraud risk.
7. Final prediction is generated.
8. Job details and prediction are stored in MySQL.

---

## Database Integration

The application uses MySQL to store:

- Job Details
- Prediction Results
- Risk Scores
- Prediction History
- Dashboard Statistics

---

## SQL Operations Used

- CREATE DATABASE
- CREATE TABLE
- INSERT
- SELECT
- UPDATE
- DELETE
- JOIN
- GROUP BY
- ORDER BY
- Aggregate Functions
- Views
- Stored Procedures

---

## Dataset

Dataset used:

Real or Fake Job Posting Prediction Dataset

Source:

https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction

---

## Installation

Clone the repository

```bash
git clone https://github.com/vaishnavikalleda05/fake-job-recruitment-detection-in-online-job-portals.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

Open your browser

```
http://127.0.0.1:5000
```

---

## Future Enhancements

- Deep Learning Models
- Resume Matching
- Company Verification API
- Admin Dashboard
- Email Alerts
- AI Chatbot for Job Verification

---

## Author

**Kalleda Vaishnavi**

B.Tech CSE (Data Science)

Malla Reddy Engineering College

GitHub:
https://github.com/vaishnavikalleda05