import random
import sys
import time
from math import gcd

class Task():
    def __init__(self, offset, wcet, period, id):
        self.offset = offset
        self.wcet = wcet
        self.period = period
        self.next_deadline = period
        self.id = id

        self.completed = False
        self.already_done = 0
        self.job_start = 0
        self.job_nb = 0
        ### TODO #####
        self.priority = self.next_deadline
        ##########

    ### ???? ####
    def update_priority(self):
        self.priority = self.next_deadline

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
    def __init__(self, tasks, start, end):
        self.preemptions = 0
        self.start = start
        self.end = end
        self.tasks = tasks
        self.previous_task = self.get_highest_priority()

    def start_msg(self):
        print("TODO")
        print("Schedule from: {} to: {} ; {} tasks".format(self.start, self.end, len(self.tasks)))

    def end_msg(self):
        print("End: {} preemptions".format(self.preemptions))

    def get_highest_priority(self):
        priorities = self.tasks[:]
        try:
            hp_task = min(priorities, key=lambda task: task.priority)
            while hp_task.completed:
                priorities.remove(hp_task)
                hp_task = min(priorities, key=lambda task: task.priority)
            return hp_task
        except:
            return "empty"

    def check_deadlines(self, time):
        for i in range(len(self.tasks)):
            if self.tasks[i].next_deadline == time:
                if not self.tasks[i].completed:
                    print("{}: Job {}J{} misses a deadline".format(
                         time, self.tasks[i].id, self.tasks[i].job_nb))
                    #return True
                else:
                    self.tasks[i].next_deadline += self.tasks[i].period
                    self.tasks[i].job_nb += 1
                    self.tasks[i].completed = False
        return False

    def schedule(self, time, task):
        if task != "empty":
            if not task.id is self.previous_task.id:
                if not self.previous_task.completed:
                    print("{}-{}: {}J{} Hello".format(self.previous_task.job_start,
                        time+1, self.previous_task.id, self.previous_task.job_nb))
                    self.previous_task.job_start = time
                    self.preemptions += 1
            if task.already_done == 0:
                task.job_start = time
                print("{}: Arrival of job {}J{}".format(time, task.id, task.job_nb))
            task.already_done += 1
            if task.already_done == task.wcet:
                task.completed = True
                task.already_done = 0
                print("{}-{}: {}J{} ".format(task.job_start,
                    time+1, task.id, task.job_nb))
            return task
        else:
            return self.previous_task


    def scheduling(self):
        for time in range(self.start, self.end):
            for task in self.tasks:
                task.update_priority()
            if self.check_deadlines(time):
                return
            self.previous_task = self.schedule(time, self.get_highest_priority())

##########################################################################################


def get_data(input_file, tasks_list):
    ''' Parse the data from the given input file.'''
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

def compute_lcm(periods):
    '''Compute the lcm of the periods (Credit: Ananay Mital from Stack Overflow).'''
    lcm = periods[0]
    for i in periods[1:]:
        lcm = int((lcm * i) / gcd(lcm, i))
    return lcm

def edf_feasibility_interval(tasks_list):
    '''Return the feasibility interval of the list of tasks.'''
    offsets = [tasks_list[i].offset for i in range(len(tasks_list))]
    periods = [tasks_list[i].period for i in range(len(tasks_list))]
    return max(offsets) + (2 * compute_lcm(periods))

###############################################################################################

def generator(tasks, goal_utility, output):
    '''Generate a new system until one has the required utility then write it to the output file.'''
    offsets, wcets, periods, gen_utility = new_system(tasks)
    while not (gen_utility > (goal_utility-0.01) and gen_utility < (goal_utility+0.01)):
        offsets, wcets, periods, gen_utility = new_system(tasks)
    output_system(offsets, wcets, periods, output)

def output_system(offsets, wcets, periods, output):
    '''Write the generated system to the output file. Overwrite if necessary.'''
    try:
        with open(output, 'w+') as file:
            for line in range(len(offsets)):
                file.write("{}; {}; {}\n".format(
                offsets[line], wcets[line], periods[line]))
    except OSError:
        sys.exit("Error: Cannot open {}".format(output))

def new_system(tasks):
    '''Generate a new system. Limits are arbiraries.'''
    offsets = []
    wcets = []
    periods = []
    for i in range(tasks):
        offsets.append(random.randint(0, 10))
        wcets.append(random.randint(1, 50))
        periods.append(random.randint(8, 100))
        gen_utility = edf_utility(wcets, periods)
    return offsets, wcets, periods, gen_utility

def edf_utility(wcets, periods):
    '''Calculate the utility of the system.'''
    interval = 0
    for i in range(len(wcets)):
        interval += wcets[i] / float(periods[i])
    return interval

############################################################################################

def options_error():
    print("Edf interval: python project.py edf_interval input_file")
    print("Generator: python project.py gen nb_tasks utility output_file")
    print("Scheduler: python project.py edf|llf input_file start stop")

def main():
    tasks_list = []

    if len(sys.argv) > 1:

        #Edf interval option
        if (str(sys.argv[1]) == "edf_interval"):
            if len(sys.argv) > 2:
                get_data(sys.argv[2], tasks_list)
                print("{},{}".format(0, edf_feasibility_interval(tasks_list)))
            else:
                print("Usage: python project.py edf_interval input_file")

        #Generator option
        elif (str(sys.argv[1]) == "gen"):
            if len(sys.argv) > 3:
                try:
                    nb_tasks = int(sys.argv[2])
                    goal_utility = float(sys.argv[3])/100
                except:
                    sys.exit("Number of tasks and utility must be numbers")
                generator(nb_tasks, goal_utility, sys.argv[4])
            else:
                print("Usage: python project.py gen nb_tasks utility output_file")

        #EDF scheduler option
        elif (str(sys.argv[1]) == "edf"):
            if len(sys.argv) > 4:
                get_data(sys.argv[2], tasks_list)
                try:
                    start = int(sys.argv[3])
                    end = int(sys.argv[4])
                    if (start < 0) or (end < start):
                        raise
                except:
                    sys.exit("Invalid start and end times")
                #try:
                edf_sceduler = Scheduler(tasks_list, start, end)
                edf_sceduler.start_msg()
                edf_sceduler.scheduling()
                edf_sceduler.end_msg()
                #except:
                    #print("Error during the scheduling")
            else:
                print("Usage: python project.py edf input_file start stop")

        #LLF scheduler option
        elif (str(sys.argv[1]) == "llf"):
            if len(sys.argv) > 4:
                pass
            else:
                print("Usage: python project.py llf input_file start stop")

        else:
            print("Unknown option", sys.argv[1])
            options_error()
    else:
        options_error()

if __name__ == "__main__":
    #start_time = time.time()
    main()
    #print("--- %s seconds ---" %(time.time() - start_time))
