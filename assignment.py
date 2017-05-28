from scriptGenerator import generate_lp


def main():
    """function to fix X=7,Y from 3 to 7, and Z=7"""
    result_file = open("result", "w")
    for y in range(3, 8):
        max_load, numLinks, highest_capcity = generate_lp(7, y, 7)
        result_file.write("{} {} {} {}\n".format(y, max_load, numLinks, highest_capcity))
    result_file.close()


if __name__ == '__main__':
    main()
