# This file contains helper functions to check if two classes sections
# overlaps in time. It works with the dictionaries created in data_loader
from pandas.core.array_algos.transforms import shift


def make_daysList(days_str):

    # Turning strings like "MFW" into a list like ["M", "W", "F"}
    days_str = days_str.strip()
    result = []

    i = 0
    while i < len(days_str):
        if days_str[i] == "T" and days_str[i+1] in ("h", "H"):
            result.append("Th")
            i += 2
        else:
            result.append(days_str[i])
            i += 1

    return result

def sections_overlap(sec1, sec2):
    # Returns True if two sections have some time overlap

    days_sec1 = make_daysList(sec1["days"])
    days_sec2 = make_daysList(sec2["days"])

    # First check if they share any day
    share_day = False
    for d1 in days_sec1:
        if d1 in days_sec2:
            share_day = True
            break

    if not share_day:
        return False

    startT1 = sec1["start"]
    startT2 = sec2["start"]
    endT1 = sec1["end"]
    endT2 = sec2["end"]

    if (startT1 < endT2) and (startT2 < endT1):
        return True

    return False

def conflicts_with_schedule(schedule, new_sec):
    #Checks if new section conflicts with any section already in the schedule

    for sec in schedule:
        if sections_overlap(sec, new_sec):
            return True

    return False
