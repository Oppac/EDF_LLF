import sys
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


def main():
    offsets = []
    wcets = []
    periods = []

    if (str(sys.argv[1]) == "edf_interval"):
        get_data(sys.argv[2], offsets, wcets, periods)
        priorities = get_priorities(periods[:])
        interval = edf_feasibility_interval(offsets, periods)

        print(offsets, wcets, periods)
        print(priorities)
        print("{},{}".format(0, interval))



main()
