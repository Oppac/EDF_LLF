
import sys

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

def get_priorities(wcets):
    priorities = []
    i = len(wcets)
    for i in range(len(wcets)):
        min_wcets = wcets.index(min(wcets))
        priorities.append(min_wcets)
        wcets[min_wcets] = max(wcets)+1
    return priorities

def main():
    offsets = []
    wcets = []
    periods = []

    if (str(sys.argv[1]) == "edf_interval"):
        get_data(sys.argv[2], offsets, wcets, periods)
        priorities = get_priorities(wcets[:])
        print(offsets, wcets, periods)
        print(priorities)



main()
