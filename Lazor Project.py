'''
Project: Lazor
Authors: Xinru Yun, Tianjun Tang(Don)

Course: Software Carpentry
Johns Hopkins University



Welcome to our Lazor Project!
This is our midterm group project of Software Carpentry,
that requires us to solve a charming game named Lazor.
(which can be downloaded from AppStore)



To play with, this code requires .bff files, most of which
can be found from our repository, that look like following:

(numbered_10.bff)
*** Map ***
.bff files start with original map.
Nomenclature follows these rules:
    x = no block allowed
    o = blocks allowed
    A = fixed reflect block
    B = fixed opaque block
    C = fixed refract block

# Grid will start at top left being 0, 0
# Step size is by half blocks
# Thus, this leads to even numbers indicating
# the rows/columns between blocks, and odd numbers
# intersecting blocks.

[For Example]
GRID START
o o o
o x o
o o o
x x o
o o o
GRID STOP

*** Movable Blocks ***
Informations of which and how many block that's movable.
(Type Amount)
Types:
    A = fixed reflect block
    B = fixed opaque block
    C = fixed refract block

[For Example]
A 5
B 3
C 1

*** Lazor ***
# Now we specify that we have two lazers
#    x, y, vx, vy
# NOTE! because 0, 0 is the top left, our axis
# are as follows:
#
#      __________  +x
#      |         /
#      |
#      |
#      |
#      |/ +y

Information of each lazor is stored as:
L x y x-direction y-direction

[For Example]
(L 5 2 -1 -1)

*** Target Points ***

# Here we have the points that we need the lazers to intersect
(P x y)
[For Example]
P 4 3
P 6 5
P 6 7
'''
from itertools import permutations, combinations
from PIL import Image, ImageDraw


class Lazor():
    '''
    *** PROTOCOL ***
    In this code, all informations are generated and changed
    inside the "info_dict", which is a dictionary that stores
    all informations we need.

    All functions must be run in given order, to make sure proper
    initializations, as follows:
        Lazor = Lazor()
        info_dict = Lazor.read_bff('dark_10.bff')
        info_dict = Lazor.load_lazor_map(info_dict)
        info_dict = Lazor.lazor_path(info_dict)
        info_dict = Lazor.solve_lazor(info_dict)
        Lazor.save_img(info_dict) or Lazor.save_txt(info_dict)

    As you may notice, besides read_bff(), all functions only requires
    one input, "info_dict", which make it easy to run and debug.

    *** FUNCTIONS ***
        ** read_bff **
        ** load_lazor_map **
            Author: Don

            This function reads raw info from the info_dict,
            and generate more infos like map_points, fixed_block_position,
            map_length/height and original_lazor, as well as making many
            initializations, basically empty lists and dictionaries,
            for following functions.

        ** reflect_block_location **
            Author: Don

            This function is a sub_function of solve_lazor() and
            redundant_blocks().

            It solves that, if the lazor path is to be blocked or
            reflected at the inputed point, where should the block be putted.
            And if it's reflected, how would new direction change.

        ** lazor_path **
            Author: Don

            This function reads the 'block_position' info, with others, to
            generate path for each lazor, stored as a dictionary holding a
            list of position tuples, labeled by each lazor's starting point.

            It also generates a 'possible_block_position' list indicating
            positions that you may put next block.
            (Notice: It's meaningless to put the block outside lazor path, at
            least in most cases.)

        ** all_possible_situations **
            Author: Don

            This is a sub_function for solve_lazor(). (Method 1)
            Input:
                possible_list:  a list of possible position combinations for
                                first few blocks
                block_list:     a list of block order, for example putting A
                                after C and putting C after A will generate
                                different lazor paths
            Output:
                A new possible list of possible position combinations after
                putting next block on block_list.

        ** solve_lazor **
            Author: Don

            This is function that applies three methods to solve the problem.
            Each method is for a different situation.
                Situation 1:Situations when you've used all blocks. In this
                            case all blocks must be putted on lazor paths.
                Situation 2:Situations when there are some block remaining
                            when all target points are hit. Remaing blocks
                            mustn't block lazor paths.
                Situation 3:Situations like dark series, in which you have to
                            block some lazor paths.
                            Also when some bugs occur in former situations,
                            it's always the last chance to solve the problem.

                Method 1:   Generate a "possible_list" that only contains
                            combinations that all blocks are on lazor path,
                            using all_possible_situations() function.
                Method 2:   Remove points on each lazor path after last target
                            point. Then use same method of 'possible_block_
                            position', but in this case, they are 'impossible_
                            block_position'.
                            If the blank positions are enough for remaining
                            blocks, after subtracting 'impossible_blocks' and
                            those already put on the map, then it's the answer.
                Method 3:   Use combinations to 'violently' solve the problem.

        ** run_possible_comb **
            Author: Don

            This function is a sub_function for solve_lazor().

            It initialize the info_dict and check if the combinations
            are correct, that is, when all target points are hit.

            It return a list of False, showing how many target points
            are not hit.

        ** redundant_blocks **
            Author: Don

            This functions is a sub_function for solve_lazor().

            It handles method 2, and return a dictionary of remaining
            blocks' positions, or return False when there aren't enough
            places.

        ** delete_duplicated_element **
            Author: Don

            This little function deletes duplicated elements in a list.

            Quite useful in many places, lol.

        ** save_txt **
        ** set_color **
        ** set_tp **
        ** set_lp **
        ** save_img **
    '''

    def read_bff(self, filename):
        '''
        This function is used to read a .bff file
        and generate a corresponding dictionary.(Written by Xinru)
        The generated dictionary contains 4 parts.

        *** map ***
        A list of lists which shows the look of the map.

        *** block ***
        A list gives us the information about numbers of
        different types of blocks.

        *** lazor ***
        A dictionary gives us the information including numbers of lasers,
        starting positon and the direction of lasers.
        {(starting position):[direction]}

        *** target_point ***
        A list gives us the information about the position of targets.
        '''
        # Open the specified file.
        f = open(filename, "r")
        file = {}
        file['filename'] = filename[:-4]
        map = []
        # Skip the line before "GRID START"
        for line in f:
            if line.strip("\n") == "GRID START":
                break
        for line in f:
            # Skip the line after "GRID STOP"
            if line.strip("\n") == "GRID STOP":
                break
            # Generate a list of lists with information of the map.
            # (the line between "GRID START" and "GRID STOP" )
            lst = []
            for x in line.strip("\n"):
                if x != " ":
                    lst.append(x)
            map.append(lst)
        # Add map to dictionary.
        file["map"] = map
        block = {}
        lazor = {}
        point = []
        for line in f:
            '''
            Generate list/dictionary with information of
            blocks/lasers/target points.
            '''
            if line.startswith('A') or line.startswith('B')\
                    or line.startswith('C'):
                lst = line.strip("\n").split(" ")
                block[lst[0]] = int(lst[1])
            if line.startswith('L'):
                lst = line.strip("\n").split(" ")
                lazor[(int(lst[1]), int(lst[2]))] = [int(lst[3]), int(lst[4])]
            if line.startswith('P'):
                lst = line.strip("\n").split(" ")
                point.append((int(lst[1]), int(lst[2])))
        # Add to the dictionary.
        file["block"] = block
        file["original_lazor"] = lazor
        file["target_point"] = point
        # Close the file
        f.close()
        return file

    def load_lazor_map(self, info_dict):
        '''
        Author: Don

        load_lazor_map() function reads the raw information from read_bff()
        function, whose output contains map organization in the form of
        [['o'], ['A']].

        It also makes many initializations, basically empty lists and
        dictionaries, for following functions.

        The output is a dictionary which contains three parts of information:
        *** map_points ***
            the position which the lazor may pass through,
            stored as a list of tuples.
        *** fixed_block_position ***
            the fixed location of block "A", "B", "C", etc.
            store as a dictionary:
                in the form of position: tpye. e.g. (x, y): ["A"]
        *** map_length ***
            the length of the map, stored as an integer
        *** map_height ***
            the height of the map, stored as an integer
        '''
        info_dict['map_points'] = []
        info_dict['blank_position'] = []
        info_dict['fixed_block_position'] = {}
        info_dict['lazor_path'] = {}
        info_dict['block_position'] = {}
        info_dict['lazor'] = {}
        info_dict['possible_block_position'] = []

        raw_info = info_dict["map"]

        info_dict["map_length"] = 2 * len(raw_info[0])
        info_dict["map_height"] = 2 * len(raw_info)

        for y in range(len(raw_info)):
            for x in range(len(raw_info[y])):
                if raw_info[y][x] == 'x':
                    pass
                else:
                    possible_points = [
                        (2 * x + 1, 2 * y),
                        (2 * x, 2 * y + 1),
                        (2 * x + 2, 2 * y + 1),
                        (2 * x + 1, 2 * y + 2)
                    ]
                    for p in possible_points:
                        if p not in info_dict['map_points']:
                            info_dict['map_points'].append(p)
                    if raw_info[y][x] == 'o':
                        info_dict['blank_position'].append(
                            (2 * x + 1, 2 * y + 1)
                        )
                    else:
                        info_dict["fixed_block_position"][
                            (2 * x + 1, 2 * y + 1)] = raw_info[y][x]
        for f in info_dict['fixed_block_position']:
            info_dict['block_position'][f] =\
                info_dict['fixed_block_position'][f]
        for target_point in info_dict['target_point']:
            if target_point not in info_dict['map_points']:
                info_dict['map_points'].append(target_point)
        for lazor_start in info_dict['original_lazor']:
            if lazor_start not in info_dict['map_points']:
                info_dict['map_points'].append(lazor_start)
        return info_dict

    def reflect_block_location(
        self, position_x, position_y, direction_x, direction_y
    ):
        '''
        Author: Don.

        This function is seperated from lazor_path(), in order to avoid too
        many if-else judgements.

        After discussion, we notice that at upper/lower bound of a block,
        x changes direction, and at left/right bound, y changes direction.
        '''
        if position_y % 2 == 1:
            return {(position_x + direction_x, position_y):
                    [direction_x * -1, direction_y]}
        elif position_x % 2 == 1:
            return {(position_x, position_y + direction_y):
                    [direction_x, direction_y * -1]}

    def lazor_path(self, info_dict):
        '''
        Author: Don

        lazor_path() function generates path for each lazor,
        as well as the possible positions in which next block
        can be putted.

        *** Output ***
            ** info_dict['lazor_path']: A dictionary in which each lazor path
                                        is stored as a list of position tuples,
                                        labeled by starting point of the lazor.

            ** info_dict['lazor']:      A dictionary stores the starting points
                                        and directions of original lazor and
                                        those generated by refract blocks.

            ** info_dict['passed_blocks']: A dictionary stores the blocks each
                                        lazor passed. It's used for possible
                                        block positions, because it cannot be
                                        checked simply by emptying possible
                                        list after reflection, for in some
                                        cases some blocks are hit more than
                                        once.

            ** info_dict['possible_block_position']:
                                        A dictionary stores the locations where
                                        you can put next block, to ensure each
                                        block is on lazor path.

        *** METHOD ***
            ** Path **
                Start from each lazor starting point.
                Use reflect_block_position() function to judge if at this point
                lazor hits a block.
                    If yes, change direction or stop (when hits B).
                    If no, store relevant block location into possible block
                    list.
                Add this point into info_dict['lazor_path'].
                Go one step further on direction_x and direction_y.
                Loop until x or y get out of range.
            ** Refract Blocks **
                Since object can't change during iteration, new lazor generated
                from Refract Blocks, C, are stored in another dictionary,
                c_lazor, which will be added into info_dict['lazor'] at the end
                and rerun this function again.

                Also there are judges to make sure same generated lazors won't
                be added into c_lazor repeatedly.
            ** Starting Point **
                In problems like numbered_7 we found things get tricky when the
                lazor starting point are blocked at both sides by "A" or "B".
                So extra judges are added to avoid confusions.
            ** Infinite Loop **
                In some cases four blocks 'traps' the lazor and creates an
                infinite loop. A counter, times, it used for this case. When
                it's more than 100, the loop will break.

        '''
        # Initializations
        info_dict['lazor_path'] = {}
        c_lazor = {}
        info_dict['passed_blocks'] = {}
        info_dict['lazor'].update(info_dict["original_lazor"])
        for i in info_dict['lazor']:
            if i not in info_dict['lazor_path']:
                info_dict['lazor_path'][i] = []
            x = i[0]
            y = i[1]
            direction_x = info_dict["lazor"][i][0]
            direction_y = info_dict["lazor"][i][1]
            info_dict['passed_blocks'][i] = []
            times = 0
            while 0 <= x <= info_dict['map_length'] and\
                    0 <= y <= info_dict['map_height']:
                (key, value), = Lazor.reflect_block_location(
                    self, x, y, direction_x, direction_y
                ).items()
                if key in info_dict["block_position"]:
                    if key not in info_dict['passed_blocks'][i] and\
                            info_dict["block_position"][key] != "B":
                        info_dict['passed_blocks'][i].append(key)
                        info_dict['possible_block_position'] = []
                    if info_dict["block_position"][key] == "A":
                        direction_x, direction_y = value
                    elif info_dict["block_position"][key] == "B":
                        if (x, y) in info_dict["map_points"]:
                            info_dict['lazor_path'][i].append((x, y))
                        # Since loop breaks here, last point hitting B
                        # won't be added into path without this line
                        break
                    elif info_dict["block_position"][key] == "C":
                        if (x + direction_x, y + direction_y) not in\
                                info_dict["lazor"]:
                            c_lazor[(x + direction_x, y + direction_y)] =\
                                (direction_x, direction_y)
                        # Creates new lazor and avoids recreating
                        direction_x, direction_y = value
                if (x, y) in info_dict["map_points"]:
                    info_dict['lazor_path'][i].append((x, y))
                (key, value), = Lazor.reflect_block_location(
                    self, x, y, direction_x, direction_y
                ).items()
                if key not in info_dict['possible_block_position'] and\
                    key in info_dict['blank_position'] and\
                        key not in info_dict["block_position"]:
                        info_dict['possible_block_position'].append(key)
                x += direction_x
                y += direction_y
                # Counter to avoid infinite loop
                times += 1
                if times > 100:
                    break
        # recheck lazor starting point
        # make sure it's not blocked at both sides (issues found in Numbered_7)
        for rsb in info_dict['original_lazor']:
            position_x, position_y = rsb
            if (position_x, position_y + 1) in info_dict['block_position'] and\
                    (position_x, position_y - 1) in info_dict[
                        'block_position']:
                up = (position_x, position_y - 1)
                down = (position_x, position_y + 1)
                if (info_dict['block_position'][up] == "A" or "B") and\
                        (info_dict['block_position'][down] == "A" or "B"):
                    info_dict['lazor_path'][rsb] = [rsb]
            elif (position_x - 1, position_y) in info_dict[
                'block_position'] and\
                    (position_x + 1, position_y) in info_dict[
                        'block_position']:
                left = (position_x - 1, position_y)
                right = (position_x + 1, position_y)
                if (info_dict['block_position'][left] == "A" or "B") and\
                        (info_dict['block_position'][right] == "A" or "B"):
                    info_dict['lazor_path'][rsb] = [rsb]
        if c_lazor == {}:
            return info_dict
        else:
            for c in c_lazor:
                info_dict['lazor'][c] = c_lazor[c]
            return Lazor.lazor_path(self, info_dict)
            # run again with newly created lazors

    def all_possible_situations(self, info_dict, possible_list, block_list):
        '''
        Author: Don

        all_possible_situations() function generates new lists which next block
        is putted.
        '''
        new_list = []
        for i in possible_list:
            # it's good to initialize everywhere bc you don't know what
            # info_dict looks like
            info_dict['lazor_path'] = {}
            info_dict['lazor'] = {}
            info_dict['block_position'] = {}
            info_dict['block_position'].update(
                info_dict['fixed_block_position'])
            info_dict['block_position'].update(zip(i, block_list))
            new_path = Lazor.lazor_path(self, info_dict)
            # There are some situations that after you put next block
            # some old blocks are no longer passed, especially when you
            # have two blocks next to each other
            passed_blocks = []
            for pb in info_dict['passed_blocks']:
                passed_blocks += info_dict['passed_blocks'][pb]
            judge = [False for block in i if block not in passed_blocks]
            if new_path['possible_block_position'] != [] and\
                    judge == []:
                for p in new_path['possible_block_position']:
                    new_list.append(i + [p])
            else:
                # when new_path['possible_block_position'] is [],
                # it means this combination is not valid because
                # you have no place for next block
                pass
        return new_list

    def solve_lazor(self, info_dict):
        '''
        Author: Don

        *** METHOD ***
            ** METHOD 1 **
                *   Situation 1:Situations when you've used all blocks. In this
                    case all blocks must be putted on lazor paths.

                *   Make permutations of blocks because they are put in order.
                *   Start from original map for first block possibilities.
                *   Loop through current combinations of blocks, check if all
                    target points are hit.
                *   If satisfies:
                        Check if there are remaining blocks, if yes, send to
                        method 2, otherwise return info_dict
                *   If not:
                        Go to all_possible_situations() to put next block, and
                        loop again.
                *   Loop through all permutations of block types, if all not
                    satisfied, go to method 3.

            ** METHOD 2 **
                *   Situation 2:Situations when there are some block remaining
                    when all target points are hit. Remaing blocks
                    mustn't block lazor paths.

                *   See redundant_blocks()

            ** METHOD 3 **
                *   Situation 3:Situations like dark series, in which you have
                    to block some lazor paths.
                    Also when some bugs occur in former methods,
                    it's always the last chance to solve the problem.

                *   Use itertool.combination to create a list of all
                    combinations of blank positions
                *   Delete_duplicated_elements() is used to remove wrong
                    combinations where you put more than one blocks in
                    same position, so that combinations can be generated
                    by a single for loop.
                *   Loop and check all the combinations, there will always be
                    an answer
        '''

        # Initializations
        info_dict['block_position'] = {}
        moveable_blocks = []
        # No need to put B on path
        for i in info_dict['block']:
            if i != 'B':
                moveable_blocks += [i] * info_dict['block'][i]
        arranged_moveable_blocks = list(
            set(permutations(moveable_blocks, len(moveable_blocks))))
        # Check each combination of blocks
        while arranged_moveable_blocks != []:
            comb = arranged_moveable_blocks[0]
            i = 0
            # Initialization
            info_dict['lazor_path'] = {}
            info_dict['lazor'] = {}
            info_dict['block_position'] = {}
            info_dict['block_position'].update(
                info_dict['fixed_block_position'])
            info_dict = Lazor.lazor_path(self, info_dict)
            # Each possible position is stored as a list so that
            # all_possible_situations() can handle
            possible_list = [[x] for x in info_dict['possible_block_position']]
            while i + 1 < len(comb):
                possible_list = Lazor.all_possible_situations(
                    self, info_dict, possible_list, comb)
                for p in possible_list:
                    # make judges while possible_list is growing
                    judge = Lazor.run_possible_comb(self, info_dict, p, comb)
                    if judge == []:
                        rb = Lazor.redundant_blocks(self, info_dict)
                        # No redundant blocks
                        # Method 1 succeed
                        if rb is False:
                            pass
                        # Method 2 starts
                        else:
                            info_dict['block_position'].update(rb)
                            info_dict = Lazor.lazor_path(self, info_dict)
                            path = []
                            # convert path dictionary
                            # back into a list
                            for p in info_dict['lazor_path']:
                                path += info_dict['lazor_path'][p]
                            judge = [
                                False for c in info_dict['target_point']
                                if c not in path
                            ]
                            if judge == []:
                                return info_dict
                            else:
                                pass
                i += 1
            arranged_moveable_blocks.remove(comb)
        # Method 3
        moveable_blocks = []
        able_positions = []
        violent_combinations = []
        for bp in info_dict['blank_position']:
            able_positions.append(bp)
        for block in info_dict['block']:
            moveable_blocks += [block] * info_dict['block'][block]
            if violent_combinations == []:
                violent_combinations += list(
                    set(combinations(
                        able_positions, info_dict['block'][block])))
            # It's strange but it appears that you cannot directly add
            # combination lists together
            else:
                new_list = []
                for vc in violent_combinations:
                    append = list(
                        combinations(
                            able_positions, info_dict['block'][block]))
                    for ap in append:
                        new_list.append(vc + ap)
                violent_combinations = new_list
        # violent_combinations is a tuple of tuples of tuples
        # convert it back into list
        listed_violent_combinations = []
        for c in violent_combinations:
            test = list(c)
            test = Lazor.delete_duplicated_element(self, test)
            if len(test) == len(moveable_blocks):
                listed_violent_combinations.append(test)
        # check for each combination
        for remain in listed_violent_combinations:
            judge = Lazor.run_possible_comb(
                self, info_dict, remain, moveable_blocks)
            if judge == []:
                return info_dict

    def run_possible_comb(self, info_dict, p, comb):
        '''
        Author: Don

        This function generates the lazor paths by given possible list(p)
        and block order(comb).

        It returns the judges that shows how many target points are not
        on lazor path.
        '''
        info_dict['lazor_path'] = {}
        info_dict['lazor'] = {}
        info_dict['block_position'] = {}
        info_dict['block_position'].update(zip(p, comb))
        info_dict['block_position'].update(
            info_dict['fixed_block_position'])
        info_dict = Lazor.lazor_path(self, info_dict)
        path = []
        for p in info_dict['lazor_path']:
            path += info_dict['lazor_path'][p]
        path = Lazor.delete_duplicated_element(self, path)
        judge = [
            False for c in info_dict['target_point']
            if c not in path
        ]
        return judge

    def redundant_blocks(self, info_dict):
        '''
        Author: Don

        This function modifies the info_dict and generate a 'redundant_list'
        of positions where remaining blocks cannot be putted. Notice it has the
        same idea when generating possible lists in solve_lazor().

        *** METHOD ***
            *   First we move all current locations of blocks.
            *   Check if there are remaining blocks, since situations combine
                method 1 and 2 in solve_lazor()
            *   Move all points after last target point on each lazor path,
                since you can put you block there
            *   Use all_possible_situation() to generate a list of position,
                which in this case they are unable positions
            *   Remove unable positions in blank position, check if it's
                shorter than length of remaining block list. If yes, return
                Flase. Otherwise return a dictionary of remaining locations.

        '''
        moveable_blocks = []
        able_positions = []
        for bp in info_dict['blank_position']:
            able_positions.append(bp)
        for block in info_dict['block']:
            moveable_blocks += [block] * info_dict['block'][block]
        # fixed_blocks are not in blank positions bc it's not on
        # the map, but they are inside block_position list
        for fixed_block in info_dict['block_position']:
            if fixed_block not in info_dict['fixed_block_position']:
                moveable_blocks.remove(
                    info_dict['block_position'][fixed_block])
                able_positions.remove(fixed_block)
        # No remains, Method 1
        if moveable_blocks == []:
            return {}
        # method 2
        else:
            unable_positions = []
            # remove all point after target point
            for lazor in info_dict['lazor_path']:
                test = info_dict['lazor_path'][lazor].pop()
                while test not in info_dict['target_point'] and\
                        info_dict['lazor_path'][lazor] != []:
                    test = info_dict['lazor_path'][lazor].pop()
                # avoid empty list error
                if info_dict['lazor_path'][lazor] == []:
                    pass
                else:
                    x = lazor[0]
                    y = lazor[1]
                    direction_x = info_dict['lazor'][lazor][0]
                    direction_y = info_dict['lazor'][lazor][1]
                    # regenerate locations
                    while (x, y) in info_dict['lazor_path'][lazor]:
                        (key, value), = Lazor.reflect_block_location(
                            self, x, y, direction_x, direction_y
                        ).items()
                        if key not in info_dict['block_position'] and\
                                key in info_dict['blank_position']:
                            unable_positions.append(key)
                        else:
                            direction_x, direction_y = value
                        x += direction_x
                        y += direction_y
            # avoid duplicated elements
            unable_positions = Lazor.delete_duplicated_element(
                self, unable_positions)
            # remove unable positions
            for up in unable_positions:
                able_positions.remove(up)
            # Check if there enough positions for remaining blocks
            if len(able_positions) < len(moveable_blocks):
                return False
            else:
                return zip(able_positions, moveable_blocks)

    def delete_duplicated_element(self, listA):
        '''
        Author: Don

        Little functions to delete duplicated functions from
        a list
        '''
        return sorted(set(listA), key=listA.index)

    def save_txt(self, info_dict):
        '''
        This function is used to generate a .txt file.
        The content of the file is based on the dictionary
        generated from the solve_lazor function.
        (Written by  Xinru)
        '''

        filename = info_dict['filename'] + '.txt'
        f = open(filename, 'w')
        map = info_dict['map']
        block_position = info_dict['block_position']
        for y in range(len(map)):
            for x in range(len(map[0])):
                if (2 * x + 1, 2 * y + 1) in block_position:
                    f.write(block_position[(2 * x + 1, 2 * y + 1)] + ' ')
                else:
                    f.write(map[y][x] + ' ')
            f.write('\n')
        f.close()
        return f

    def set_pixel(self, a, blockSize=50, gapSize=5):
        '''
        This function is to change the value of a variable to pixel value.
        This is widely used in the below functions.
        (written by Xinru)
        '''

        a = gapSize + (blockSize + gapSize) * a
        return a

    def set_tp(self, info_dict):
        '''
        This function is to generate a list of pixel values of target points.
        (written by Xinru)
        '''

        target_point = info_dict['target_point']
        tp = []
        for (x, y) in target_point:
            x = Lazor.set_pixel(self, x) / 2
            y = Lazor.set_pixel(self, y) / 2
            tp.append((x, y))
        return tp

    def set_lp(self, info_dict):
        '''
        This function is to generate a dictionary of pixel values
        of laser path.(written by Xinru)

        *** info_dict ***
        This is a dictionary generated from the above functions.
        It contains information about filename, map, laser, target points, ets.
        This dictionary allows us to generate the image file to show
        how to solve the 'lazor' game.
        '''

        lazor_path = info_dict['lazor_path']
        lp = {}
        for (x0, y0) in lazor_path:
            x1 = Lazor.set_pixel(self, x0) / 2
            y1 = Lazor.set_pixel(self, y0) / 2
            lst = []
            for (x, y) in lazor_path[(x0, y0)]:
                x = Lazor.set_pixel(self, x) / 2
                y = Lazor.set_pixel(self, y) / 2
                lst.append((x, y))
            lp[(x1, y1)] = lst
        return lp

    def save_img(self, info_dict):
        '''
        This function is used to generate a .png file to show clearly
        the answer to the game.(written by Xinru)

        *** info_dict ***
        This is a dictionary generated from the above functions.
        It contains information about filename, map, laser, target points, ets.
        This dictionary allows us to generate the image file to show
        how to solve the 'lazor' game.
        '''

        # Generate a new list of the pixel values of map.
        map = info_dict['map']
        block_position = info_dict['block_position']
        for y in range(len(map)):
            for x in range(len(map[0])):
                if (2 * x + 1, 2 * y + 1) in block_position:
                    map[y][x] = block_position[(2 * x + 1, 2 * y + 1)]

        # Create a new image.
        w_blocks = len(map[0])
        h_blocks = len(map)
        SIZE = (Lazor.set_pixel(self, w_blocks),
                Lazor.set_pixel(self, h_blocks))
        # Set the background of the image.
        img = Image.new("RGB", SIZE, (99, 90, 91))

        # Show three different types of blocks:
        # A - reflect blocks, B - opaque blocks, C - refract blocks
        # and fixed blocks of these three types.
        for y, row in enumerate(map):
            for x, block_ID in enumerate(row):
                if block_ID != 'x':
                    block = Image.open(block_ID + '.jpg')
                    block = block.resize((50, 50))
                    pxl = block.load()
                    for a in range(50):
                        for b in range(50):
                            img.putpixel((Lazor.set_pixel(self, x) + a,
                                         Lazor.set_pixel(self, y) + b),
                                         pxl[a, b])

        # Draw lines to show the path of the laser.
        draw = ImageDraw.Draw(img)
        lazor = info_dict['lazor']
        original_lazor = info_dict['original_lazor']
        lazor_path = Lazor.set_lp(self, info_dict)

        # For laser touching block A/B.
        for (x, y) in lazor:
            if (x, y) in original_lazor:
                x = Lazor.set_pixel(self, x) / 2
                y = Lazor.set_pixel(self, y) / 2
                draw.ellipse((x - 3, y - 3, x + 3, y + 3),
                             fill=(255, 0, 0))
                lst = lazor_path[(x, y)]
                draw.line(lst, width=5, fill=(255, 0, 0))

        # For laser passing block C.
        for (x, y) in lazor:
            if (x, y) not in info_dict['original_lazor']:
                x = Lazor.set_pixel(self, x) / 2
                y = Lazor.set_pixel(self, y) / 2
                lst = lazor_path[(x, y)]
                direction_x = lst[1][0] - lst[0][0]
                direction_y = lst[1][1] - lst[0][1]
                lst.insert(0, (x - direction_x, y - direction_y))
                draw.line(lst, width=5, fill=(255, 0, 0))

        # Draw points to show the position of target points.
        target_point = Lazor.set_tp(self, info_dict)
        for (x, y) in target_point:
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 0, 0))
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 255))
        filename = info_dict['filename']
        img.save(filename + '.png')


if __name__ == "__main__":

    a = Lazor()
    b = a.read_bff('mad_1.bff')
    b = a.load_lazor_map(b)
    b = a.lazor_path(b)
    c = a.solve_lazor(b)
    a.save_txt(c)
    a.save_img(c)
