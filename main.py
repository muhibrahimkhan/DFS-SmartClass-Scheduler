from operator import truediv

from data_loader import load_csvfile
from dfs_scheduler import build_optimal_schedules
from conflicts import make_daysList

def minutes_toRealTime(t):
    #converts the minutes from midday we were using till now to real time
    hour = t // 60
    minute = t % 60
    hour_str = str(hour).zfill(2)
    minute_str = str(minute).zfill(2)

    return hour_str + ":" + minute_str

def days_ofClass(section, allowed_days_set):
    #returns true if the section only uses the days from the allowed_days_set

    if allowed_days_set is None:
        return True # None means no restriction on specific days of class
    sec_days = make_daysList(section["days"])
    # if even one of the section days is Not in the allowed days set, reject it
    for d in sec_days:
        if d not in allowed_days_set:
            return False

    return True

def print_schedule(schedule, rank, score):
    print("\n=== Schdule #" + str(rank) + " (score = " + str(score) + ") ===")
    for sec in schedule:
        start_str = minutes_toRealTime(sec["start"])
        end_str = minutes_toRealTime((sec["end"]))

        print(sec["course"] + " Section " + str(sec["section"]) + ": ")
        print(sec["days"] + " " + start_str + " - " + end_str)

def main():
    all_sections, courses_to_sections = load_csvfile()

    print("======= Available Courses ======== \n")
    for c in courses_to_sections.keys():
        print(" - ", c)

    print("Enter the courses you want, separated by commas: ")
    print("\nExample: CSE 121, CSE 122 \n")
    raw_courses = input(">>>>> ")

    desired_courses = []
    for part in raw_courses.split(","):
        code = part.strip()
        if code:
            desired_courses.append(code)

    print("\nEnter the days you are willing to have class on as a single string.")
    print("Use: M, T, W, Th, F (no spaces).")
    print("Examples:")
    print("  MTWThF  -> allow any weekday")
    print("  MWF     -> only Monday/Wednesday/Friday")
    print("  TTh     -> only Tuesday/Thursday")
    print("Or just press Enter to allow ALL days.")
    raw_days = input(">>>>> ").strip()

    if raw_days == "":
        allowed_days_set = None

    else:
        allowed_days_list = make_daysList(raw_days)
        allowed_days_set = set(allowed_days_list)
        print("\nYou want classes on these days: ", allowed_days_set)

    # filer sections by allowed days
    filtered_courses_to_sections = {}

    for course_code, sections in courses_to_sections.items():
        allowed_sections = []
        for sec in sections:
            if days_ofClass(sec, allowed_days_set):
                allowed_sections.append(sec)

        #Only keep sections that have at least one allowed section
        if allowed_sections:
            filtered_courses_to_sections[course_code] = allowed_sections

    top_schedules = build_optimal_schedules(all_sections,
                    filtered_courses_to_sections, desired_courses, max_results=5, )
    if not top_schedules:
        print("\nNo valid schedules found with those courses and days selected")
        return

    print("\nFound", len(top_schedules), "schedule(s). Showing best first:")

    for rank, (score, schedule) in enumerate(top_schedules, start=1):
        print_schedule(schedule, rank, score)


if __name__ == "__main__":
    main()


