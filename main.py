#!/usr/bin/env python3

from maze import Maze, print_route

if __name__ == '__main__':
    m = Maze('maze.jpg')
    boss_pos = tuple(m.find(1, (0,0))[0])
    bonfire_pos = (76, 23)
    route = m._astar(bonfire_pos, boss_pos)
    print(print_route(route))