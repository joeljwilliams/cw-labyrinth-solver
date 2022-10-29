#!/usr/bin/env python3

from maze import Maze, print_route

if __name__ == '__main__':
    m = Maze('maze.jpg')
    # m.xlsx('maze.xlsx')
    boss_pos = tuple(m.find(1, None))[0]
    bonfire_pos = (8, 155)
    route = m._astar(bonfire_pos, boss_pos)
    fountains = m.find(3, None)
    f_on_r = set(route) & fountains
    print("Total Steps: ", len(route))
    print("Heals on Route: ", len(f_on_r))
    m.xlsx('maze.xlsx', map_route=route)
    print(print_route(route))