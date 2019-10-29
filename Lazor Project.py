'''
每次Update，在此处写上更新的内容和新实现的功能
'''


class Lazor():
    '''
    '''

    def __init__(self):
        '''
        '''
        pass

    def read_bff(self):
        '''
        '''
        pass

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
                            [(2 * x + 1, 2 * y + 1)] = [raw_info[y][x]]
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
        info_dict['possible_block_position'] = {}
        c_lazor = {}
        for i in info_dict['lazor']:
            if i not in info_dict['lazor_path']:
                info_dict['lazor_path'][i] = []
                info_dict['possible_block_position'][i] = []
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
                    if (x + direction_x, y) not in passed_blocks:
                        passed_blocks.append(key)
                        info_dict['possible_block_position'][i] = []
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
                if key not in info_dict['possible_block_position'][i] and\
                    key in info_dict['blank_position'] and\
                        key not in info_dict["block_position"]:
                    info_dict['possible_block_position'][i].append(key)
                x += direction_x
                y += direction_y

        if c_lazor == {}:
            return info_dict
        else:
            for c in c_lazor:
                info_dict['lazor'][c] = c_lazor[c]
            return Lazor.load_lazor_map(self, info_dict)

    def solve_lazor(self):
        '''
        注意：有些地图中的目标点在地图之外！
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
    # Diagonal 7
    info_dict = {
        'map': [
            ["x", "o", 'o', 'o'],
            ['x', 'x', 'o', 'o'],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'x']
        ],
        'lazor': {
            (8, 7): [-1, -1],
            (7, 4): [1, -1]
        },
        'block_position': {
            (5, 3): "A",
            (1, 5): "A",
            (3, 7): "A",
            (5, 9): "A",
            (7, 5): "C"
        }
    }
    a = Lazor()
    b = a.load_lazor_map(info_dict)
    c = a.lazor_path(b)
    print(b)