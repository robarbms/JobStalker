"""Scraper search targets, not company headquarters or replacement job locations."""

import re


BOSTON_COMPANIES = (
    "MathWorks", "Akamai Technologies", "InterSystems", "CarGurus", "athenahealth",
    "Bose", "HubSpot", "Toast", "Klaviyo", "Datadog", "Rapid7",
)

SEATTLE_COMPANIES = ("Adobe", "Amazon", "Apple", "Google", "Expedia", "Zillow")

COMPANY_LOCATIONS = {
    **dict.fromkeys(BOSTON_COMPANIES, "Boston"),
    **dict.fromkeys(SEATTLE_COMPANIES, "Seattle"),
}


def get_company_location(company):
    return COMPANY_LOCATIONS.get(company, "Remote")


def remote_mode(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, list):
        modes = {remote_mode(item) for item in value}
        return False if False in modes else True if True in modes else None
    if value is not None and not isinstance(value, str):
        raise ValueError(f"Invalid workplace type: {value!r}")
    value = (value or "").casefold().replace("-", "").replace("_", "").replace(" ", "")
    if value in ("remote", "telecommute", "fullyremote", "oraremote"):
        return True
    if value in ("hybrid", "onsite", "inoffice", "office", "orahybrid", "oraonsite"):
        return False
    return None


def matches_location(job, target):
    location = job.get("location") or ""
    if target == "Remote":
        if job.get("is_remote") is not None:
            return job["is_remote"] is True
        location_and_title = location + " " + (job.get("title") or "")
        if re.search(r"\b(?:hybrid|onsite|on-site|not remote|no remote)\b", location_and_title, re.I):
            return False
        return bool(
            re.search(r"\b(?:remote|home[\s-]+based|work[\s-]+from[\s-]+home|anywhere)\b", location, re.I)
            or re.search(
                r"\bremote\b(?![\s-]+(?:sensing|control|procedure|desktop)\b)",
                job.get("title") or "", re.I,
            )
        )
    if target not in ("Boston", "Seattle"):
        raise ValueError(f"Unknown scraper location: {target}")
    for part in re.split(r";|\n|\s/\s", location):
        if re.search(r"\b(?:UK|GB|united kingdom|england|ontario|canada|netherlands|australia)\b", part, re.I):
            continue
        if target == "Boston":
            if re.fullmatch(r"\s*Boston\s*", part, re.I):
                return True
            if re.search(r"\b(?:MA|Massachusetts)\b", part, re.I) and re.search(
                r"\b(?:boston|cambridge|natick|framingham|watertown|waltham|somerville|lexington|"
                r"burlington|needham|wellesley|woburn|bedford|billerica|andover)\b", part, re.I,
            ):
                return True
        else:
            if re.fullmatch(r"\s*Seattle\s*", part, re.I):
                return True
            if re.search(r"\b(?:WA|Washington)\b", part, re.I) and re.search(
                r"\b(?:seattle|bellevue|redmond|kirkland|bothell|issaquah|renton)\b", part, re.I,
            ):
                return True
    return False


def matches_company_location(job, company):
    return matches_location(job, get_company_location(company))


def filter_company_jobs(jobs, company):
    return [job for job in jobs if matches_company_location(job, company)]
