from subprocess import check_output,call
import argparse
import sys

NK=3.0

def get_nodes(symbol,N):
    nodes = ["{}{}".format(symbol,n) for n in range(1, N + 1)]
    return nodes

#def set_link_constraint()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('X', type=int, help="Please enter the number of source nodes")
    parser.add_argument('Y', type=int, help="Please enter the number(>=3) of transit nodes ")
    parser.add_argument('Z', type=int, help="Please enter the number of destination nodes")
    args=parser.parse_args()
    X = args.X
    Y = args.Y
    Z = args.Z
    if not (isinstance(X,int) or isinstance(Y,int) or isinstance(Z,int)):
        print("Parameters must be integers.")
        sys.exit(1)
    if Y < 3:
        print("Y must >= 3")
        sys.exit(1)

    startNodes = get_nodes('S', X)
    transitNodes = get_nodes('T',Y)
    endNodes = get_nodes('D',Z)
    everyNode = set()
    u_set = set()
    links = []

    print("startNodes",startNodes)
    print("transitnodes",transitNodes)
    print("endnodes",endNodes)
    # get template as string
    output_lp_file = open("ass2.lp", "w")
    output_lp_file.write("Minimize\n")
    output_lp_file.write("r\n")
    output_lp_file.write("Subject to\n")

    output_lp_file.write("demandConstraints:\n")
    for i in range(1,X+1):
        for j in range(1,Z+1):
            eqn = ""
            for t in transitNodes:
                eqn += "x{}{}{}+".format(startNodes[i-1], t, endNodes[j-1])
                everyNode.add("x{}{}{}".format(startNodes[i-1], t, endNodes[j-1]))
            eqn = eqn[:-1]
            eqn += "={}".format(i+j)
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("3flowConstraints:\n")
    for i in range(1, X + 1):
        for j in range(1, Z + 1):
            eqn = ""
            for t in transitNodes:
                eqn += "u{}{}{}+".format(startNodes[i - 1], t, endNodes[j - 1])
                u_set.add("u{}{}{}".format(startNodes[i - 1], t, endNodes[j - 1]))
            eqn = eqn[:-1]
            eqn += "={}".format(NK)
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("equalFlowConstraints:\n")
    for i in range(1, X + 1):
        for j in range(1, Z + 1):
            eqn = ""
            for t in transitNodes:
                eqn = "3x{}{}{}={}u{}{}{}".format(startNodes[i - 1], t, endNodes[j - 1],i+j,startNodes[i - 1], t, endNodes[j - 1])
            output_lp_file.write(eqn + "\n")


    output_lp_file.write("linkConstraints:\n")
    for i in range(1,X+1):
        for j in range(1,Y+1):
            eqn = ""
            for k in range(1,Z+1):
                eqn += "x{}{}{}+".format(startNodes[i-1], transitNodes[j-1], endNodes[k-1])
                everyNode.add("x{}{}{}".format(startNodes[i-1], transitNodes[j-1], endNodes[k-1]))
            eqn = eqn[:-1]
            eqn += "-c{}{} <=0".format(i,j)
            links.append("y{}{}".format(startNodes[i-1], transitNodes[j-1]))
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("\n")
    for k in range(1,Y+1):
        for j in range(1,Z+1):
            eqn = ""
            for i in range(1,X+1):
                eqn += "x{}{}{}+".format(startNodes[i-1], transitNodes[k-1], endNodes[j-1])
                everyNode.add("x{}{}{}".format(startNodes[i-1], transitNodes[k-1], endNodes[j-1]))
            eqn = eqn[:-1]
            eqn += "-D{}{} <= 0".format(k,j)
            links.append("y{}{}".format(transitNodes[k-1], endNodes[j-1]))
            output_lp_file.write(eqn + "\n")

    output_lp_file.write("transiteNodesConstraint:\n")
    for i in transitNodes:
        eqn = ""
        for j in startNodes:

            for d in endNodes:
                eqn += "x{}{}{}+".format(j,i, d)
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

if __name__ == '__main__':
    main()
