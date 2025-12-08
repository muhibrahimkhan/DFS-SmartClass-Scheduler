#This file contains the greedy algorithm scoring function
#Scoring function can give a numeric value to a completed schedule
#Lower score = better the schedule
#Greedy Ideas: 1. We prefer fewer days with classes 2. We prefer smaller and lesser gaps between classes
#Final Score = total gaps + 60 * days with classes

from conflicts import make_daysList

def score_schedule(schedule):

    if not schedule:
        #return almost infinity for "no schedule"
        return 10**8

    # Group time intervals by day
    by_day = {}

    for sec in schedule:
        day = make_daysList(sec["days"])
        for d in day:
            if d not in by_day:
                by_day[d] = []
            by_day[d].append((sec["start"], sec["end"]))

    total_gaps = 0
    days_with_classes = 0

    for day, intervals in by_day.items():
        days_with_classes += 1

        # Sort intervals by start time on that day
        #intervals contains tuples with start and end time of each day
        #They are sorted in place
        intervals.sort(key=lambda pair: pair[0])

        # Add up the gaps between classes on this day
        for i in range(len(intervals) - 1):
            current_end = intervals[i][1]
            next_start = intervals[i + 1][0]
            gap = next_start - current_end
            if gap > 0:
                total_gaps += gap

    # Greedy scoring:
    # 1 point per minute of gap
    # 60 points per distinct day with classes
    score = total_gaps + 60 * days_with_classes
    return score