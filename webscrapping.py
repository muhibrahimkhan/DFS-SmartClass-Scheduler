import requests
from bs4 import BeautifulSoup
import csv


url = "https://www.washington.edu/students/timeschd/pub/WIN2026/cse.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
page_text = soup.get_text()
lines = page_text.splitlines()
#This list will store all the open sections we find
open_sections = []
#This will store the current course we are going through
current_course = ""
#Count how many open sections we saved per course
sections_per_course = {}

#Go through the lines and look for courses and sections that are open
for line in lines:
    line = line.strip()   # remove spaces at the edges

#Any line that starts with CSE should be split
    if line.startswith("CSE"):
        parts = line.split()

        # Make sure the line has at least "CSE" and a course number
        if len(parts) >= 2:
            current_course = parts[0] + " " + parts[1]
        else:
            current_course = ""
        continue

# Helps to store the classes that are open
    if "Open" in line and current_course != "":
        parts = line.split()

# Save section name and days
        section = parts[1]
        days = parts[3]

        # Find the time by looking up for "-"
        timing = ""
        for p in parts:
            if "-" in p:
                timing = p
                break
        # If we couldn't find a timing, skip this line
        if timing == "":
            continue
        # Split timing into start and end time
        start_time, end_time = timing.split("-")

        # Only save 3 open sections per course or data set might become too large for this project
        if current_course not in sections_per_course:
            sections_per_course[current_course] = 0

        if sections_per_course[current_course] >= 3:
            continue  # already have 3 sections for this course

        sections_per_course[current_course] += 1

        # Save the section information
        open_sections.append({
            "course_code": current_course,
            "section": section,
            "days": days,
            "start_time": start_time,
            "end_time": end_time
        })
# Print everything we found to show everything is working
for sec in open_sections:
    print("Course:", sec["course_code"])
    print("Section:", sec["section"])
    print("Days:", sec["days"])
    print("Start Time:", sec["start_time"])
    print("End Time:", sec["end_time"])
    print()

# Save into a CSV file
with open("uw_cse_open_sections.csv", "w", newline="") as f:
    writer = csv.writer(f)

    # Write the header row
    writer.writerow(["course_code", "section", "days", "start_time", "end_time"])

    # Write each section's data
    for sec in open_sections:
        writer.writerow([
            sec["course_code"],
            sec["section"],
            sec["days"],
            sec["start_time"],
            sec["end_time"]
        ])
#Print so we know the programme is completed
print("Saved file: uw_cse_open_sections.csv")
