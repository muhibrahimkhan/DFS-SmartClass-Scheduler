from data_loader import load_csvfile
from conflicts import conflicts_with_schedule
from greedyalgo_scroing import score_schedule



def dfs_schedule(courses_list,index, courses_to_sections, current_schedule, best_schedule,max_result):

    # Base case to avoid going deeper: we have chosen a section for every course
    if index == len(courses_list):
        score = score_schedule(current_schedule)
        schedule_copy = list(current_schedule) #make a copy so backtracking doesnt change it

        add_schedule(best_schedule, score, schedule_copy, max_result)
        return

    #choose a section for the next course
    course_code = courses_list[index]
    possible_sections = courses_to_sections.get(course_code, []) #get all possible section for course

    #Greedy Algorithm, which try earlier sections first by time
    def section_start(sec):
        return sec["start"]

    possible_sections = sorted(possible_sections, key=section_start)

    #Try each section for this course
    for sec in possible_sections:
        #if it conflicts with current schedule skip it
        if conflicts_with_schedule(current_schedule, sec):
            continue
        current_schedule.append(sec)

        #recursively move on to the next course
        dfs_schedule(courses_list, index + 1, courses_to_sections, current_schedule, best_schedule, max_result)

        #Execute backtracking by removing the last chosen section
        current_schedule.pop()

def add_schedule(best_schedule, score, schedule, max_results):
    # Helper function that keep best schedules as a small sorted list

    # If we have not filled up best_schedules yet, just add it
    if len(best_schedule) < max_results:
        best_schedule.append((score, schedule))
    else:
        # Find the worst (highest) score currently stored
        worst_index = 0
        worst_score = best_schedule[0][0]
        for i in range(1, len(best_schedule)):
            if best_schedule[i][0] > worst_score:
                worst_score = best_schedule[i][0]
                worst_index = i

        # If this new schedule is better than the worst one, replace it
        if score < worst_score:
            best_schedule[worst_index] = (score, schedule)

    # Keep the list sorted by score (best first)
    best_schedule.sort(key=lambda pair: pair[0])

def build_optimal_schedules(all_sections, courses_to_sections, desired_courses, max_results=5):

    # Filter desired courses to ones that actually exist
    filtered_desired = []
    for code in desired_courses:
        if code in courses_to_sections:
            filtered_desired.append(code)
        else:
            print("Warning: no open sections found for course")

    if not filtered_desired:
        print("No valid courses to schedule.")
        return []

    # Run DFS to search all valid schedules
    best_schedules = []

    dfs_schedule(
        courses_list=filtered_desired,
        index=0,
        courses_to_sections=courses_to_sections,
        current_schedule=[],
        best_schedule=best_schedules,
        max_result=max_results,
    )
    return best_schedules
