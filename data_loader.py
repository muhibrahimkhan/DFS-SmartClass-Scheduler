# This project uses an optimized CSV loader that builds two data structures
# while reading the file: 1. a list of all sections, and 2. a dictionary
# (hash map) that groups sections by course code. Reading the CSV still takes
# O(n) time because every row must be processed, but storing sections in a
# dictionary makes later lookups much faster: retrieving all sections for a
# course becomes an O(1) average-time operation instead of searching through
# the entire list every time (which would be O(n)). This greatly improves the
# efficiency of the DFS scheduling algorithm, because DFS frequently needs to
# access all sections for each course. Using a hash map reduces repeated work
# and keeps the algorithm clean, fast, and well-structured.


import csv

def time_toMinutes(t):
    #This function can be used to convert time to minutes from midnight

    t = t.strip()
    digits = ""
    for time in t:
        if time.isdigit():
            digits += time

    #Make sure the time are converted into minutes properly
    #By knowing the last 2 digits are minutes, everything before is the hour
    if len(digits) <= 2:
        hour = int(digits)
        minute = 0
    else:
        hour = int(digits[:-2])
        minute = int(digits[-2:])

    return (hour*60) + minute


#Following function reads the csv file and gives a list of section dictionaries.
def load_csvfile(filename = "uw_cse_open_sections.csv"):

    #Will fill this empty list with class sections dictionary
    sections_list =[]
    coursesToSections = {} #dict: course_code -> list of sections

    # Open the csv file for reading and close it afterwords
    with open(filename, newline="", encoding = "utf-8") as f:

        #Read the file row by row
        reader = csv.DictReader(f)

        #loop over every row in the csv file -> O(n)
        for row in reader:
            course_code = row["course_code"].strip()
            section_id = row["section"].strip()
            days = row["days"].strip()
            start_t = row["start_time"].strip()
            end_t = row["end_time"].strip()

            #convert times to minutes from midnight
            start_t = time_toMinutes(start_t)
            end_t = time_toMinutes(end_t)

            # Building a dictionary for sections
            sec = {
                "course" : course_code,
                "section" : section_id,
                "days": days,
                "start": start_t,
                "end" : end_t

            }

            #add them to the section list
            sections_list.append(sec)

            #add into the dictionary for quick lookup by course
            if course_code not in coursesToSections:
                coursesToSections[course_code] = []

            coursesToSections[course_code].append(sec)

        return sections_list, coursesToSections


