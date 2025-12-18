import tkinter as tk
from tkinter import messagebox

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

def generate_schedule():
    courses_input = courses_entry.get().strip()
    days_input = days_entry.get().strip()

    if not courses_input:
        messagebox.showerror("Error", "Please enter at least one course.")
        return

    desired_courses = [c.strip() for c in courses_input.split(",")]

    if days_input == "":
        allowed_days = None
    else:
        allowed_days = set(make_daysList(days_input))

    # Filter sections by allowed days
    filtered = {}
    for course, sections in courses_to_sections.items():
        allowed_sections = []
        for sec in sections:
            if days_ofClass(sec, allowed_days):
                allowed_sections.append(sec)
        if allowed_sections:
            filtered[course] = allowed_sections

    results = build_optimal_schedules(
        all_sections,
        filtered,
        desired_courses,
        max_results=5
    )

    output_text.delete("1.0", tk.END)

    if not results:
        output_text.insert(tk.END, "No valid schedules found.\n")
        return

    for i, (score, schedule) in enumerate(results, start=1):
        output_text.insert(tk.END, f"\nSchedule #{i} (score = {score})\n")
        output_text.insert(tk.END, "-" * 40 + "\n")
        for sec in schedule:
            start = minutes_toRealTime(sec["start"])
            end = minutes_toRealTime(sec["end"])
            output_text.insert(
                tk.END,
                f"{sec['course']} Section {sec['section']}: "
                f"{sec['days']} {start}-{end}\n"
            )

def main():
    global all_sections, courses_to_sections
    global window, courses_entry, days_entry, output_text

    # Load the CSV data
    all_sections, courses_to_sections = load_csvfile()

    # Create the window
    window = tk.Tk()
    window.title("DFS Smart Class Scheduler")
    window.geometry("700x500")

    tk.Label(window, text="Courses (comma separated):").pack()
    courses_entry = tk.Entry(window, width=60)
    courses_entry.pack()
    courses_entry.insert(0, "CS 310, ENGL 101")

    tk.Label(window, text="Allowed days (example: TuTh or MWF). Leave empty for all:").pack()
    days_entry = tk.Entry(window, width=20)
    days_entry.pack()

    tk.Button(window, text="Generate Schedule", command=generate_schedule).pack(pady=10)

    output_text = tk.Text(window, height=20, width=80)
    output_text.pack()

    window.mainloop()

if __name__ == "__main__":
    main()