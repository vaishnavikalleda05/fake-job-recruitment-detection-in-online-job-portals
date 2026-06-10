import re

# ─────────────────────────────────────────────
# Smart Job Posting Extractor
# Extracts structured fields from raw pasted job text
# ─────────────────────────────────────────────

def extract_email(text: str) -> str:
    pattern = r"[\w\.-]+@[\w\.-]+\.\w{2,}"
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""


def extract_phone(text: str) -> str:
    pattern = r"(\+91[\s\-]?)?[6-9]\d{9}|\+?\d[\d\s\-]{8,12}\d"
    matches = re.findall(pattern, text)
    return matches[0].strip() if matches else ""


def extract_website(text: str) -> str:
    pattern = r"https?://[^\s\)\"\'<>]+"
    matches = re.findall(pattern, text)
    # Filter out social media links
    for m in matches:
        if not any(s in m for s in ["linkedin", "facebook", "twitter", "instagram", "youtube"]):
            return m
    return ""


def extract_company_name(text: str) -> str:
    patterns = [
        r"(?:company|employer|organisation|organization|firm|about us)[:\-\s]+([A-Z][A-Za-z0-9\s&\.,]{2,40})",
        r"(?:at|@|with|join)\s+([A-Z][A-Za-z0-9\s&\.]{2,30})(?:\s+as|\s+for|\s+is|\.|,)",
        r"^([A-Z][A-Za-z0-9\s&\.]{2,30})\s+(?:is hiring|is looking|seeks|requires|invites)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            name = match.group(1).strip().rstrip(".,")
            if len(name) > 2:
                return name
    return ""


def extract_job_title(text: str) -> str:
    patterns = [
        r"(?:position|role|job title|vacancy|opening|hiring for|post)[:\-\s]+([A-Za-z\s\/\-]{3,50})",
        r"(?:we are hiring|looking for|seeking)[:\s]+(?:a\s+|an\s+)?([A-Za-z\s\/\-]{3,50})",
        r"^([A-Z][A-Za-z\s\/\-]{2,40})(?:\s*[-–]\s*Job|\s*Position|\s*Role|\s*Vacancy)",
        r"Job Title[:\s]+([A-Za-z\s\/\-]{3,50})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            title = match.group(1).strip().rstrip(".,\n")
            if 3 < len(title) < 60:
                return title
    # Fallback: first line that looks like a title
    for line in text.split("\n")[:5]:
        line = line.strip()
        if 5 < len(line) < 60 and not any(c in line for c in ["@", "http", "₹", "$"]):
            return line
    return ""


def extract_location(text: str) -> str:
    patterns = [
        r"(?:location|place|city|based in|office)[:\-\s]+([A-Za-z\s,]{3,50})",
        r"(?:work from|wfh|remote|onsite|hybrid)[:\s]*([A-Za-z\s,]{0,30})",
        r"\b(Bangalore|Mumbai|Delhi|Hyderabad|Chennai|Pune|Kolkata|Noida|Gurgaon|"
        r"Ahmedabad|Jaipur|Remote|Work From Home|WFH)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            loc = match.group(1).strip().rstrip(".,\n") if match.lastindex else match.group(0).strip()
            if loc:
                return loc
    return ""


def extract_salary(text: str) -> str:
    patterns = [
        r"(?:salary|ctc|package|pay|stipend|compensation)[:\-\s]+([\d\s\-–,\.LlKkPA\/permonthyear₹$]+)",
        r"(₹\s*[\d,\.]+\s*(?:LPA|lpa|L|lakh|k|K)?(?:\s*[-–to]+\s*[\d,\.]+\s*(?:LPA|lpa|L|lakh|k|K)?)?)",
        r"(\d+[\d,\.]*\s*(?:LPA|lpa|lakh|lac|L)\s*(?:[-–to]+\s*\d+[\d,\.]*\s*(?:LPA|lpa|lakh|lac|L))?)",
        r"(\d+[kK]\s*[-–to]+\s*\d+[kK])",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            sal = match.group(1).strip().rstrip(".,\n ")
            if sal and len(sal) < 50:
                return sal
    return ""


def extract_employment_type(text: str) -> str:
    text_lower = text.lower()
    if any(x in text_lower for x in ["full time", "full-time", "permanent"]):
        return "Full-time"
    if any(x in text_lower for x in ["part time", "part-time"]):
        return "Part-time"
    if "contract" in text_lower:
        return "Contract"
    if any(x in text_lower for x in ["internship", "intern"]):
        return "Internship"
    if "temporary" in text_lower:
        return "Temporary"
    return ""


def extract_experience(text: str) -> str:
    patterns = [
        r"(\d+\+?\s*[-–to]+\s*\d+\s*years?\s*(?:of\s*)?experience)",
        r"(\d+\+?\s*years?\s*(?:of\s*)?experience)",
        r"(?:experience|exp)[:\-\s]+([\w\s\+\-]{3,30})",
        r"(fresher|entry level|no experience|0[\-–]1 year)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def extract_description_sections(text: str) -> dict:
    """
    Try to split raw text into description, requirements, benefits sections.
    Falls back to putting everything in description.
    """
    sections = {
        "description": "",
        "requirements": "",
        "benefits": "",
        "company_profile": "",
    }

    # Patterns to identify section headers
    desc_headers = r"(?:job description|about the role|role overview|responsibilities|duties|what you.ll do)"
    req_headers = r"(?:requirements?|qualifications?|skills? required|what we.re looking for|eligibility|must have)"
    ben_headers = r"(?:benefits?|perks?|what we offer|compensation|why join us|we offer)"
    comp_headers = r"(?:about (?:the )?company|about us|who we are|company overview|our company)"

    def split_section(pattern, text):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.start() if match else -1

    desc_pos = split_section(desc_headers, text)
    req_pos  = split_section(req_headers, text)
    ben_pos  = split_section(ben_headers, text)
    comp_pos = split_section(comp_headers, text)

    positions = sorted(
        [(p, k) for p, k in [
            (desc_pos, "description"), (req_pos, "requirements"),
            (ben_pos, "benefits"), (comp_pos, "company_profile")
        ] if p != -1]
    )

    if not positions:
        # No section headers found — put everything in description
        sections["description"] = text.strip()
        return sections

    for i, (pos, key) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        sections[key] = text[pos:end].strip()

    # If description section is empty, use text before first section
    if not sections["description"] and positions:
        sections["description"] = text[:positions[0][0]].strip()

    return sections


# ─────────────────────────────────────────────
# Master Extractor
# ─────────────────────────────────────────────

def extract_all(raw_text: str) -> dict:
    """
    Given raw pasted job posting text, extract all structured fields.
    Returns a dict ready to pass into the model and explainer.
    """
    sections = extract_description_sections(raw_text)

    return {
        "title":            extract_job_title(raw_text),
        "company_name":     extract_company_name(raw_text),
        "location":         extract_location(raw_text),
        "salary_range":     extract_salary(raw_text),
        "contact_email":    extract_email(raw_text),
        "contact_phone":    extract_phone(raw_text),
        "company_website":  extract_website(raw_text),
        "employment_type":  extract_employment_type(raw_text),
        "experience":       extract_experience(raw_text),
        "description":      sections["description"] or raw_text,
        "requirements":     sections["requirements"],
        "benefits":         sections["benefits"],
        "company_profile":  sections["company_profile"],
        "has_company_logo": 0,
        "has_questions":    0,
        "raw_text":         raw_text,
    }
