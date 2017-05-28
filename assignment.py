from scriptGenerator import generate_lp


def main():
    """function to fix X=7,Y from 3 to 7, and Z=7"""
    template_heading = "{:6}{:20}{:20}{:20}{:20}{:20}\n"
    template_data = "{:<6} {:<20.3f} {:<20.3f} {:<20} {:<20} {:<20}\n"
    result_file = open("result", "w")
    result_file.write(template_heading.format("Y", "Average Time", "Maximum load", "Number of links", "highest link",
                                              "highest capacity"))
    for y in range(3, 8):
        results = generate_lp(7, y, 7)
        result_file.write(template_data.format(y, *results))
    result_file.close()


if __name__ == '__main__':
    main()
