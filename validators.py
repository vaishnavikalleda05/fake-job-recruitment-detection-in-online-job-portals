import re
import requests

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
FREE_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "rediffmail.com", "ymail.com", "aol.com", "mail.com",
    "icloud.com", "protonmail.com", "zoho.com"
]

# Average salary ranges in INR per month (role keyword → [min, max])
SALARY_BENCHMARKS_INR = {
    "software engineer": [40000, 200000],
    "data scientist": [50000, 250000],
    "web developer": [25000, 150000],
    "graphic designer": [20000, 80000],
    "hr": [20000, 80000],
    "accountant": [20000, 90000],
    "sales": [15000, 70000],
    "marketing": [20000, 100000],
    "content writer": [15000, 60000],
    "customer support": [15000, 50000],
    "manager": [50000, 200000],
    "intern": [5000, 25000],
    "fresher": [15000, 40000],
    "data entry": [10000, 30000],
    "teacher": [15000, 60000],
    "nurse": [20000, 70000],
    "driver": [10000, 35000],
    "security": [10000, 30000],
}

DEFAULT_SALARY_RANGE = [10000, 300000]  # fallback


# ─────────────────────────────────────────────
# Email Validator
# ─────────────────────────────────────────────
def validate_email(email: str) -> dict:
    """
    Returns a dict with:
    - is_valid: bool
    - is_free_domain: bool
    - domain: str
    - flags: list of warning strings
    """
    result = {"is_valid": False, "is_free_domain": False, "domain": "", "flags": []}

    if not email or not isinstance(email, str):
        result["flags"].append("No email provided")
        return result

    email = email.strip().lower()
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"

    if not re.match(pattern, email):
        result["flags"].append("Invalid email format")
        return result

    result["is_valid"] = True
    domain = email.split("@")[-1]
    result["domain"] = domain

    if domain in FREE_EMAIL_DOMAINS:
        result["is_free_domain"] = True
        result["flags"].append(
            f"⚠️ Company using free email domain ({domain}) — legitimate companies use official domains"
        )

    return result


# ─────────────────────────────────────────────
# Domain / Company Website Validator
# ─────────────────────────────────────────────
def validate_company_domain(url: str) -> dict:
    """
    Checks if a company website URL is reachable.
    Returns status dict.
    """
    result = {"provided": False, "reachable": False, "flags": []}

    if not url or not isinstance(url, str) or url.strip() == "":
        result["flags"].append("⚠️ No company website provided — legitimate companies usually have a website")
        return result

    result["provided"] = True
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url

    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        if response.status_code < 400:
            result["reachable"] = True
        else:
            result["flags"].append(f"⚠️ Company website returned error code {response.status_code}")
    except requests.exceptions.ConnectionError:
        result["flags"].append("⚠️ Company website is unreachable — could be a fake domain")
    except requests.exceptions.Timeout:
        result["flags"].append("⚠️ Company website timed out")
    except Exception as e:
        result["flags"].append(f"⚠️ Could not verify website: {str(e)}")

    return result


# ─────────────────────────────────────────────
# Salary Sanity Check
# ─────────────────────────────────────────────
def parse_salary(salary_str: str):
    """
    Attempts to extract a numeric salary from strings like:
    '50000-80000', '$50,000', '50k-80k', '5 lakh', etc.
    Returns (min_salary, max_salary) in INR monthly or None if unparseable.
    """
    if not salary_str or not isinstance(salary_str, str):
        return None, None

    salary_str = salary_str.lower().replace(",", "").replace("$", "").replace("₹", "")

    # Handle 'lakh' / 'lac'
    lakh_match = re.findall(r"(\d+\.?\d*)\s*(?:lakh|lac|l\b)", salary_str)
    if lakh_match:
        amounts = [float(x) * 100000 for x in lakh_match]
        # Convert annual to monthly
        monthly = [a / 12 for a in amounts]
        return (min(monthly), max(monthly)) if len(monthly) > 1 else (monthly[0], monthly[0])

    # Handle 'k' (thousands)
    k_values = re.findall(r"(\d+\.?\d*)k", salary_str)
    if k_values:
        amounts = [float(x) * 1000 for x in k_values]
        return (min(amounts), max(amounts)) if len(amounts) > 1 else (amounts[0], amounts[0])

    # Plain numbers
    numbers = re.findall(r"\d+\.?\d*", salary_str)
    if numbers:
        amounts = [float(x) for x in numbers]
        # If very large (annual), convert to monthly
        amounts = [a / 12 if a > 50000 else a for a in amounts]
        return (min(amounts), max(amounts)) if len(amounts) > 1 else (amounts[0], amounts[0])

    return None, None


def validate_salary(salary_str: str, job_title: str = "") -> dict:
    """
    Checks if the salary is realistic for the given job title.
    Returns a dict with flags.
    """
    result = {"flags": [], "parsed_min": None, "parsed_max": None, "suspicious": False}

    if not salary_str or salary_str.strip() == "":
        result["flags"].append("ℹ️ No salary mentioned — common in both real and fake jobs")
        return result

    min_sal, max_sal = parse_salary(salary_str)
    result["parsed_min"] = min_sal
    result["parsed_max"] = max_sal

    if min_sal is None:
        result["flags"].append("ℹ️ Could not parse salary format")
        return result

    # Find benchmark
    benchmark = DEFAULT_SALARY_RANGE
    title_lower = job_title.lower() if job_title else ""
    for keyword, range_ in SALARY_BENCHMARKS_INR.items():
        if keyword in title_lower:
            benchmark = range_
            break

    # Check if unrealistically high
    if max_sal and max_sal > benchmark[1] * 3:
        result["suspicious"] = True
        result["flags"].append(
            f"🚨 Salary (₹{max_sal:,.0f}/month) is suspiciously HIGH for '{job_title}'. "
            f"Typical range: ₹{benchmark[0]:,} – ₹{benchmark[1]:,}/month"
        )
    elif min_sal and min_sal < benchmark[0] * 0.3:
        result["flags"].append(
            f"⚠️ Salary (₹{min_sal:,.0f}/month) seems very LOW for '{job_title}'. "
            f"Typical range: ₹{benchmark[0]:,} – ₹{benchmark[1]:,}/month"
        )
    else:
        result["flags"].append(f"✅ Salary appears reasonable for '{job_title}'")

    return result
