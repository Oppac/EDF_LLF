import random
import sys
import time
from math import gcd
try:
    import matplotlib.pyplot as plt
    import_ok = True
except:
    import_ok = False
    print("Warning: matplotlib is required to use the schedule plotter")

class Task():
    '''Task class that stores a task'''
    def __init__(self, offset=0, wcet=0, period=0, id="None"):
        self.offset = offset
        self.wcet = wcet
        self.period = period
        self.next_deadline = period + offset
        self.id = id

        self.completed = False
        self.already_done = 0
        self.job_start = 0
        self.job_nb = 0
        self.scheduler = ""
        self.priority = 0

    def update_priority(self, time):
        '''Compute the priority of the current job'''
        if self.scheduler == "edf":
            self.priority = self.next_deadline
        elif self.scheduler == "llf":
            self.priority = self.next_deadline - (time + (self.wcet - self.already_done))

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
    def __init__(self, tasks, start, end, type):
        self.preemptions = 0
        self.start = start
        self.end = end
        self.tasks = tasks
        self.type = type
        for task in tasks: task.scheduler = type
        self.previous_job = Task()
        self.just_completed = Task()

        #Output_log format: key=time value=[type, end_time, task_id, job_id]
        self.output_log = {time: [] for time in range(0, self.end+1)}
        #Data format: [task_id, start_time, end_time]
        self.plot_values = []
        self.plot_arrival = []
        self.plot_deadlines = []
        self.plot_preemptions = []

    def draw_schedule(self, show, output):
        tasks_plot = [int(task.id[-1]) for task in self.tasks]
        time = [i for i in range(self.start, self.end+1)]

        for v in self.plot_values:
            task = v[0]
            start_time = v[1]
            end_time = v[2]
            plt.plot([start_time, end_time], [task, task], color='b')

        for v in self.plot_preemptions:
            interrupted_task = v[0]
            preemption_time = v[1]
            plt.plot([preemption_time], [interrupted_task], marker="v", color='orange')

        for v in self.plot_deadlines:
            missed_task = v[0]
            deadline_time = v[1]
            plt.plot([deadline_time], [missed_task], marker='x', color='r')

        for v in self.plot_arrival:
            finished_task = v[0]
            arrival_time = v[1]
            plt.plot([arrival_time], [finished_task], marker='o', color='g')


        plt.grid()
        plt.xticks(range(self.start, self.end+1))
        plt.yticks(range(0, len(tasks_plot)))
        plt.xlabel("Time")
        plt.ylabel("Tasks")
        plt.gca().invert_yaxis()

        plt.title("{}  Scheduler".format(self.type.title()))
        if output:
            plt.savefig("{}_{}.png".format(self.type, output),  format='png')
        if show:
            plt.show()

    def start_msg(self):
        print("TODO")
        print("Schedule from: {} to: {} ; {} tasks".format(self.start, self.end, len(self.tasks)))

    def end_msg(self):
        print("End: {} preemptions".format(self.preemptions))

    def print_log(self):
        for key, values in self.output_log.items():
            values = sorted(values, key=lambda x: x[3])
            for v in values:
                if v[0] == "Deadline":
                    print("{}: Job {}J{} misses a deadline".format( key, v[2], v[3]))
                    self.plot_deadlines.append([int(v[2][-1]), key])
            for v in values:
                if v[0] == "Arrival":
                    print("{}: Arrival of job {}J{}".format(key, v[2], v[3]))
                    self.plot_arrival.append([int(v[2][-1]), key])
            for v in values:
                if v[0] == "Execution":
                    print("{}-{}: {}J{} ".format(key, v[1], v[2], v[3]))
                    self.plot_values.append([int(v[2][-1]), key, v[1]])

    def get_highest_priority(self, time):
        '''Get the job that has the priority'''
        priorities = self.tasks[:]
        try:
            hp_task = min(priorities, key=lambda task: task.priority)
            while hp_task.completed or time < hp_task.offset:
                priorities.remove(hp_task)
                hp_task = min(priorities, key=lambda task: task.priority)
            return hp_task
        except:
            return None

    def check_deadlines(self, time):
        '''Check if a job missed its deadline or if its time for a new job'''
        for i in range(len(self.tasks)):
            if self.tasks[i].next_deadline == time:
                self.tasks[i].job_nb += 1
                self.just_completed = self.tasks[i]
                if not self.tasks[i].completed:
                    if time >= self.start:
                        self.output_log[time].append(
                        ["Deadline", None, self.tasks[i].id, self.tasks[i].job_nb])
                else:
                    if time >= self.start:
                        self.output_log[time].append(
                        ["Arrival", None, self.tasks[i].id, self.tasks[i].job_nb])
                self.tasks[i].next_deadline += self.tasks[i].period
                self.tasks[i].already_done = 0
                self.tasks[i].completed = False

    def schedule(self, time, task):
        task.already_done += 1
        self.just_completed = Task()
        if task.already_done >= task.wcet:
            task.completed = True
            if time >= self.start:
                print(str(time) + " represent")
                self.output_log[task.job_start].append(["Execution", time+1, task.id, task.job_nb])
        return task

    def scheduling(self):
        '''Main time loop, choose each time which job to schedule and control the flow of the scheduler'''
        for time in range(0, self.end):

            for task in self.tasks:
                task.update_priority(time)

            for i in range(len(self.tasks)):
                if time == self.tasks[i].offset and time >= self.start:
                    self.output_log[time].append(
                    ["Arrival", None, self.tasks[i].id, self.tasks[i].job_nb])

            new_job = self.get_highest_priority(time)
            if new_job is not None:
                if new_job is not self.previous_job:
                    if not self.previous_job.completed and \
                       not self.previous_job is self.just_completed and \
                       not self.previous_job.id == "None":
                        if time >= self.start and self.previous_job.job_start >= self.start:
                            print(str(time) + " represent")
                            self.output_log[self.previous_job.job_start].append(
                            ["Execution", time, self.previous_job.id, self.previous_job.job_nb])
                            self.preemptions += 1
                            self.plot_preemptions.append([int(self.previous_job.id[-1]), time])
                    new_job.job_start = time
                    self.previous_job = self.schedule(time, new_job)
                else:
                    self.previous_job = self.schedule(time, new_job)

            self.check_deadlines(time)


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
    print("Scheduler: python project.py edf|llf input_file start stop [graphic_options]")
    print("Graphic options: draw (show schedule plotter) | save (save plot)")

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

        #EDF and LLF schedulers option
        elif (str(sys.argv[1]) == "edf") or (str(sys.argv[1] == "llf")):
            if len(sys.argv) > 4:
                get_data(sys.argv[2], tasks_list)
                try:
                    start = int(sys.argv[3])
                    end = int(sys.argv[4])
                    if (start < 0) or (end < start):
                        raise
                except:
                    sys.exit("Invalid start and end times")
                try:
                    if sys.argv[1] == "edf":
                        scheduler = Scheduler(tasks_list, start, end, "edf")
                    else:
                        scheduler = Scheduler(tasks_list, start, end, "llf")
                    scheduler.start_msg()
                    scheduler.scheduling()
                    scheduler.print_log()
                    scheduler.end_msg()

                    if len(sys.argv) > 5:
                        if import_ok:
                            if "draw" in sys.argv and "save" in sys.argv:
                                file_name = sys.argv[2][sys.argv[2].find("/")+1:sys.argv[2].find(".")]
                                scheduler.draw_schedule(True, file_name)
                            elif "draw" in sys.argv:
                                scheduler.draw_schedule(True, False)
                            elif "save" in sys.argv:
                                file_name = sys.argv[2][sys.argv[2].find("/")+1:sys.argv[2].find(".")]
                                scheduler.draw_schedule(False, file_name)
                            else:
                                print("Graphic options: draw (show schedule plotter) | save (save plot)")
                        else:
                            print("Please install matplotlib to use the schedule plotter")
                except:
                    print("Error during the scheduling")
            else:
                print("Usage: python project.py edf|llf input_file start stop")
        else:
            print("Unknown option", sys.argv[1])
            options_error()
    else:
        options_error()

if __name__ == "__main__":
    #start_time = time.time()
    main()
    #print("--- %s seconds ---" %(time.time() - start_time))
