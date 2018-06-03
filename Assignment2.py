import time
import subprocess

SPLIT = 3
def programe_input():
    x = input("Enter X ")
    y = input("Enter Y ")
    z = input("Enter Z ")
    return x, y, z

def main():
    "Run the program"
    x, y, z = programe_input()

    to_write(int(x), int(y), int(z))

def to_write(x, y, z):
    all_nodes = set()
    u_set = set()
    links = []

    file = "lpFile.lp"
    output = open(file, "w")

    output.write("Minimize\nr\nSubject to\n")

    write_demands(x,y,z,all_nodes,output)
    write_3_flow_constraint(x,y,z,u_set,output)
    write_equal_flow_c(x,y,z,output)
    link_to_source_c(x, y, z, all_nodes, links, output)
    transit_to_src(x, y, z, all_nodes, links, output)
    transit_node_constraint(x, y, z, output)
    write_b(all_nodes,u_set,output)

    output.write("END")
    output.close()

    average, maximum, no_of_links, highest_link, highest_cap = cplex_run(file)

    print_answer(x,y,z,average,maximum,no_of_links,highest_link,highest_cap)

def write_demands(x,y,z, all_nodes, output):
    for i in range(x):
        for k in range(z):
            line = ""
            for n in range(y):
                line += "x{0}{1}{2} +".format(i + 1,
                                              n + 1,
                                              k + 1)
                all_nodes.add("x{0}{1}{2}".format(i + 1,
                                                  n + 1,
                                                  k + 1))
            line = line[:-1]
            line += "= {}".format(i + k + 2)
            output.write(line + "\n")

def write_3_flow_constraint(x,y,z, u_set, output):
    for i in range(x):
        for k in range(z):
            line = ""
            for n in range(y):
                line += "u{0}{1}{2} +".format(i + 1,
                                              n + 1,
                                              k + 1)
                u_set.add("u{0}{1}{2}".format(i + 1,
                                              n + 1,
                                              k + 1))
            line = line[:-1]
            line += "= {}".format(SPLIT)
            output.write(line + "\n")

def write_equal_flow_c(x,y,z, output):
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

def link_to_source_c(x,y,z,all_nodes, links, output):
    for i in range(x):
        for n in range(y):
            line = ""
            for k in range (z):
                line += "x{0}{1}{2} +".format(i + 1,
                                              n + 1,
                                              k + 1)
                all_nodes.add("x{0}{1}{2}".format(i + 1,
                                                  n + 1,
                                                  k + 1))
            line = line[:-1]
            line += "-c{0}{1} <= 0".format(i + 1,
                                           n + 1)
            links.append("y{0}{1}".format(i + 1,
                                          n +1))
            output.write(line + "\n")

def transit_to_src(x,y,z,all_nodes, links, output):
    for n in range(y):
        for k in range(z):
            line = ""
            for i in range(x):
                line += "x{0}{1}{2} +".format(i + 1,
                                              n + 1,
                                              k + 1)
                all_nodes.add("x{0}{1}{2}".format(i + 1,
                                                  n + 1,
                                                  k + 1))
            line = line[:-1]
            line += "-d{0}{1} <= 0".format(n + 1,
                                           k + 1)
            links.append("y{0}{1}".format(n + 1,
                                          k + 1))
            output.write(line + "\n")

def transit_node_constraint(x,y,z,output):
    for n in range(y):
        line = ""
        for i in range(x):
            for k in range(z):
                line += "x{0}{1}{2}+".format( i + 1,
                                              n + 1,
                                              k + 1)
        line = line[:-1]
        line += "-r <= 0"
        output.write(line +"\n")

def write_b(all_nodes, u_set, output):
    output.write("Bounds \n")
    for node in list(all_nodes):
        output.write("0 <= {0}\n".format(node))
    output.write("0 <= r\n")
    output.write("Binaries\n")
    for u in list(u_set):
        output.write(u + "\n")


def print_answer(x,y,z, average, maximum, no_of_links, highest_link,highest_cap):

    print("x = {0}, y = {1}, z = {2}".format(x,y,z))
    print("Average time: {}".format(average))
    print("Maximum: {}".format(maximum))
    print("Number of link: {}".format(no_of_links))
    print("Highest link capacity: {}".format(highest_link))
    print("Highest capacity: {}".format(highest_cap))


def cplex_run(filename):

    cplex_command = ["cplex", "-c", "read", filename,  "optimize", "display", "solution", "variables", "-"]
    mark = time.clock

    total = 0
    for i in range(10):
        start = mark()
        output = subprocess.run(cplex_command, shell=True, stdout=subprocess.PIPE)
        end = mark()
        total = (end - start)

    time_avg = total / 10
    cplex_out = output.stdout.decode("utf-8")


    output2 = cplex_out.split("\n")
    start_index = output2.index("Variable Name           Solution Value\r")

    maximum = 0
    no_of_links = 0
    highest_link = ""
    highest_cap = 0
    for line in output2[start_index + 1:]:
        line.strip("\r")
        line = line.split(" ")
        id = line[0]
        try:
            value = float(line[-1])
        except ValueError:
            break
        if id == "r":
            maximum = value
        if id[0] == "c" or id[0] == "d":
            no_of_links += 1
            if highest_cap < value:
                highest_cap = value
                highest_link = id

    return time_avg, maximum, no_of_links, highest_link, highest_cap

if __name__ == '__main__':
    main()
