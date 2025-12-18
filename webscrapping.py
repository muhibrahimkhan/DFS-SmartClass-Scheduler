import json, os, re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

def minutes_to_24h(mins):
    hours = mins // 60
    minutes = mins % 60

    return str(hours).zfill(2) + ":" + str(minutes).zfill(2)

import csv

def write_sections_csv(rows, out_path="uw_cse_open_sections.csv"):
    # Open a file to write into
    f = open(out_path, "w", newline="", encoding="utf-8")

    # Create a CSV writer that knows the column names
    writer = csv.DictWriter(f, fieldnames=["course_code", "section", "days", "start_time", "end_time"])

    # Write the header row (column names)
    writer.writeheader()

    # Write each row of data
    for row in rows:
        writer.writerow(row)

    # Close the file when done
    f.close()


def scrape_subjects(driver):
    # Load the main subject listing page
    driver.get("https://courses.umb.edu/course_catalog/listing/ugrd")
    # Wait until subject list elements are present
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#content ul li")))
    subjects = []
    # Loop through each subject list item
    for li in driver.find_elements(By.CSS_SELECTOR, "div#content ul li"):
        try:
            a = li.find_element(By.TAG_NAME, "a")
            # Extract subject code from URL
            code = a.get_attribute("href").split('/')[-1]
            if code.startswith("ugrd_") and code.endswith("_all"):
                code = code[5:-4]  # Clean code, e.g., "ugrd_cs_all" -> "cs"
            else:
                code = ""
            # Add subject info dict to list
            subjects.append({"code": code, "name": a.text.strip(), "url": a.get_attribute("href")})
        except:
            pass  # Ignore errors silently
    return subjects

def scrape_courses_for_subject(driver, code):
    # Load courses page for a given subject code
    driver.get(f"https://courses.umb.edu/course_catalog/courses/ugrd_{code.lower()}_all")
    # Wait until course list elements are present
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.showHideList li")))
    courses = []
    # Loop through each course listing
    for li in driver.find_elements(By.CSS_SELECTOR, "ul.showHideList li"):
        try:
            header = li.find_element(By.CLASS_NAME, "class-info-rows").text.strip().rstrip(" +")
            parts = header.split()
            number = parts[1] if len(parts) > 1 else ""  # Course number
            title = " ".join(parts[2:]) if len(parts) > 2 else ""  # Course title
            extra = li.find_element(By.CLASS_NAME, "extra-info")
            # Attempt to find "More Info" URL
            try:
                more_info = extra.find_element(By.XPATH, ".//a[text()='More Info']").get_attribute("href")
            except:
                more_info = None
            semesters = [{"name": "TBA", "url": None}]  # Default if no semesters found
            try:
                # Look for offered semesters list
                ul = extra.find_element(By.CSS_SELECTOR, "ul.course-info-listing-padding-bottom")
                semesters = []
                for sem_li in ul.find_elements(By.TAG_NAME, "li"):
                    try:
                        a = sem_li.find_element(By.TAG_NAME, "a")
                        semesters.append({"name": a.get_attribute("textContent").strip(), "url": a.get_attribute("href")})
                    except:
                        semesters.append({"name": "TBA", "url": None})
            except:
                pass  # If semester info not found, keep default
            # Append course dictionary
            courses.append({"code": number, "title": title, "more_info_url": more_info, "offered_semesters": semesters})
        except:
            pass  # Ignore course parsing errors silently

    return courses

def parse_days(s):
    # Parse day abbreviations from string (e.g., 'MWF', 'TuTh')
    days, i = [], 0
    while i < len(s):
        if s[i:i+2] in ("Tu","Th"):
            days.append(s[i:i+2])
            i += 2
        else:
            days.append(s[i])
            i += 1
    return days

def convert_to_minutes(t):
    # Convert a time string like '5:30 pm' to minutes since midnight
    m = re.match(r"(\d{1,2}):(\d{2})\s*(am|pm)?", t.strip().lower())
    if not m:
        return None, None
    h, mm, mer = int(m.group(1)), int(m.group(2)), m.group(3)
    if mer == "am" and h == 12:
        h = 0
    elif mer == "pm" and h != 12:
        h += 12
    return h*60 + mm, mer

def parse_time_range(time_raw):
    # Parse a time range string like '5:30 - 8:15 pm' into start and end minutes
    if not isinstance(time_raw, str):
        return None, None

    raw = time_raw.strip().lower()
    if not raw:
        return None, None

    parts = re.split(r"\s*-\s*", raw, maxsplit=1)
    if len(parts) != 2:
        return None, None

    start_str, end_str = parts
    start_min, start_mer = convert_to_minutes(start_str)
    end_min, end_mer = convert_to_minutes(end_str)
    if start_min is None or end_min is None:
        return None, None

    VALID = {50, 75, 165}  # Valid class durations in minutes

    def dur(s):
        d = end_min - s
        return d + 1440 if d < 0 else d

    # If start meridian missing but end meridian present, try to infer start meridian by flipping 12 hours
    if start_mer is None and end_mer and dur(start_min) not in VALID:
        flip = (start_min + (720 if end_mer == "am" else -720)) % 1440
        if dur(flip) in VALID:
            start_min = flip

    return start_min, end_min

def scrape_sections_for_semester(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    sections = []
    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "tr.class-info-rows:not(.class-info-rows-show-extra-background)"
    )

    for row in rows:
        try:
            section = row.find_element(By.CSS_SELECTOR, "td[data-label='Section']").text.strip()
            sched_html = row.find_element(
                By.CSS_SELECTOR, "td[data-label='Schedule/Time']"
            ).get_attribute("innerHTML").strip()

            if "<br>" in sched_html:
                days_raw, time_raw = sched_html.split("<br>", 1)
            else:
                days_raw, time_raw = sched_html, ""

            days_str = days_raw.strip()
            start_min, end_min = parse_time_range(time_raw)

            # Skip TBA / invalid times
            if not days_str or start_min is None or end_min is None:
                continue

            sections.append({
                "section": section,
                "days_str": days_str,
                "start_min": start_min,
                "end_min": end_min
            })

        except Exception:
            continue

    return sections


def scrape_sections_for_courses(driver, courses_path):
    # Load courses JSON and scrape sections for each semester's URL
    with open(courses_path, "r", encoding="utf-8") as f:
        courses = json.load(f)
    for course in courses:
        for semester in course.get("offered_semesters", []):
            if semester.get("url"):
                semester["sections"] = scrape_sections_for_semester(driver, semester["url"])
            else:
                semester["sections"] = []
    # Save updated courses with section info back to JSON
    with open(courses_path, "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=4)

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # more reliable headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service()  # Selenium Manager will try to provide a driver
    driver = webdriver.Chrome(service=service, options=options)

    all_rows = []
    seen = set()  # prevent duplicates (course_code, section, days, start, end)

    try:
        subjects = scrape_subjects(driver)

        for subj in subjects:
            subject_code = subj["code"]
            courses = scrape_courses_for_subject(driver, subject_code)

            for course in courses:
                # Make a scheduler-friendly course_code like "CS 310"
                course_code = f"{subject_code.upper()} {course['code']}"

                for sem in course.get("offered_semesters", []):
                    sem_url = sem.get("url")
                    if not sem_url:
                        continue

                    sections = scrape_sections_for_semester(driver, sem_url)

                    for s in sections:
                        key = (course_code, s["section"], s["days_str"], s["start_min"], s["end_min"])
                        if key in seen:
                            continue
                        seen.add(key)

                        all_rows.append({
                            "course_code": course_code,
                            "section": s["section"],
                            "days": s["days_str"],
                            "start_time": minutes_to_24h(s["start_min"]),  # 24h format for data_loader.py
                            "end_time": minutes_to_24h(s["end_min"])
                        })

    finally:
        driver.quit()

    # Write CSV where your existing scheduler expects it by default
    write_sections_csv(all_rows, out_path="uw_cse_open_sections.csv")
    print(f"Done. Wrote {len(all_rows)} sections to uw_cse_open_sections.csv")


if __name__ == "__main__":
    main()
