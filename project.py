import random
import sys
import time
from numpy import lcm

from task import Task

def get_data(input_file, offsets, wcets, periods):
    try:
        with open(input_file, 'r') as file:
            for line in file:
                line = line.replace(" ", "")
                line = line.replace("\n", "")
                line_arr = line.split(";")

                if len(line_arr) == 3:
                    offsets.append(int(line_arr[0]))
                    wcets.append(int(line_arr[1]))
                    periods.append(int(line_arr[2]))
        return offsets, wcets, periods

    except OSError:
        print('cannot open', input_file)

def edf_priorities(periods):
    priorities = []
    tmp_periods = periods[:]
    for i in range(len(tmp_periods)):
        min_deadline = tmp_periods.index(min(tmp_periods))
        priorities.append(min_deadline)
        tmp_periods[min_deadline] = max(tmp_periods)+1
    return priorities

def edf_feasibility_interval(offsets, periods):
    return max(offsets) + (2 * lcm.reduce(periods))

def edf_utility(wcets, periods):
    interval = 0
    for i in range(len(wcets)):
        interval += wcets[i] / float(periods[i])
    return interval

def draft_generator(tasks, goal_utility, output):
    offsets, wcets, periods, gen_utility = new_system(tasks)
    while not (gen_utility > (goal_utility-0.01) and gen_utility < (goal_utility+0.01)):
        offsets, wcets, periods, gen_utility = new_system(tasks)
    output_system(offsets, wcets, periods, output)

def output_system(offsets, wcets, periods, output):
    try:
        with open(output, 'w+') as file:
            for line in range(len(offsets)):
                file.write("{}; {}; {}\n".format(
                offsets[line], wcets[line], periods[line]))
    except OSError:
        print('cannot open', output)

def new_system(tasks):
    offsets = []
    wcets = []
    periods = []
    for i in range(tasks):
        offsets.append(random.randint(0, 2))
        wcets.append(random.randint(1, 3))
        periods.append(random.randint(8, 20))
        gen_utility = edf_utility(wcets, periods)
    return offsets, wcets, periods, gen_utility

def start_scheduler(tasks, start, end):
    preemptions = 0
    print("TODO")
    print("Schedule from: {} to: {} ; {} tasks".format(start, end, len(tasks)))

    for time in range(start, end):
        for i in range(len(tasks)):
            if tasks[i].period == time:
                if not tasks[i].completed:
                    print("{}: Task {} misses a deadline".format(time, tasks[i].name))
                    print("End: {} preemptions".format(preemptions))
                    return
                else:
                    tasks[i].period += tasks[i].period
                    print("{}: Arrival of task {}".format(time, tasks[i].name))
                

    print("End: {} preemptions".format(preemptions))


def main():
    offsets = []
    wcets = []
    periods = []

    if len(sys.argv) > 1:
        if (str(sys.argv[1]) == "edf_interval"):
            if len(sys.argv) > 2:
                get_data(sys.argv[2], offsets, wcets, periods)
                priorities = get_priorities(periods[:])
                interval = edf_feasibility_interval(offsets, periods)
                print("{},{}".format(0, interval))
            else:
                print("Usage: python edf_inteval input_file")
        elif (str(sys.argv[1]) == "gen"):
            if len(sys.argv) > 3:
                nb_tasks = int(sys.argv[2])
                goal_utility = float(sys.argv[3])/100
                output_file = sys.argv[4]
                draft_generator(nb_tasks, goal_utility, output_file)
            else:
                print("Usage: python project.py gen nb_tasks utility output")
        elif (str(sys.argv[1]) == "edf"):
            if len(sys.argv) > 4:
                get_data(sys.argv[2], offsets, wcets, periods)
                start = int(sys.argv[3])
                end = int(sys.argv[4])
                priorities = edf_priorities(periods)

                tasks = [Task(offsets[i], wcets[i], periods[i], priorities[i], "T"+str(i))
                for i in range(len(offsets))]

                start_scheduler(tasks, start, end)
            else:
                print("Usage: python project.py edf input_file start stop")
        elif (str(sys.argv[1]) == "llf"):
            if len(sys.argv) > 4:
                pass
            else:
                print("Usage: python project.py llf input_file start stop")

start_time = time.time()
main()
#print("--- %s seconds ---" %(time.time() - start_time))
