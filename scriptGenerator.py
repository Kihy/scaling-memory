import subprocess
import argparse
import sys

NK = 3.0


def get_nodes(symbol, n):
    """get nodes name as combination of symbol and N, used for testing"""
    nodes = ["{}{}".format(symbol, n) for n in range(1, n + 1)]
    return nodes


def check_input(X, Y, Z):
    """checks if input is correct"""
    if not (isinstance(X, int) or isinstance(Y, int) or isinstance(Z, int)):
        print("Parameters must be integers.")
        sys.exit(1)


def get_input():
    """gets the input from argument parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('X', type=int, help="Please enter the number of source nodes")
    parser.add_argument('Y', type=int, help="Please enter the number(>=3) of transit nodes ")
    parser.add_argument('Z', type=int, help="Please enter the number of destination nodes")
    args = parser.parse_args()
    X = args.X
    Y = args.Y
    Z = args.Z

    check_input(X, Y, Z)
    return X, Y, Z


def main():
    """main program"""
    X, Y, Z = get_input()

    generate_lp(X, Y, Z, True)


def generate_lp(X, Y, Z, print_result=False):
    """generate lp file from input"""

    # startNodes = get_nodes('S', X)
    # transitNodes = get_nodes('T', Y)
    # endNodes = get_nodes('D', Z)
    every_node = set()
    u_set = set()
    links = []

    filename = "lpFile_{}{}{}.lp".format(X, Y, Z)
    output_lp_file = open(filename, "w")
    output_lp_file.write("Minimize\n")
    output_lp_file.write("r\n")
    # eqn="r"
    # for i in range(1, X + 1):
    #     for j in range(1, Y + 1):
    #         eqn+="+c{}{}".format(i,j)
    #
    # for i in range(1, Y + 1):
    #     for j in range(1, Z + 1):
    #         eqn+="+d{}{}".format(i,j)
    # output_lp_file.write(eqn)
    output_lp_file.write("\nSubject to\n")

    output_lp_file.write("demandConstraints:\n")
    for i in range(1, X + 1):
        for j in range(1, Z + 1):
            eqn = ""
            for t in range(1, Y + 1):
                eqn += "x{}{}{}+".format(i, t, j)
                every_node.add("x{}{}{}".format(i, t, j))
            eqn = eqn[:-1]
            eqn += "={}".format(i + j)
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("\nthreeFlowConstraints:\n")
    for i in range(1, X + 1):
        for j in range(1, Z + 1):
            eqn = ""
            for t in range(1, Y + 1):
                eqn += "u{}{}{}+".format(i, t, j)
                u_set.add("u{}{}{}".format(i, t, j))
            eqn = eqn[:-1]
            eqn += "={}".format(NK)
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("\nequalFlowConstraints:\n")
    for i in range(1, X + 1):
        for j in range(1, Z + 1):
            for t in range(1, Y + 1):
                eqn = "3x{}{}{}-{}u{}{}{}=0".format(i, t, j, i + j, i, t, j)
                output_lp_file.write(eqn + "\n")

    output_lp_file.write("\nsourceToTransitLinkConstraints:\n")
    for i in range(1, X + 1):
        for j in range(1, Y + 1):
            eqn = ""
            for k in range(1, Z + 1):
                eqn += "x{}{}{}+".format(i, j, k)
                every_node.add("x{}{}{}".format(i, j, k))
            eqn = eqn[:-1]
            eqn += "-c{}{} <=0".format(i, j)
            links.append("y{}{}".format(i, j))
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("\nTransitToDestinationLinkConstraints:\n")
    for k in range(1, Y + 1):
        for j in range(1, Z + 1):
            eqn = ""
            for i in range(1, X + 1):
                eqn += "x{}{}{}+".format(i, k, j)
                every_node.add("x{}{}{}".format(i, k, j))
            eqn = eqn[:-1]
            eqn += "-d{}{} <= 0".format(k, j)
            links.append("y{}{}".format(k, j))
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("\ntransiteNodesConstraint:\n")
    for k in range(1, Y + 1):
        eqn = ""
        for i in range(1, X + 1):

            for j in range(1, Z + 1):
                eqn += "x{}{}{}+".format(i, k, j)
        eqn = eqn[:-1]
        eqn += "-r <= 0"
        output_lp_file.write(eqn + "\n")

    output_lp_file.write("\nnegativityConstraints:\n")
    for i in list(every_node):
        output_lp_file.write("{} >= 0\n".format(i))

    output_lp_file.write("r >= 0\n")

    output_lp_file.write("\nBinary\n")
    for u in list(u_set):
        output_lp_file.write(u + "\n")

    output_lp_file.write("END\n")
    output_lp_file.close()

    average, max_load, num_links, highest_link, highest_capacity = process_cplex(filename)

    if print_result:
        print("Summary for X={}, Y={}, Z={}".format(X, Y, Z))
        print("Average time: {}".format(average))
        print("Maximum load: {}".format(max_load))
        print("Number of links with non-zero capacity: {}".format(num_links))
        print("Highest capacity link: {} value: {}".format(highest_link, highest_capacity))

    return average, max_load, num_links, highest_link, highest_capacity


def process_cplex(filename):
    """
    Runs the cplex program and calculate maximum_load,
    number of links with non-zero capacity and highest capacity link
    """
    num_runs = 10

    cplex_command = ["cplex -c read {} optimize display solution variables -".format(filename)]
    time_command = ["time -p cplex -c read {} optimize".format(filename)]

    output = subprocess.run(cplex_command, shell=True, stdout=subprocess.PIPE)
    cplex_output = output.stdout.decode("utf-8")
    # process output
    # get the solution variables part
    output = cplex_output.split("Variable Name           Solution Value\n")[-1]
    highest_capacity = 0
    num_links = 0
    max_load = 0
    highest_link = ""
    for line in output.split("\n"):
        line = line.split(" ")
        variable_name = line[0]
        try:
            value = float(line[-1])
        except ValueError:
            break
        if variable_name == "r":
            max_load = value
        if variable_name.startswith("c") or variable_name.startswith("d"):
            num_links += 1
            if highest_capacity < value:
                highest_capacity = value
                highest_link = variable_name

    # measure time as average of 10 Runs
    total = 0
    for _ in range(num_runs):
        output = subprocess.run(time_command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        time_list = output.stderr.decode("utf-8").split("\n")

        user_time = get_time(time_list[1])
        sys_time = get_time(time_list[2])
        total = total + user_time + sys_time

    average = total / num_runs

    return average, max_load, num_links, highest_link, highest_capacity


def get_time(time_string):
    """gets the time from time_string generated by linux time command"""
    return float(time_string.split(" ")[1])


if __name__ == '__main__':
    main()
