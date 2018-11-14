import random
import sys
import time
from numpy import lcm

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


def get_priorities(periods):
    priorities = []
    for i in range(len(periods)):
        min_deadline = periods.index(min(periods))
        priorities.append(min_deadline)
        periods[min_deadline] = max(periods)+1
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
    print(offsets, wcets, periods)
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
            if len(sys.argv) > 4:
                nb_tasks = int(sys.argv[2])
                goal_utility = float(sys.argv[3])/100
                output_file = sys.argv[4]
                draft_generator(nb_tasks, goal_utility, output_file)
            else:
                print("Usage: python project.py gen nb_tasks utility output")

start_time = time.time()
main()
print("--- %s seconds ---" %(time.time() - start_time))
