def location(row, column):
    '''
        This function helps align text.

        example;
            align = colorOS.location(12, 24)
            print(f"{align} selam")
    '''
    return f"\033[{row};{column}H"
