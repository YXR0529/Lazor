'''
Don: finished loading map and loading lazor path
working on solving
'''
from itertools import permutations, combinations
from PIL import Image, ImageDraw


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
            # Generate list/dictionary with information of blocks/lazors/target points.
            if line.startswith('A') or line.startswith('B') or line.startswith('C'):
                lst = line.strip("\n").split(" ")
                block[lst[0]] = int(lst[1])
            if line.startswith('L'):
                lst = line.strip("\n").split(" ")
                lazor[(int(lst[1]),int(lst[2]))] = [int(lst[3]),int(lst[4])]
            if line.startswith('P'):
                lst = line.strip("\n").split(" ")
                point.append((int(lst[1]),int(lst[2])))
        # Add to the dictionary.
        file["block"] = block
        file["original_lazor"] = lazor
        file["target_point"] = point
        # Close the file
        f.close()
        return file

    def load_lazor_map(self, info_dict):
        '''
        This part is written by Don.
        Load_lazor_map() function reads the raw information from read_bff()
        function, whose output contains map organization in the form of
        [['o'], ['A']]

        The output is a dictionary which contains three parts of information:
        *** map_points ***
            the position which the lazor may pass through,
            stored as a list of tuples.
        *** possible_block_position ***
            possible positions which blocks can be put in.
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
                        info_dict["fixed_block_position"]\
                            [(2 * x + 1, 2 * y + 1)] = raw_info[y][x]
        for f in info_dict['fixed_block_position']:
            info_dict['block_position'][f] =\
                info_dict['fixed_block_position'][f]
        for target_point in info_dict['target_point']:
            if target_point not in info_dict['map_points']:
                info_dict['map_points'].append(target_point)
        return info_dict

    def reflect_block_location(
        self, position_x, position_y, direction_x, direction_y
    ):
        '''
        Written by Don.

        This function is seperated from lazor_path(), in order to avoid too
        many if-else judgements.

        After discussion, we notice that at upper/lower bound of a block,
        x changes direction while at left/right bound, y changes direction.
        '''
        if position_y % 2 == 1:
            return {(position_x + direction_x, position_y):
                    [direction_x * -1, direction_y]}
        elif position_x % 2 == 1:
            return {(position_x, position_y + direction_y):
                    [direction_x, direction_y * -1]}

    def lazor_path(self, info_dict):
        '''
        Written by Don.

        Full comment will be updated after I add the last part of generating
        possible location of next block.
        '''
        info_dict['lazor_path'] = {}
        c_lazor = {}
        info_dict['lazor'].update(info_dict["original_lazor"])
        for i in info_dict['lazor']:
            if i not in info_dict['lazor_path']:
                info_dict['lazor_path'][i] = []
            x = i[0]
            y = i[1]
            direction_x = info_dict["lazor"][i][0]
            direction_y = info_dict["lazor"][i][1]
            passed_blocks = []
            while 0 <= x <= info_dict['map_length'] and\
                    0 <= y <= info_dict['map_height']:
                (key, value), = Lazor.reflect_block_location(
                    self, x, y, direction_x, direction_y
                ).items()
                if key in info_dict["block_position"]:
                    if (x + direction_x, y) not in passed_blocks and\
                            info_dict["block_position"][key] != "B":
                        passed_blocks.append(key)
                        info_dict['possible_block_position'] = []
                    if info_dict["block_position"][key] == "A":
                        direction_x, direction_y = value
                    elif info_dict["block_position"][key] == "B":
                        break
                    elif info_dict["block_position"][key] == "C":
                        if (x + direction_x, y + direction_y) not in\
                                info_dict["lazor"]:
                            c_lazor[(x + direction_x, y + direction_y)] =\
                                (direction_x, direction_y)
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
        if c_lazor == {}:
            return info_dict
        else:
            for c in c_lazor:
                info_dict['lazor'][c] = c_lazor[c]
            return Lazor.lazor_path(self, info_dict)

    def all_possible_situations(self, info_dict, possible_list, block_list):
        '''
        '''
        new_list = []
        for i in possible_list:
            info_dict['lazor_path'] = {}
            info_dict['lazor'] = {}
            info_dict['block_position'] = {}
            info_dict['block_position'].update(
                info_dict['fixed_block_position'])
            info_dict['block_position'].update(zip(i, block_list))
            new_path = Lazor.lazor_path(self, info_dict)
            if new_path['possible_block_position'] != []:
                for p in new_path['possible_block_position']:
                    new_list.append(i + [p])
        return new_list

    def solve_lazor(self, info_dict):
        '''
        '''
        info_dict['block_position'] = {}
        moveable_blocks = []
        for i in info_dict['block']:
            if i != 'B':
                moveable_blocks += [i] * info_dict['block'][i]
        arranged_moveable_blocks = list(
            set(permutations(moveable_blocks, len(moveable_blocks))))
        for comb in arranged_moveable_blocks:
            print(comb)
            i = 0
            info_dict['lazor_path'] = {}
            info_dict['lazor'] = {}
            info_dict['block_position'] = {}
            info_dict['block_position'].update(
                info_dict['fixed_block_position'])
            info_dict = Lazor.lazor_path(self, info_dict)
            possible_list = [[x] for x in info_dict['possible_block_position']]
            while i < len(comb):
                possible_list = Lazor.all_possible_situations(
                    self, info_dict, possible_list, comb)
                print(possible_list)
                for p in possible_list:
                        info_dict['lazor_path'] = {}
                        info_dict['lazor'] = {}
                        info_dict['block_position'] = {}
                        info_dict['block_position'].update(zip(p, comb))
                        info_dict['block_position'].update(
                            info_dict['fixed_block_position'])
                        info_dict = Lazor.lazor_path(self, info_dict)
                        print(info_dict)
                        path = []
                        for p in info_dict['lazor_path']:
                            path += info_dict['lazor_path'][p]
                        judge = [
                            False for c in info_dict['target_point']
                            if c not in path
                        ]
                        print(judge)
                        if judge == []:
                            return info_dict
                i += 1
        return info_dict

    def save_txt(self):
        '''
        '''
        pass

    def set_color(self, img, x0, y0, dim, gap, color):
        '''
        \\
        '''

        for x in range(dim):
            for y in range(dim):
                img.putpixel(
                    (gap + (gap + dim) * x0 + x, gap + (gap + dim) * y0 + y),
                    color
                )

    def set_tp(self, info_dict, dim, gap):
        '''
        '''
        target_point = info_dict['target_point']
        tp = []
        for (x, y) in target_point:
            x = (gap + (gap + dim) * x) / 2
            y = (gap + (gap + dim) * y) / 2
            tp.append((x,y))
        return tp

    def set_lp(self, info_dict, dim, gap):
        '''
        '''
        lazor_path = info_dict['lazor_path']


    def save_img(self, info_dict, filename, blockSize=50, gapSize=5):
        '''
        '''
        COLORS = {
            'A': (255, 255, 255),  # white
            'B': (0, 0, 0),  # black
            'C': (245, 245, 245),  # transparent
            'o': (192, 192, 192),
            'x': (128, 128, 128),
            'lazor': (255, 0, 0),
            'target_point': (255, 0, 0)
        }

        map = info_dict['map']
        block_position = info_dict['block_position']
        for y in range(len(map)):
            for x in range(len(map[0])):
                if (2 * x + 1, 2 * y + 1) in block_position:
                    map[y][x] = block_position[(2 * x + 1, 2 * y + 1)]

        w_blocks = len(map[0])
        h_blocks = len(map)
        SIZE = (w_blocks * (blockSize + gapSize) + gapSize,
                h_blocks * (blockSize + gapSize) + gapSize)
        img = Image.new("RGB", SIZE, color=COLORS['x'])

        for y, row in enumerate(map):
            for x, block_ID in enumerate(row):
                Lazor.set_color(self, img,
                                x, y, blockSize, gapSize, COLORS[block_ID])

        lazor = info_dict['lazor_path']

        draw = ImageDraw.Draw(img)
        target_point = Lazor.set_tp(self, info_dict, blockSize, gapSize)
        for (x, y) in target_point:
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=COLORS['target_point'])
        img.save(filename)

    def General(self):
        '''
        '''
        pass


if __name__ == "__main__":
    # diagonal 8
    info_dict = {
        'map': [
            ["o", "o", 'o', 'o'],
            ["B", "o", 'o', 'o'],
            ["o", "x", 'o', 'o'],
            ["o", "o", 'B', 'o'],
            ["o", "o", 'o', 'o']
        ],
        'lazor': {},
        'block': {
            'A': 4,
            'C': 2
        },
        'original_lazor': {
            (8, 7): [-1, -1]
        },
        "target_point": [(2, 3), (3, 4), (4, 5), (5, 6), (6, 7)],
        'block_position': {
        }
    }
    # Braid 8
    info_dict_2 = {
        'map': [
            ["o", "x", 'o', 'o'],
            ["o", "o", 'o', 'o'],
            ["o", "o", 'o', 'o'],
            ["o", "o", 'o', 'o'],
            ["o", "o", 'o', 'o'],
            ["o", "o", 'o', 'o']
        ],
        'lazor': {},
        'block': {
            'A': 5
        },
        'original_lazor': {
            (2, 1): [1, 1],
            (4, 1): [-1, 1]
        },
        "target_point": [(5, 2), (5, 4), (5, 6), (5, 8), (5, 10)],
        'block_position': {
        }
    }
    a = Lazor()
    b = a.read_bff('yarn_6.bff')
    # print(b['original_lazor'])
    b = a.load_lazor_map(b)
    b = a.lazor_path(b)
    g = a.load_lazor_map(info_dict_2)
    # print(g)
    g = a.lazor_path(g)
    # print(g)
    # c = a.load_lazor_map(b)
    # d = a.lazor_path(c)
    # b['block_position'] = {}
    # f = a.load_lazor_map(b)
    # print(f)
    # possible_block_position = list(combinations(g['blank_position'], 6))
    # print(len(possible_block_position))
    k = a.solve_lazor(b)
    print(k)
    a.save_txt(k, 'tricky_6.txt')
    a.save_img(k, 'tricky_6.png')
    # g = a.solve_lazor(g)
    # print(g)
    '''
    for i in possible_block_position:
        g['lazor'] = {}
        g['block_position'] = {}
        arranged_moveable_blocks = list(
            set(permutations(['A', "A", 'A', 'A', 'C', 'C'], 6)))
        for k in arranged_moveable_blocks:
            for j in range(len(k)):
                g['block_position'][i[j]] = k[j]
            g['block_position'][(1, 3)] = "B"
            g['block_position'][(5, 7)] = "B"
            g = a.lazor_path(g)
            path = []
            for lpath in g['lazor_path']:
                for s in g['lazor_path'][lpath]:
                    path.append(s)
            if (2, 3) in path and (3, 4) in path and (4, 5) in path and (5, 6) in path and (6, 7) in path:
                print(possible_block_position.index(i))
                break
    print(path)
    print(g)
    '''
    '''
    g = a.lazor_path(f)
    h = a.solve_lazor(g)
    '''
