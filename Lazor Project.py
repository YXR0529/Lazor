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
        *** points ***
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
        info_dict['points'] = []
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
                        if p not in info_dict['points']:
                            info_dict['points'].append(p)
                    if raw_info[y][x] == 'o':
                        info_dict['blank_position'].append(
                            (2 * x + 1, 2 * y + 1)
                        )
                    else:
                        info_dict["fixed_block_position"][(2 * x + 1, 2 * y + 1)] = [raw_info[y][x]]
        return info_dict

    def lazor_path(self, info_dict):
        info_dict['lazor_path'] = []
        info_dict['possible_block_position'] = []
        c_lazor = {}
        for i in info_dict['lazor']:
            x = i[0]
            y = i[1]
            direction_x = info_dict["lazor"][i][0]
            direction_y = info_dict["lazor"][i][1]
            reflected_times = 0
            possible_position = []
            while 0 <= x <= info_dict['map_length'] and 0 <= y <= info_dict['map_height']:
                if y % 2 == 1 and (x + direction_x, y) in info_dict["block_position"]:
                    if reflected_times >= len(info_dict['block_position']):
                        pass
                    else:
                        possible_position = []
                        reflected_times += 1
                    if info_dict["block_position"][(x + direction_x, y)] == "A":
                        direction_x = direction_x * -1
                    elif info_dict["block_position"][(x + direction_x, y)] == "B":
                        break
                    elif info_dict["block_position"][(x + direction_x, y)] == "C":
                        if (x + direction_x, y + direction_y) not in info_dict["lazor"]:
                            c_lazor[(x + direction_x, y + direction_y)] = (direction_x, direction_y)
                        direction_x = direction_x * -1
                elif x % 2 == 1 and (x, y + direction_y) in info_dict["block_position"]:
                    if reflected_times >= len(info_dict['block_position']):
                        pass
                    else:
                        possible_position = []
                        reflected_times += 1
                    if info_dict["block_position"][(x, y + direction_y)] == "A":
                        direction_y = direction_y * -1
                    elif info_dict["block_position"][(x, y + direction_y)] == "B":
                        break
                    elif info_dict["block_position"][(x, y + direction_y)] == "C":
                        if (x + direction_x, y + direction_y) not in info_dict["lazor"]:
                            c_lazor[(x + direction_x, y + direction_y)] = (direction_x, direction_y)
                        direction_y = direction_y * -1
                if (x, y) not in info_dict['lazor_path'] and (x, y) in info_dict["points"]:
                    info_dict['lazor_path'].append((x, y))
                x += direction_x
                y += direction_y
                possible_position.append((x, y))
            for p in possible_position:
                info_dict['possible_block_position'].append(i)
        if c_lazor == {}:
            return info_dict
        else:
            for c in c_lazor:
                info_dict['lazor'][c] = c_lazor[c]
            return Lazor.load_lazor_map(self, info_dict)

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
    info_dict = {
        'map': [
            ["o", "o", 'o', 'o'],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o']
        ],
        'lazor': {
            (8, 7): [-1, -1]
        },
        'block_position': {
        (5, 3): "A",
        (1, 5): "A",
        (3, 7): "C",
        (5, 7): "B"}
    }
    a = Lazor()
    a.load_lazor_map(info_dict)
    b = a.lazor_path(a.load_lazor_map(info_dict))
    print(b)
