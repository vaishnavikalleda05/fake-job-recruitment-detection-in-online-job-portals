from preprocess import SUSPICIOUS_KEYWORDS, SCAM_EMAIL_DOMAINS
import re

RED_FLAG_RULES = [
    {"id":"suspicious_keywords","name":"Suspicious Keywords Found","severity":"HIGH","check":lambda job:_check_keywords(job)},
    {"id":"free_email","name":"Free Email Domain Used","severity":"HIGH","check":lambda job:_check_free_email(job)},
    {"id":"no_company_profile","name":"Missing Company Profile","severity":"MEDIUM","check":lambda job:_check_missing_field(job,"company_profile","Company profile is missing")},
    {"id":"no_requirements","name":"No Requirements Listed","severity":"MEDIUM","check":lambda job:_check_missing_field(job,"requirements","No job requirements specified")},
    {"id":"no_logo","name":"No Company Logo","severity":"LOW","check":lambda job:_check_no_logo(job)},
    {"id":"vague_description","name":"Very Short/Vague Description","severity":"MEDIUM","check":lambda job:_check_vague_description(job)},
    {"id":"excessive_exclamation","name":"Excessive Exclamation Marks","severity":"LOW","check":lambda job:_check_exclamation(job)},
    {"id":"no_location","name":"No Location Provided","severity":"LOW","check":lambda job:_check_missing_field(job,"location","No location specified")},
    {"id":"unrealistic_title","name":"Unrealistic Job Title","severity":"MEDIUM","check":lambda job:_check_unrealistic_title(job)},
    {"id":"too_good_salary","name":"Unrealistically High Salary Claims","severity":"HIGH","check":lambda job:_check_salary_claims(job)},
    {"id":"contact_info_in_description","name":"Phone/WhatsApp in Description","severity":"HIGH","check":lambda job:_check_contact_in_desc(job)},
    # ── NEW RULE 12 — Naukri-inspired ──
    {"id":"confidential_info_request","name":"Asking for Confidential / Personal Info","severity":"HIGH","check":lambda job:_check_confidential_info(job)},
    # ── NEW RULE 13 — Naukri-inspired ──
    {"id":"portal_impersonation","name":"Fake Job Portal Impersonation","severity":"HIGH","check":lambda job:_check_portal_impersonation(job)},
]


def _check_keywords(job):
    full_text = " ".join([str(job.get(k,"")) for k in ["title","description","requirements","benefits"]]).lower()
    found = [kw for kw in SUSPICIOUS_KEYWORDS if kw in full_text]
    if found:
        return {"message":f"Found {len(found)} suspicious keyword(s): {', '.join(found[:5])}{'...' if len(found)>5 else ''}","detail":"Scam postings use high-earning promises and urgency language."}
    return None


def _check_free_email(job):
    email = str(job.get("contact_email","")).lower().strip()
    if not email: return None
    for domain in SCAM_EMAIL_DOMAINS:
        if email.endswith(f"@{domain}"):
            return {"message":f"Recruiter using free email domain: {email}","detail":"Legitimate companies use official domain emails (hr@company.com), not Gmail/Yahoo."}
    return None


def _check_missing_field(job, field, message):
    val = job.get(field,"")
    if not val or str(val).strip()=="" or str(val).lower() in ["nan","none"]:
        return {"message":message,"detail":"Incomplete job postings are a common sign of fraudulent listings."}
    return None


def _check_no_logo(job):
    try:
        if int(job.get("has_company_logo",1))==0:
            return {"message":"No company logo attached","detail":"Most legitimate companies upload their logo."}
    except: pass
    return None


def _check_vague_description(job):
    desc = str(job.get("description",""))
    wc = len(desc.split())
    if wc < 30:
        return {"message":f"Job description is very short ({wc} words)","detail":"Real postings typically contain 100+ words."}
    return None


def _check_exclamation(job):
    count = (str(job.get("description",""))+str(job.get("title",""))).count("!")
    if count >= 3:
        return {"message":f"Description contains {count} exclamation marks","detail":"Overuse of '!' is a classic scam tactic to create false excitement."}
    return None


def _check_unrealistic_title(job):
    title = str(job.get("title","")).lower()
    for phrase in ["earn from home","work from home job","home based","no experience","easy money"]:
        if phrase in title:
            return {"message":f"Job title contains suspicious phrase: '{phrase}'","detail":"Real job titles describe roles, not income promises."}
    return None


def _check_salary_claims(job):
    text = str(job.get("description","")).lower()
    patterns = [r"\d+\s*(lakh|lac)\s*per\s*(month|week|day)",r"earn\s*\d+",r"\d+000\s*per\s*(day|week)",r"unlimited\s*(income|earning|salary)"]
    for p in patterns:
        if re.search(p, text):
            return {"message":"Unrealistic salary or earning claims in description","detail":"'Earn 1 lakh per month' or 'unlimited income' are classic scam red flags."}
    return None


def _check_contact_in_desc(job):
    text = str(job.get("description",""))
    if re.search(r"\b(\+91|0)?[6-9]\d{9}\b", text) or re.search(r"whatsapp|telegram|contact\s*us\s*at", text, re.IGNORECASE):
        return {"message":"Phone number or WhatsApp/Telegram contact in description","detail":"Legitimate postings use official application systems, not personal messaging apps."}
    return None


# ── NEW RULE 12: Confidential Info Request ──
def _check_confidential_info(job):
    """
    Detects requests for sensitive personal/financial information.
    Inspired by Naukri.com Security Center advisory.
    Common Indian scam pattern: ask for Aadhar, PAN, OTP, bank details during hiring.
    """
    text = " ".join([str(job.get(k,"")) for k in ["title","description","requirements"]]).lower()

    CONFIDENTIAL_KEYWORDS = [
        "credit card","debit card","card number",
        "aadhar","aadhaar","aadhar number","aadhar card",
        "pan card","pan number",
        "otp","one time password",
        "bank account","account number","ifsc","ifsc code",
        "passbook","cancelled cheque","cheque",
        "send your documents","send your id proof",
        "share your personal details","share your bank details",
        "net banking","upi id","gpay","phonepe","paytm transfer",
        "date of birth","passport number","driving licence",
    ]

    found = [kw for kw in CONFIDENTIAL_KEYWORDS if kw in text]
    if found:
        return {
            "message": f"Posting requests confidential information: {', '.join(found[:4])}{'...' if len(found)>4 else ''}",
            "detail":  "Legitimate employers NEVER ask for Aadhar, PAN, OTP, bank account or credit card details during recruitment. This is a major Indian scam pattern."
        }
    return None


# ── NEW RULE 13: Fake Job Portal Impersonation ──
def _check_portal_impersonation(job):
    """
    Detects emails/content impersonating known job portals.
    e.g. naukriservices004@naukrioutlook.com looks like Naukri but isn't.
    Inspired by Naukri.com Security Center advisory.
    """
    KNOWN_PORTALS = ["naukri","indeed","linkedin","monster","shine","timesjobs","freshersworld","instahyre","hirist","foundit","glassdoor","internshala"]
    OFFICIAL_DOMAINS = {
        "naukri":["naukri.com"],"indeed":["indeed.com"],"linkedin":["linkedin.com"],
        "monster":["monster.com","foundit.in"],"shine":["shine.com"],
        "timesjobs":["timesjobs.com"],"freshersworld":["freshersworld.com"],
        "glassdoor":["glassdoor.com"],"internshala":["internshala.com"],
        "foundit":["foundit.in"],"instahyre":["instahyre.com"],"hirist":["hirist.com"],
    }

    email = str(job.get("contact_email","")).lower().strip()
    text  = " ".join([str(job.get(k,"")) for k in ["description","company_profile","title"]]).lower()

    if email and "@" in email:
        email_domain = email.split("@")[-1]
        for portal in KNOWN_PORTALS:
            if portal in email and email_domain not in OFFICIAL_DOMAINS.get(portal,[portal+".com"]):
                return {
                    "message": f"Email impersonates '{portal}' portal: {email}",
                    "detail":  f"Scammers create fake domains containing '{portal}' to appear official. Real {portal} emails only come from their verified domain."
                }

    for portal in KNOWN_PORTALS:
        if re.search(rf"(?:from|by|via|through)\s+{portal}(?:\s+team|\s+hr|\s+recruitment)", text, re.IGNORECASE):
            if email and not any(email.endswith(d) for d in OFFICIAL_DOMAINS.get(portal,[portal+".com"])):
                return {
                    "message": f"Claims to be from '{portal}' but email doesn't match official domain",
                    "detail":  f"Verified {portal} communications come only from their official domain. This may be an impersonation scam."
                }

    return None


# ─────────────────────────────────────────────
SEVERITY_WEIGHT = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

def explain_job(job: dict) -> dict:
    red_flags = []
    total_weight = 0
    triggered_weight = 0

    for rule in RED_FLAG_RULES:
        weight = SEVERITY_WEIGHT[rule["severity"]]
        total_weight += weight
        result = rule["check"](job)
        if result:
            triggered_weight += weight
            red_flags.append({"name":rule["name"],"severity":rule["severity"],"message":result["message"],"detail":result["detail"]})

    base_score = (triggered_weight / total_weight) * 100 if total_weight > 0 else 0
    ml_prob    = float(job.get("_ml_prob", 0.5))
    risk_score = round((base_score * 0.5) + (ml_prob * 100 * 0.5), 1)
    risk_score = min(risk_score, 100.0)

    if risk_score >= 65:   verdict, verdict_color = "🚨 LIKELY FAKE",  "red"
    elif risk_score >= 35: verdict, verdict_color = "⚠️ SUSPICIOUS",   "orange"
    else:                  verdict, verdict_color = "✅ LIKELY REAL",   "green"

    return {"red_flags":red_flags,"risk_score":risk_score,"verdict":verdict,"verdict_color":verdict_color,"rule_flags_count":len(red_flags)}
