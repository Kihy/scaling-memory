import subprocess
import argparse
import sys

NK=3.0

def get_nodes(symbol,N):
    nodes = ["{}{}".format(symbol,n) for n in range(1, N + 1)]
    return nodes

def check_input(X,Y,Z):
    """checks if input is correct"""
    if not (isinstance(X,int) or isinstance(Y,int) or isinstance(Z,int)):
        print("Parameters must be integers.")
        sys.exit(1)

def get_input():
    """gets the input from argument parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('X', type=int, help="Please enter the number of source nodes")
    parser.add_argument('Y', type=int, help="Please enter the number(>=3) of transit nodes ")
    parser.add_argument('Z', type=int, help="Please enter the number of destination nodes")
    args=parser.parse_args()
    X = args.X
    Y = args.Y
    Z = args.Z

    check_input(X,Y,Z)
    return X,Y,Z

def main():
    """main program"""
    X,Y,Z=get_input()

    generate_lp(X,Y,Z)

def generate_lp(X,Y,Z):
    """generate lp file from input"""

    startNodes = get_nodes('S', X)
    transitNodes = get_nodes('T',Y)
    endNodes = get_nodes('D',Z)
    everyNode = set()
    u_set = set()
    links = []

    filename="lpFile_{}{}{}.lp".format(X,Y,Z)
    output_lp_file = open(filename, "w")
    output_lp_file.write("Minimize\n")
    output_lp_file.write("r\n")
    output_lp_file.write("Subject to\n")

    output_lp_file.write("demandConstraints:\n")
    for i in range(1,X+1):
        for j in range(1,Z+1):
            eqn = ""
            for t in range(1,Y+1):
                eqn += "x{}{}{}+".format(i, t, j)
                everyNode.add("x{}{}{}".format(i, t, j))
            eqn = eqn[:-1]
            eqn += "={}".format(i+j)
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("threeFlowConstraints:\n")
    for i in range(1, X + 1):
        for j in range(1, Z + 1):
            eqn = ""
            for t in range(1,Y+1):
                eqn += "u{}{}{}+".format(i, t, j)
                u_set.add("u{}{}{}".format(i, t, j))
            eqn = eqn[:-1]
            eqn += "={}".format(NK)
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("equalFlowConstraints:\n")
    for i in range(1, X + 1):
        for j in range(1, Z + 1):
            for t in range(1,Y+1):
                eqn = "3x{}{}{}-{}u{}{}{}=0".format(i, t,j,i+j,i, t, j)
                output_lp_file.write(eqn + "\n")


    output_lp_file.write("sourceToTransitLinkConstraints:\n")
    for i in range(1,X+1):
        for j in range(1,Y+1):
            eqn = ""
            for k in range(1,Z+1):
                eqn += "x{}{}{}+".format(i,j,k)
                everyNode.add("x{}{}{}".format(i,j,k))
            eqn = eqn[:-1]
            eqn += "-c{}{} <=0".format(i,j)
            links.append("y{}{}".format(i,j))
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("TransitToDestinationLinkConstraints:\n")
    for k in range(1,Y+1):
        for j in range(1,Z+1):
            eqn = ""
            for i in range(1,X+1):
                eqn += "x{}{}{}+".format(i,k,j)
                everyNode.add("x{}{}{}".format(i,k,j))
            eqn = eqn[:-1]
            eqn += "-d{}{} <= 0".format(k,j)
            links.append("y{}{}".format(k,j))
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("transiteNodesConstraint:\n")
    for k in range(1,Y+1):
        eqn = ""
        for i in range(1,X+1):

            for j in range(1,Z+1):
                eqn += "x{}{}{}+".format(i,k, j)
        eqn = eqn[:-1]
        eqn += "-r <= 0"
        output_lp_file.write(eqn + "\n")

    output_lp_file.write("negativityConstraints:\n")
    for i in list(everyNode):
        output_lp_file.write("{} >= 0\n".format(i))

    output_lp_file.write("r >= 0\n")

    output_lp_file.write("Binary\n")
    for u in list(u_set):
        output_lp_file.write(u+"\n")

    output_lp_file.write("END\n")
    output_lp_file.close()

    return run_cplex(filename)

def run_cplex(filename):
    command_args=["time","cplex", "-c", "read {}".format(filename), "optimize", "display solution variables -"]
    print(" ".join(command_args))
    output=subprocess.check_output(command_args[1:]).decode("utf-8")

    #process output
    #get the solution variables part
    output=output.split("Variable Name           Solution Value\n")[-1]
    highest_capcity=0
    numLinks=0
    for line in output.split("\n"):
        line=line.split(" ")
        variableName=line[0]
        try:
            value=float(line[-1])
        except:
            break;
        if variableName=="r":
            max_load=value
        if variableName.startswith("c") or variableName.startswith("d"):
            numLinks+=1
            if highest_capcity<value:
                highest_capcity=value
                highest_link=variableName

    print("Maximum load: {}".format(max_load))
    print("Number of links with non-zero capacity: {}".format(numLinks))
    print("Highest capacity link: {} value: {}".format(highest_link,highest_capcity))
    return max_load,numLinks,highest_capcity



if __name__ == '__main__':
    main()
