import random
import sys
import time
from math import gcd

class Task():
    def __init__(self, offset, wcet, period, id):
        self.offset = offset
        self.wcet = wcet
        self.period = period
        #self.priority = self.offset + (job_nb-1) * period
        self.id = id

        self.completed = False
        self.task_start_time = 0
        self.already_done = 0
        self.job_nb = 0

    def change_priority(self):
        self.priority = self.offset + (job_nb-1) * initial_period

    def check_task_correctness(self):
        ''' Check if the parsed tasks pass basic correctness tests '''
        if (self.wcet > self.period):
            print("Warning: Worst case execution time of task {} is superior" \
             " to the period".format(self.id))
        if (self.offset > self.period):
            print("Warning: The offset of task {} is superior" \
            " to the period".format(self.id))
        if (self.wcet == 0):
            print("Warning: The worst execution time of task {} is equal" \
            " to zero".format(self.id))
        elif (self.period == 0):
             print("Warning: The period of task {} is equal" \
             " to zero".format(self.id))

#######################################################################################

class Scheduler():
    def __init__(self, start, end, tasks):
        self.preemptions = 0
        self.start = start
        self.end = end
        self.tasks = tasks
        self.pending_tasks = [tasks[0], tasks[2], tasks[1]]
        self.current_pending = self.pending_tasks[0]

    def start_msg(self):
        print("TODO")
        print("Schedule from: {} to: {} ; {} tasks".format(self.start, self.end, len(self.tasks)))

    def end_msg(self):
        print("End: {} preemptions".format(self.preemptions))

    def update_priorities(self):
            priorities = []
            periods = [self.tasks[i].period for i in range(len(self.tasks))]
            for i in range(len(periods)):
                min_deadline = periods.index(min(periods))
                priorities.append(min_deadline)
                periods[min_deadline] = max(periods)+1
            return priorities

    def check_deadlines(self, time):
        for i in range(len(self.tasks)):
            if self.tasks[i].period == time:
                if not self.tasks[i].completed:
                    print("{}: Task {}J{} misses a deadline".format(
                          time, self.tasks[i].name, self.tasks[i].job_nb))
                    return True
                else:
                    self.tasks[i].period += self.tasks[i].period
                    self.tasks[i].job_nb += 1
                    self.tasks[i].completed = False
                    print("{}-{}: Task {}J{} ".format(self.tasks[i].task_start_time,
                          time+1, self.tasks[i].name, self.tasks[i].job_nb))
        return False

    def schedule(self, time):
        for i in range(len(self.tasks)):
            if not self.pending_tasks[0].completed:
                if self.pending_tasks[0].already_done == 0:
                    self.pending_tasks[0].task_start_time = time
                    print("{}: Arrival of task {}J{}".format(
                          time, self.pending_tasks[0].name, self.pending_tasks[0].job_nb))
                self.pending_tasks[0].already_done += 1
                if self.pending_tasks[0].already_done == self.pending_tasks[0].wcet:
                    self.pending_tasks[0].completed = True
                    self.pending_tasks[0].already_done = 0
                    break
                else:
                    break
            else:
                self.pending_tasks.append(self.pending_tasks.pop(
                             self.pending_tasks.index(self.pending_tasks[0])))


    def scheduling(self):
        print(self.update_priorities())
        for time in range(self.start, self.end):
            self.schedule(time)
            if self.check_deadlines(time):
                return
            #update_priorities()

##########################################################################################


def get_data(input_file, tasks_list):
    ''' Parse the data from the given input file'''
    try:
        with open(input_file, 'r') as file:
            for line in file:
                line = line.replace(" ", "")
                line = line.replace("\n", "")
                line_arr = line.split(";")

                if len(line_arr) == 3:
                    try:
                        line_arr[0] = int(line_arr[0])
                        line_arr[1] = int(line_arr[1])
                        line_arr[2] = int(line_arr[2])
                    except ValueError:
                        print("Could not properly load data from", sys.argv[2])
                        sys.exit("Error: Data must be integers only")
                    tasks_list.append(Task(line_arr[0], line_arr[1], line_arr[2], "T"+str(len(tasks_list))))
                    tasks_list[len(tasks_list)-1].check_task_correctness()
                elif len(line_arr) > 1:
                    print("Could not properly load data from", sys.argv[2])
                    sys.exit("Error: {} is an incorrect data format".format(line))
            return tasks_list
    except OSError:
        print("Could not properly load data from", sys.argv[2])
        sys.exit("Error: Cannot open {}".format(input_file))

############################################################################################################

# def edf_priorities(periods):
#     priorities = []
#     tmp_periods = periods[:]
#     for i in range(len(tmp_periods)):
#         min_deadline = tmp_periods.index(min(tmp_periods))
#         priorities.append(min_deadline)
#         tmp_periods[min_deadline] = max(tmp_periods)+1
#     return priorities

def compute_lcm(periods):
    '''Compute the lcm of the periods (Credit: Ananay Mital from Stack Overflow) '''
    lcm = periods[0]
    for i in periods[1:]:
        lcm = int((lcm * i) / gcd(lcm, i))
    return lcm

def edf_feasibility_interval(tasks_list):
    '''Return the feasibility interval of the list of tasks'''
    offsets = [tasks_list[i].offset for i in range(len(tasks_list))]
    periods = [tasks_list[i].period for i in range(len(tasks_list))]
    return max(offsets) + (2 * compute_lcm(periods))

def edf_utility(wcets, periods):
    interval = 0
    for i in range(len(wcets)):
        interval += wcets[i] / float(periods[i])
    return interval

###############################################################################################

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

############################################################################################

def start_scheduler(tasks, start, end):

    edf_sceduler = Scheduler(start, end, tasks)
    edf_sceduler.start_msg()
    edf_sceduler.scheduling()
    edf_sceduler.end_msg()

def main():
    tasks_list = []

    if len(sys.argv) > 1:
        if (str(sys.argv[1]) == "edf_interval"):
            if len(sys.argv) > 2:
                get_data(sys.argv[2], tasks_list)
                #priorities = edf_priorities(periods[:])
                interval = edf_feasibility_interval(tasks_list)
                print("{},{}".format(0, interval))
            else:
                print("Usage: python project.py edf_interval input_file")
        elif (str(sys.argv[1]) == "gen"):
            if len(sys.argv) > 3:
                nb_tasks = int(sys.argv[2])
                goal_utility = float(sys.argv[3])/100
                output_file = sys.argv[4]
                draft_generator(nb_tasks, goal_utility, output_file)
            else:
                print("Usage: python project.py gen nb_tasks utility output_file")
        elif (str(sys.argv[1]) == "edf"):
            if len(sys.argv) > 4:
                get_data(sys.argv[2], tasks_list)
                try:
                    start = int(sys.argv[3])
                    end = int(sys.argv[4])
                    if (start < 0) or (end < start):
                        raise
                except:
                    sys.exit("Please, enter valid start and end times")

                try:
                    priorities = edf_priorities(periods)
                    tasks = [Task(offsets[i], wcets[i], periods[i], priorities[i], "T"+str(i))
                    for i in range(len(offsets))]
                    start_scheduler(tasks, start, end)
                except:
                    print("Error during the scheduling")
            else:
                print("Usage: python project.py edf input_file start stop")
        elif (str(sys.argv[1]) == "llf"):
            if len(sys.argv) > 4:
                pass
            else:
                print("Usage: python project.py llf input_file start stop")
        else:
            print("Unknown option", sys.argv[1])
            print("Edf interval: python project.py edf_interval input_file")
            print("Generator: python project.py gen nb_tasks utility output_file")
            print("Scheduler: python project.py edf|llf input_file start stop")
    else:
        print("Edf interval: python project.py edf_interval input_file")
        print("Generator: python project.py gen nb_tasks utility output_file")
        print("Scheduler: python project.py edf|llf input_file start stop")

if __name__ == "__main__":
    #start_time = time.time()
    main()
    #print("--- %s seconds ---" %(time.time() - start_time))
