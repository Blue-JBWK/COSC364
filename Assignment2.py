import time
import subprocess
import argparse
import sys
NK = 3.0


def get_nodes(symbol, n):
    for n in range(1, n + 1):
        nodes = ["{}{}".format(symbol, n)]
    return nodes

def valid_check(input1, input2, input3):
    if input1 is not int and input2 is not int and input3 is not int:
        print("Error in input state. Input must be intereger")
        sys.exit(1)

def programe_input():
    x = input("Enter the number of the source node ")
    y = input("Enter the number of transit node ")
    z = input("Enter the number of the dest node ")
    return x, y, z

def main():
    "Run the program"
    x, y, z = programe_input()

    to_write(int(x), int(y), int(z))

def to_write(x, y, z):
    every_nodes = set()
    u_set = set()
    links = []

    file = "lpFile.lp"
    output = open(file, "w")

    output.write("Minimize\nr\nSubject to\n")
                 #"demandConstraints:\n")
    for i in range(x):
        for k in range(z):
            line = ""
            for n in range(y):
                line += "x{0}{1}{2} +".format(i + 1, n + 1, k + 1)
                every_nodes.add("x{0}{1}{2}".format(i + 1, n + 1, k + 1))
            line = line[:-1]
            line += "= {}".format(i + k + 2)
            output.write(line + "\n")

    #output.write("threeFlowConstraints:\n")
    for i in range(x):
        for k in range(z):
            line = ""
            for n in range(y):
                line += "u{0}{1}{2} +".format(i + 1, n + 1, k + 1)
                u_set.add("u{0}{1}{2}".format(i + 1, n + 1, k + 1))
            line = line[:-1]
            line += "= {}".format(NK)
            output.write(line + "\n")

    #output.write("equalFlowConstraints\n")
    for i in range(x):
        for k in range(z):
            for n in range(y):
                line = "3 x{0}{1}{2} - {3} u{4}{5}{6} = 0".format(i + 1,
                                                              n + 1,
                                                              k + 1,
                                                              i + k + 2,
                                                              i + 1,
                                                              n + 1,
                                                              k + 1)
                output.write(line + "\n")

    #output.write("Source To Transit Link Constrain\n")
    for i in range(x):
        for n in range(y):
            line = ""
            for k in range (z):
                line += "x{0}{1}{2} +".format(i + 1,n + 1,k + 1)
                every_nodes.add("x{0}{1}{2}".format(i + 1,n + 1,k + 1))
            line = line[:-1]
            line += "-c{0}{1} <= 0".format(i + 1, n + 1)
            links.append("y{0}{1}".format(i + 1, n +1))
            output.write(line + "\n")

    #output.write("Transit to destination link constrain: \n")
    for n in range(y):
        for k in range(z):
            line = ""
            for i in range(x):
                line += "x{0}{1}{2} +".format(i + 1, n + 1, k + 1)
                every_nodes.add("x{0}{1}{2}".format(i + 1, n + 1, k + 1))
            line = line[:-1]
            line += "-d{0}{1} <= 0".format(n + 1, k + 1)
            links.append("y{0}{1}".format(n + 1, k + 1))
            output.write(line + "\n")

    #output.write("Transit node constrain: \n")
    for n in range(y):
        line = ""
        for i in range(x):
            for k in range(z):
                line += "x{0}{1}{2}+".format( i + 1, n + 1, k + 1)
        line = line[:-1]
        line += "-r <= 0"
        output.write(line +"\n")

    output.write("Bounds \n")
    for node in list(every_nodes):
        output.write("0 <= {0}\n".format(node))
    output.write("0 <= r\n")
    output.write("Binary\n")
    for u in list(u_set):
        output.write(u + "\n")

    output.write("END")
    output.close()

    average, maximum, no_of_links, highest_link, highest_cap = cplex_run(file)

    ###########################
    """Print out statistic"""

    print("Summary x = {0}, y = {1}, z = {2}".format(x,y,z))
    print("Average time taken: {}".format(average))
    print("Maximum_load: {}".format(maximum))
    print("Number of link: {}".format(no_of_links))
    print("Highest link capacity: {} - {}".format(highest_link, highest_cap))


def cplex_run(filename):
    path = "C:\\Users\\Blue - Meraki\\Desktop\\364\\lpFile.lp"
    num_runs = 10
    cplex_command = ["cplex", "-c", "read", filename,  "optimize", "display", "solution", "variables", "-"]
    time_command = ["time", "-p", "cplex", "-c", "read", filename, "optimize"]
    mark = time.clock

    total = 0
    for i in range(num_runs):
        start = mark()
        output = subprocess.run(cplex_command, shell=True, stdout=subprocess.PIPE)
        end = mark()
        total = (end - start)
    time_avg = total / 10
    cplex_out = output.stdout.decode("utf-8")
    #print(cplex_out)


    output2 = cplex_out.split("\n")
    #print(output2)
    start_index = output2.index("Variable Name           Solution Value\r")
    #length = len(output2[start_index:])
    #print(output2[start_index:])
    max = 0
    no_of_links = 0
    highest_link = ""
    highest_cap = 0
    for line in output2[start_index + 1:]:
        line.strip("\r")
        #print(line)
        line = line.split(" ")
        id = line[0]
        try:
            value = float(line[-1])
        except ValueError:

            break
        if id == "r":
            max = value
        if id.startswith("c") or id.startswith("d"):
            no_of_links += 1
            if highest_cap < value:
                highest_cap = value
                highest_link = id
    total = 0
    #print(no_of_links)
    #print(max)
    #print(highest_cap)
    #print(highest_link)
    #for run in range(num_runs):

        #output = subprocess.run(time_command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        #print(run)
        #time_list = output.stderr.decode("utf-8").split("\n")
        #user_time = get_time(time_list[1])
        #sys_time = get_time(time_list[2])
        #total = total + user_time + sys_time

    #average = total / num_runs

    return time_avg, max, no_of_links, highest_link, highest_cap

def get_time(time_string):
    return float(time_string.split(" ")[1])


if __name__ == '__main__':
    main()










