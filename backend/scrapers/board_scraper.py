"""Adapters for public employer job feeds. No credentials or browser required."""

from datetime import datetime, timezone
from html import unescape
import json
import re
from urllib.parse import parse_qs, urljoin, urlsplit
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
import requests

from .scraper_utils import get_queries, log
from .company_locations import matches_company_location, matches_location, remote_mode


class ScraperError(RuntimeError):
    """A board could not be fetched or no longer matches its expected format."""


def text(value):
    return BeautifulSoup(unescape(value or ""), "html.parser").get_text(" ", strip=True)


def matches(title, queries):
    return any(query in title.casefold() for query in queries)


def record(job_id, title, link, description="", location="", date_posted=None, is_remote=None):
    if job_id is None or not str(job_id).strip():
        raise ValueError("Missing job ID")
    if not isinstance(title, str):
        raise ValueError(f"Missing title for job {job_id}")
    return {
        "job_id": str(job_id),
        "title": title.strip(),
        "link": link,
        "description": text(description),
        "location": location or "",
        "date_posted": date_posted[:10] if date_posted else None,
        "salary_min": None,
        "salary_max": None,
        "notes": "",
        "summary": "",
        "is_remote": is_remote,
    }


def scrape_jobs(company, job_ids, queries, source, **options):
    queries = get_queries() if queries is None else queries
    queries = list(dict.fromkeys(query.strip().casefold() for query in queries))
    if not queries:
        return [], 0
    known_ids = {str(job_id) for job_id in job_ids}
    found_ids = set()
    jobs = []
    log(f"Fetching jobs for {company}...", "info", no_end=True)
    try:
        with requests.Session() as session:
            session.headers["User-Agent"] = "JobStalker/1.0 (public employer job listings)"
            for job in source(session, queries, known_ids, **options):
                job_id = job["job_id"]
                if (
                    job_id in found_ids
                    or not matches(job["title"], queries)
                    or not matches_company_location(job, company)
                ):
                    continue
                found_ids.add(job_id)
                if job_id in known_ids:
                    continue
                if not job["title"] or not job["description"]:
                    raise ValueError(f"Missing title or description for job {job_id}")
                if urlsplit(job["link"]).scheme not in ("https", "http"):
                    raise ValueError(f"Invalid job link for {job_id}")
                job["company"] = company
                jobs.append(job)
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
        raise ScraperError(f"{company}: {error}") from error
    return jobs, len(found_ids)


def get_json(session, url, **kwargs):
    response = session.get(url, timeout=30, **kwargs)
    response.raise_for_status()
    return response.json()


def post_json(session, url, **kwargs):
    response = session.post(url, timeout=30, **kwargs)
    response.raise_for_status()
    return response.json()


def get_soup(session, url, **kwargs):
    response = session.get(url, timeout=30, **kwargs)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def required_text(soup, selector):
    element = soup.select_one(selector)
    if element is None:
        raise ScraperError(f"Missing required element: {selector}")
    return element.get_text(" ", strip=True)


def check_progress(ids, seen):
    if not ids or not set(ids) - seen:
        raise ScraperError("Pagination stopped before all advertised jobs were returned")
    seen.update(ids)


def greenhouse_jobs(session, queries, known_ids, board, brand=None):
    data = get_json(
        session, f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs",
        params={"content": "true"},
    )
    for job in data["jobs"]:
        if brand:
            brands = [
                item["value"] for item in job.get("metadata") or []
                if item["name"] == "Brands"
            ]
            if not any(brand in (value if isinstance(value, list) else [value]) for value in brands):
                continue
        workplace = next((
            item["value"] for item in job.get("metadata") or []
            if item["name"].casefold() in ("workplace type", "work model", "remote")
        ), None)
        yield record(
            job["id"], job["title"], job["absolute_url"], job["content"],
            job["location"]["name"], job.get("first_published"), remote_mode(workplace),
        )


def ashby_jobs(session, queries, known_ids, board):
    data = get_json(session, f"https://api.ashbyhq.com/posting-api/job-board/{board}")
    for job in data["jobs"]:
        if job.get("isListed") is False:
            continue
        locations = [job["location"]] + [
            location["location"] for location in job.get("secondaryLocations") or []
        ]
        workplace = remote_mode(job.get("workplaceType"))
        if workplace is None:
            workplace = remote_mode(job.get("isRemote"))
        yield record(
            job["id"], job["title"], job["jobUrl"], job["descriptionHtml"],
            "; ".join(dict.fromkeys(locations)), job.get("publishedAt"),
            workplace,
        )


def lever_jobs(session, queries, known_ids, board):
    offset = 0
    seen = set()
    while True:
        data = get_json(
            session, f"https://api.lever.co/v0/postings/{board}",
            params={"mode": "json", "skip": offset, "limit": 100},
        )
        if not isinstance(data, list):
            raise ScraperError("Expected a list of Lever postings")
        if not data:
            return
        check_progress([job["id"] for job in data], seen)
        for job in data:
            description = "\n".join(
                [job.get("description", "")]
                + [f"{item['text']}\n{item['content']}" for item in job.get("lists") or []]
                + [job.get("additional", "")]
            )
            created = job.get("createdAt")
            posted = datetime.fromtimestamp(created / 1000, timezone.utc).isoformat() if created else None
            yield record(
                job["id"], job["text"], job["hostedUrl"], description,
                job["categories"].get("location", ""), posted, remote_mode(job.get("workplaceType")),
            )
        if len(data) < 100:
            return
        offset += len(data)


def jibe_jobs(session, queries, known_ids, base_url, employer=None):
    page = 1
    seen = set()
    while True:
        data = get_json(session, base_url + "/api/jobs", params={"page": page, "limit": 100})
        postings = [item["data"] for item in data["jobs"]]
        if not postings and data["totalCount"] == 0:
            return
        check_progress([job["req_id"] for job in postings], seen)
        for job in postings:
            # Parent-company boilerplate mentions every brand; only inspect role-specific text.
            if employer:
                description = BeautifulSoup(job["description"], "html.parser")
                for paragraph in description.find_all("p"):
                    if "Who We Are" in paragraph.get_text():
                        continue
                    paragraph_text = " ".join(paragraph.get_text(" ", strip=True).split())
                    if any(phrase in paragraph_text for phrase in (
                        "SiriusXM and its brands", "SiriusXM is the leading",
                        "SiriusXM's subsidiaries", "Pandora, a subsidiary",
                    )):
                        paragraph.decompose()
                if employer.casefold() not in text(job["title"] + " " + str(description)).casefold():
                    continue
            yield record(
                job["req_id"], job["title"],
                f"{base_url}/jobs/{job['slug']}",
                job["description"], job.get("full_location", ""), job.get("posted_date"),
                remote_mode((job.get("tags1") or []) + (job.get("tags6") or [])),
            )
        if len(seen) >= data["totalCount"]:
            return
        page += 1


def oracle_jobs(session, queries, known_ids, host, site, careers_url, target_location=None):
    api = host + "/hcmRestApi/resources/latest"
    yielded = set()
    for query in queries:
        offset = 0
        seen = set()
        while True:
            finder = (
                f"findReqs;siteNumber={site},limit=100,offset={offset},"
                f"keyword={query}"
            )
            data = get_json(
                session, api + "/recruitingCEJobRequisitions",
                params={"onlyData": "true", "expand": "requisitionList", "finder": finder},
            )["items"][0]
            postings = data["requisitionList"]
            if not postings and data["TotalJobsCount"] == 0:
                break
            check_progress([job["Id"] for job in postings], seen)
            for job in postings:
                job_id = str(job["Id"])
                if job_id in yielded or not matches(job["Title"], queries):
                    continue
                yielded.add(job_id)
                candidate = record(
                    job_id, job["Title"], f"{careers_url}/job/{job_id}",
                    location=job.get("PrimaryLocation", ""), date_posted=job.get("PostedDate"),
                    is_remote=remote_mode(job.get("WorkplaceType") or job.get("WorkplaceTypeCode")),
                )
                if target_location and not matches_location(candidate, target_location):
                    continue
                description = ""
                if job_id not in known_ids:
                    details = get_json(
                        session, api + "/recruitingCEJobRequisitionDetails",
                        params={"onlyData": "true", "finder": f'ById;Id="{job_id}"'},
                    )["items"][0]
                    description = "\n".join(details.get(field) or "" for field in (
                        "ExternalDescriptionStr", "ExternalResponsibilitiesStr", "ExternalQualificationsStr",
                    ))
                candidate["description"] = text(description)
                yield candidate
            offset += len(postings)
            if offset >= data["TotalJobsCount"]:
                break


def workday_jobs(session, queries, known_ids, host, tenant, site, employer=None):
    api = f"{host}/wday/cxs/{tenant}/{site}"
    facets = {}
    if employer:
        first = post_json(
            session, api + "/jobs",
            json={"limit": 20, "offset": 0, "searchText": "", "appliedFacets": {}},
        )
        company_facet = next(
            (facet for facet in first["facets"] if facet["facetParameter"] == "hiringCompany"), None
        )
        if company_facet is None:
            raise ScraperError("Workday company filter missing")
        company_ids = [value["id"] for value in company_facet["values"] if value["descriptor"] == employer]
        if not company_ids:
            raise ScraperError(f"Workday company filter no longer contains {employer}")
        facets = {"hiringCompany": company_ids}
    offset = 0
    seen = set()
    while True:
        data = post_json(
            session, api + "/jobs",
            json={
                "limit": 20, "offset": offset, "searchText": "",
                "appliedFacets": facets,
            },
        )
        postings = data["jobPostings"]
        if not postings and data["total"] == 0:
            return
        check_progress([job["externalPath"] for job in postings], seen)
        for job in postings:
            if not matches(job["title"], queries):
                continue
            job_id = str(job["bulletFields"][0])
            details = {}
            multiple_locations = bool(re.search(r"\b\d+ locations\b", job.get("locationsText", ""), re.I))
            if job_id not in known_ids or multiple_locations:
                details = get_json(session, api + job["externalPath"])["jobPostingInfo"]
            locations = [details.get("location") or job.get("locationsText", "")]
            locations.extend(details.get("additionalLocations") or [])
            yield record(
                job_id, job["title"], f"{host}/{site}{job['externalPath']}",
                details.get("jobDescription", ""), "; ".join(dict.fromkeys(locations)),
                details.get("startDate"),
                remote_mode(details.get("remoteType")),
            )
        offset += len(postings)
        if offset >= data["total"]:
            return


def tiktok_jobs(session, queries, known_ids):
    url = "https://api.lifeattiktok.com/api/v1/public/supplier/search/job/posts"
    headers = {"website-path": "tiktok", "Origin": "https://lifeattiktok.com"}
    yielded = set()
    for query in queries:
        offset = 0
        seen = set()
        while True:
            response = post_json(
                session, url, headers=headers,
                json={"keyword": query, "limit": 100, "offset": offset},
            )
            if response["code"] != 0:
                raise ScraperError(f"TikTok API error: {response.get('message')}")
            data = response["data"]
            postings = data["job_post_list"]
            if not postings and data["count"] == 0:
                break
            check_progress([job["id"] for job in postings], seen)
            for job in postings:
                job_id = str(job["id"])
                if job_id in yielded:
                    continue
                yielded.add(job_id)
                locations = []
                city = job.get("city_info")
                while city:
                    locations.append(city["en_name"])
                    city = city.get("parent")
                yield record(
                    job_id, job["title"], f"https://lifeattiktok.com/search/{job_id}",
                    job["description"] + "\n" + (job.get("requirement") or ""),
                    ", ".join(dict.fromkeys(locations)),
                )
            offset += len(postings)
            if offset >= data["count"]:
                break


def linkedin_jobs(session, queries, known_ids):
    yielded = set()
    for query in queries:
        offset = 0
        seen = set()
        while True:
            soup = get_soup(
                session, "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
                params={"f_C": "1337", "keywords": query, "start": offset, "sortBy": "DD"},
            )
            cards = soup.select("[data-entity-urn^='urn:li:jobPosting:']")
            if not cards:
                if soup.select_one("form, title"):
                    raise ScraperError("LinkedIn returned a login or challenge page")
                break
            check_progress([card["data-entity-urn"] for card in cards], seen)
            for card in cards:
                job_id = card["data-entity-urn"].rsplit(":", 1)[1]
                if job_id in yielded:
                    continue
                yielded.add(job_id)
                title = required_text(card, ".base-search-card__title")
                if not matches(title, queries):
                    continue
                link = f"https://www.linkedin.com/jobs/view/{job_id}"
                description = ""
                if job_id not in known_ids:
                    details = get_soup(session, link)
                    container = details.select_one(".description__text .show-more-less-html__markup")
                    if container is None:
                        raise ScraperError(f"LinkedIn description missing for {job_id}")
                    description = str(container)
                location = card.select_one(".job-search-card__location")
                posted = card.select_one("time[datetime]")
                yield record(
                    job_id, title, link, description,
                    location.get_text(strip=True) if location else "",
                    posted["datetime"] if posted else None,
                )
            offset += len(cards)


def job_postings(soup):
    def walk(value):
        if isinstance(value, list):
            for item in value:
                yield from walk(item)
        elif isinstance(value, dict):
            types = value.get("@type", [])
            if types == "JobPosting" or isinstance(types, list) and "JobPosting" in types:
                yield value
            if "@graph" in value:
                yield from walk(value["@graph"])

    for script in soup.select('script[type="application/ld+json"]'):
        yield from walk(json.loads(script.get_text()))


def website_jobs(session, queries, known_ids, url, link_pattern, description_selector, location_selector):
    soup = get_soup(session, url)
    links = {}
    for anchor in soup.select("a[href]"):
        link = urljoin(url, anchor["href"]).split("?")[0].rstrip("/")
        match = re.fullmatch(link_pattern, link)
        if match:
            links[match["id"]] = (link, anchor.get_text(" ", strip=True))
    if not links:
        if re.search(r"no (?:current |open )?(?:positions|openings|jobs)", soup.get_text(), re.I):
            return
        raise ScraperError(f"No job links found on {url}; check the board layout")
    for job_id, (link, title) in links.items():
        if not matches(title, queries):
            continue
        details = get_soup(session, link)
        schema = next(job_postings(details), {})
        heading = details.select_one("h1")
        description = details.select_one(description_selector)
        location = details.select_one(location_selector)
        if heading is None or description is None:
            raise ScraperError(f"Missing job content on {link}")
        yield record(
            job_id, heading.get_text(" ", strip=True), link, str(description),
            location.get_text(" ", strip=True) if location else "",
            schema.get("datePosted"),
            remote_mode(schema.get("jobLocationType")),
        )


def hulu_jobs(session, queries, known_ids):
    url = "https://www.disneycareers.com/en/search-jobs/Hulu/391-1635/1"
    visited = set()
    seen = set()
    while url:
        if url in visited:
            raise ScraperError("Disney careers pagination repeated a page")
        visited.add(url)
        soup = get_soup(session, url)
        listing = soup.select_one("#search-results-jobs")
        if listing is None:
            raise ScraperError("Disney careers results missing")
        cards = listing.select("a[data-job-id]")
        if cards:
            check_progress([card["data-job-id"] for card in cards], seen)
        elif int(listing.get("data-results-count", 0)) > 0:
            raise ScraperError("Disney careers jobs missing from nonempty results")
        for card in cards:
            job_id = card["data-job-id"]
            title = required_text(card, "h2")
            if not matches(title, queries):
                continue
            link = urljoin(url, card["href"])
            description = ""
            if job_id not in known_ids:
                details = get_soup(session, link)
                container = details.select_one(".ats-description")
                if container is None:
                    raise ScraperError(f"Disney careers description missing for {job_id}")
                description = str(container)
            location = card.select_one(".job-location")
            posted = card.select_one(".job-date-posted")
            date_posted = None
            if posted:
                date_posted = datetime.strptime(
                    posted.get_text(strip=True).replace(".", ""), "%b %d, %Y"
                ).strftime("%Y-%m-%d")
            yield record(
                job_id, title, link, description,
                location.get_text(" ", strip=True) if location else "", date_posted,
            )
        next_page = soup.select_one(".pagination a.next:not(.disabled)")
        url = urljoin(url, next_page["href"]) if next_page else None


def get_xml(session, url):
    response = session.get(url, timeout=30)
    response.raise_for_status()
    try:
        return ET.fromstring(response.content)
    except ET.ParseError as error:
        raise ScraperError(f"Invalid XML feed from {url}: {error}") from error


def mathworks_jobs(session, queries, known_ids):
    root = get_xml(session, "https://www.mathworks.com/company/jobs/opportunities/rss.xml")
    channel = root.find("channel")
    if root.tag != "rss" or channel is None:
        raise ScraperError("MathWorks RSS channel missing")
    for item in channel.findall("item"):
        job_id = item.findtext("id")
        title = item.findtext("title_raw")
        link = item.findtext("link")
        if not link or not title:
            raise ScraperError("MathWorks job title or link missing")
        description = "\n".join(item.findtext(field) or "" for field in (
            "summary", "responsibilities", "qualifications", "required_qualifications",
        ))
        yield record(
            job_id, title, link, description,
            item.findtext("location/locationName", "").strip(),
        )


def signals_jobs(session, queries, known_ids):
    root = get_xml(session, "https://37signals.com/feed/jobs.xml")
    ns = "{http://www.w3.org/2005/Atom}"
    if root.tag != ns + "feed":
        raise ScraperError("37signals Atom feed missing")
    for item in root.findall(ns + "entry"):
        links = item.findall(ns + "link")
        link = next((
            element.get("href") for element in links
            if element.get("rel", "alternate") == "alternate"
        ), None)
        if not link:
            raise ScraperError("37signals job link missing")
        element = item.find(ns + "content")
        content = None if element is None else (
            "".join(ET.tostring(child, encoding="unicode") for child in element)
            if len(element) else element.text
        )
        if not content:
            raise ScraperError(f"37signals job content missing for {link}")
        yield record(
            item.findtext(ns + "id"), item.findtext(ns + "title"), link, content,
            "Remote", item.findtext(ns + "published"), True,
        )


def rapid7_jobs(session, queries, known_ids):
    url = "https://careers.rapid7.com/jobs/search"
    seen = set()
    page_number = 1
    while url:
        soup = get_soup(session, url)
        table = soup.select_one("table tbody")
        if table is None:
            raise ScraperError("Rapid7 job table missing; the site may be blocking requests")
        rows = table.select("tr")
        page_links = []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 5:
                raise ScraperError("Rapid7 job columns changed")
            anchor = cells[0].select_one("a[href]")
            if anchor is None:
                raise ScraperError("Rapid7 job link missing")
            job_id = cells[1].get_text(strip=True)
            if not job_id:
                raise ScraperError("Rapid7 requisition identifier missing")
            page_links.append(anchor["href"])
            title = anchor.get_text(" ", strip=True)
            location_items = cells[3].select("li")
            location = "; ".join(
                item.get_text(" ", strip=True) for item in location_items
            ) if location_items else cells[3].get_text(" ", strip=True)
            if not matches(title, queries) or not matches_location({"location": location}, "Boston"):
                continue
            link = urljoin(url, anchor["href"])
            description = ""
            posted = None
            if job_id not in known_ids:
                schema = next(job_postings(get_soup(session, link)), None)
                if schema is None:
                    raise ScraperError(f"Rapid7 JobPosting metadata missing for {job_id}")
                description = schema["description"]
                posted = schema.get("datePosted")
            yield record(
                job_id, title, link, description, location, posted,
                remote_mode(cells[4].get_text(strip=True)),
            )
        if rows:
            check_progress(page_links, seen)
        next_page = next((
            anchor for anchor in soup.select(".pagination a[href]")
            if parse_qs(urlsplit(anchor["href"]).query).get("page") == [str(page_number + 1)]
        ), None)
        url = urljoin(url, next_page["href"]) if next_page else None
        page_number += 1
