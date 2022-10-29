#!/usr/bin/env

from PIL import Image
import numpy as np
import xlsxwriter
import io

import heapq

PIXMAP = {
    (255, 255, 255): [9, '⬜️'], # white : passage
    (  0,   0,   0): [0, '⬛️'], # black : wall
    (255,   0,   0): [1, '🟥'], # red   : boss
    ( 55,  59, 255): [2, '🟦'], # blue  : landmark
    ( 57, 156,  42): [3, '🟩'], # green : fountain
    (137, 121, 216): [4, '🟪'], # lilac : monster
    (255, 162,   0): [5, '🟧'], # orange: bonfire
    (  7, 237, 130): [6, '🟨'], # cyan  : treasure
}

CARDINALS = {
    (-1,  0): ["N", "🔼"],
    ( 1,  0): ["S", "🔽"],
    ( 0,  1): ["E", "▶️"],
    ( 0, -1): ["W", "◀️"],
}

def print_route(route):
    route_str = ""
    prev = tuple()
    for curr in route:
        if not prev:
            prev = curr
            continue
        diff = np.array(curr) - np.array(prev)
        route_str += CARDINALS[tuple(diff)][1]
        prev = curr
    return route_str


class Maze(object):
    def __init__(self, maze) -> None:
        palette_im = Image.open('palette.png')
        maze_im = Image.open(maze).quantize(8, method=Image.Quantize.LIBIMAGEQUANT, palette=palette_im, dither=Image.Dither.NONE).convert(mode="RGB")
        self.scaled_maze = maze_im.reduce(5).quantize(8, palette=palette_im).convert(mode="RGB")
        nim = np.array(self.scaled_maze)
        self.width, self.height = self.scaled_maze.size
        self.maze_arr = np.array([[PIXMAP[tuple(pixel)][0] for pixel in row] for row in nim])

    def find(self, block_type, current_block) -> set:
        """Return 5 nearest blocks to current"""
        return set(map(tuple, np.asarray(np.where(self.maze_arr == block_type)).T))


    def _manhattan_distance(self, p1, p2):
        d = 0
        for x1, x2 in zip(p1, p2):
            d += np.abs(x2 - x1)
        return d
    
    def _astar(self, start, goal):
        # For now our heuristic function is just the manhattan distance
        # TODO: improve heuristic by factoring in treasures, bonfires and fountains
        def h(p1, p2):
            costs = {
                0: 6,
                1: 0,
                2: 6,
                3: 0,
                4: 10,
                5: 2,
                6: 1,
                9: 1
            }
            return self._manhattan_distance(p1, p2) + (costs[self.maze_arr[p1]] + costs[self.maze_arr[p2]])//2
        # h = self._manhattan_distance
        # Allowed movements
        # North (-1, 0) South (1, 0) East (0, 1) West (0, -1)
        neighbours = CARDINALS.keys()

        # Set used to track the nodes already visited
        visited = set()

        # For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from start
        # to n currently known.
        came_from = {}

        # For node n, gScore[n] is the cost of the cheapest path from start to n currently known.
        gscore = {}
        gscore[start] = 0

        # For node n, fScore[n] := gScore[n] + h(n). fScore[n] represents our current best guess as to
        # how cheap a path could be from start to finish if it goes through n.
        fscore = {}
        fscore[start] = h(start, goal)
        
        # The set of discovered nodes that may need to be (re-)expanded.
        # Initially, only the start node is known.
        # This is usually implemented as a min-heap or priority queue rather than a hash-set.
        open_set = []
        heapq.heappush(open_set, (fscore[start], start))

        while open_set:
            # Set current to the node from open_set with the lowest fscore value
            # This occurs in O(Log(N)) time since open_set is a min-heap
            current = heapq.heappop(open_set)[1]
            if current == goal:
                # Goal has been reached so now we reconstruct the path.
                # Note the path would be in reverse order from goal -> start so we append the
                # start and then reverse the order to obtain start -> goal.
                data = []
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                data.append(start)
                data.reverse()
                return data
            # Add the current node to visited
            visited.add(current)
            for i,j in neighbours:
                # for each of the neigbours of our current node
                neighbour = current[0]+i, current[1]+j
                # calculate their tentative gscore which is the gscore to current + distance to neighbour
                tentative_g_score = gscore[current] + h(current, neighbour)
                # some bounds checking on the neighbour to see if it is within the maze
                if 0 <= neighbour[0] < self.maze_arr.shape[0]:
                    if 0 <= neighbour[1] < self.maze_arr.shape[1]:
                        if self.maze_arr[neighbour[0]][neighbour[1]] == 0:
                            # the neigbour is in a wall so we skip
                            continue
                    else:
                        # neighbour is out of x_bound so we skip
                        continue
                else:
                    # neighbour is out of y_bound so we skip
                    continue
                if (neighbour in visited) and (tentative_g_score >= gscore.get(neighbour, 0)):
                    # the neighbour has already been visited before and already has a lower score so we skip
                    continue
                if (tentative_g_score < gscore.get(neighbour, 0)) or (neighbour not in [i[1] for i in open_set]):
                    # the path to this neigbour is better than any previous path and it is not already in the open_set
                    # so we calculate the gscore and fscore, record it and push it onto our min-heap open_set
                    came_from[neighbour] = current
                    gscore[neighbour] = tentative_g_score
                    fscore[neighbour] = tentative_g_score + h(neighbour, goal)
                    heapq.heappush(open_set, (fscore[neighbour], neighbour))

        # open_set is empty but we were unable to reach our goal
        # so there is no path from start to goal
        return []

    def xlsx(self, filename=None, map_route=None):
        if filename:
            workbook = xlsxwriter.Workbook(filename)
        else:
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)

        worksheet = workbook.add_worksheet('maze')
        
        cell_formats = {}

        for rgb, i in PIXMAP.items():
            cell_formats[i[0]] = workbook.add_format({'bg_color': "#{:02x}{:02x}{:02x}".format(*rgb)})
        for i in range(self.height):
            for j in range(self.width):
                text = None
                x = self.maze_arr[i,j]
                if (i,j) in map_route:
                    text = "★"
                worksheet.write(i, j, text, cell_formats[x])

        worksheet.set_column_pixels(0, self.width, 17)

        workbook.close()
        if filename:
            return None
        else:
            output.seek(0)
            return output

    def __repr__(self) -> str:
        return str(self.maze_arr)