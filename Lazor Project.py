'''
finish read_bff
'''


class Lazor():
    '''
    '''

    def __init__(self):
        '''
        '''

    def read_bff(self,filename):
        '''
        This function is used to read a .bff file and generate a corresponding dictionary.(Written by Xinru)
        The generated dictionary contains 4 parts.

        *** map ***
        A list of lists which shows the look of the map.

        *** block ***
        A list gives us the information about numbers of different types of blocks.

        *** lazer ***
        A dictionary gives us the information including numbers of lazers, starting positon and the direction of lazers.
        {(starting position):[direction]}

        *** target_point ***
        A list gives us the information about the position of targets.
        '''
        # Open the specified file.
        f = open(filename, "r")
        file = {}
        map = []
        # Skip the line before "GRID START"
        for line in f:
            if line.strip("\n") == "GRID START":
                break
        for line in f:
            # Skip the line after "GRID STOP"
            if line.strip("\n") == "GRID STOP":
                break
            # Generate a list of lists with information of the map(the line between "GRID START" and "GRID STOP" )
            map.append(line.strip("\n").split(" "))
        # Add map to dictionary.
        file["map"] = map
        block = []
        lazer = {}
        point = []
        for line in f:
            # Generate list/dictionary with information of blocks/lazers/target points.
            if line.startswith('A') or line.startswith('B') or line.startswith('C'):
                block.append(line.strip("\n").split(" "))
            if line.startswith('L'):
                lst = line.strip("\n").split(" ")
                lazer[(int(lst[1]),int(lst[2]))] = [int(lst[3]),int(lst[4])]
            if line.startswith('P'):
                lst = line.strip("\n").split(" ")
                point.append((int(lst[1]),int(lst[2])))
        # Add to the dictionary.
        file["block"] = block
        file["lazer"] = lazer
        file["target_point"] = point
        # Close the file
        f.close()
        return file

    def solve_lazor(self):
        '''
        '''
        pass

    def save_txt(self):
        '''
        '''
        pass

    def save_image(self):
        '''
        '''
        pass

    def General(self):
        '''
        '''
        pass


if __name__ == "__main__":
    pass
