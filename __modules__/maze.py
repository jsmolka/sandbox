import numpy as np
from enum import Enum
from json import dump, load
from os.path import isfile
from PIL import Image
from random import randint, getrandbits, shuffle


class Algorithm:
    """
    This class contains enumerations for all relevant creating and solving algorithms used in the Maze class
    """
    class Create(Enum):
        BACKTRACKING = "Recursive backtracking algorithm"
        HUNT = "Hunt and kill algorithm"
        ELLER = "Eller's algorithm"
        SIDEWINDER = "Sidewinder algorithm"
        PRIM = "Prim's algorithm"
        KRUSKAL = "Kruskal's algorithm"

    class Solve(Enum):
        DEPTH = "Depth-first search"


class Maze:
    """
    This class contains all relevant methods for creating and solving mazes

    Variable explanation:
    __c_: functions / variables used in create()
    __s_: functions / variables used in solve()
    __c_dir_one: returns new x and y with a step length of 2
    __s_dir_one: returns new x and y with a step length of 1
    __dir_two: returns new and between x and y with a step length of 2
    """
    def __init__(self):
        """Constructor"""
        self.maze = None
        self.solution = None

        self.__c_dir_one = [
            lambda x, y: (x + 2, y),
            lambda x, y: (x - 2, y),
            lambda x, y: (x, y - 2),
            lambda x, y: (x, y + 2)
        ]

        self.__s_dir_one = [
            lambda x, y: (x + 1, y),
            lambda x, y: (x - 1, y),
            lambda x, y: (x, y - 1),
            lambda x, y: (x, y + 1)
        ]

        self.__dir_two = [
            lambda x, y: (x + 2, y, x + 1, y),
            lambda x, y: (x - 2, y, x - 1, y),
            lambda x, y: (x, y - 2, x, y - 1),
            lambda x, y: (x, y + 2, x, y + 1)
        ]

    @property
    def row_count_with_walls(self):
        """Returns row count with walls"""
        if self.maze is not None:
            return len(self.maze)
        elif self.solution is not None:
            return len(self.solution)
        else:
            raise Exception("Maze and solution are not assigned")

    @property
    def col_count_with_walls(self):
        """Returns column count with walls"""
        if self.maze is not None:
            return len(self.maze[0])
        elif self.solution is not None:
            return len(self.solution[0])
        else:
            raise Exception("Maze and solution are not assigned")

    @property
    def row_count(self):
        """Returns row count"""
        return self.row_count_with_walls // 2

    @property
    def col_count(self):
        """Returns column count"""
        return self.col_count_with_walls // 2

    @staticmethod
    def __shuffled(l):
        """Returns shuffled list"""
        result = l[:]
        shuffle(result)
        return result

    def __out_of_bounds(self, x, y):
        """Checks if indices are out of bounds"""
        return True if x < 0 or y < 0 or x >= self.row_count_with_walls or y >= self.col_count_with_walls else False

    def create(self, row_count, col_count, algorithm):
        """Creates maze"""
        if (row_count or col_count) <= 0:
            raise Exception("Row or column count cannot be smaller than zero")

        self.maze = np.zeros((2 * row_count + 1, 2 * col_count + 1, 3), dtype=np.uint8)

        if algorithm == Algorithm.Create.BACKTRACKING:
            self.__c_recursive_backtracking()
        elif algorithm == Algorithm.Create.HUNT:
            self.__c_hunt_and_kill()
        elif algorithm == Algorithm.Create.ELLER:
            self.__c_eller()
        elif algorithm == Algorithm.Create.SIDEWINDER:
            self.__c_sidewinder()
        elif algorithm == Algorithm.Create.PRIM:
            self.__c_prim()
        elif algorithm == Algorithm.Create.KRUSKAL:
            self.__c_kruskal()
        else:
            raise Exception("Wrong algorithm\n"
                            "Use \"Algorithm.Create.<algorithm>\" to choose an algorithm")

    def __c_walk(self, x, y):
        """Walks over maze"""
        for direction in Maze.__shuffled(self.__dir_two):  # Check adjacent cells randomly
            tx, ty, bx, by = direction(x, y)
            if not self.__out_of_bounds(tx, ty) and self.maze[tx, ty, 0] == 0:  # Check if unvisited
                self.maze[tx, ty] = self.maze[bx, by] = [255, 255, 255]  # Mark as visited
                return tx, ty, True  # Return new cell and continue walking

        return x, y, False  # Return old cell and stop walking

    def __c_backtrack(self, stack):
        """Backtracks stack"""
        while stack:
            x, y = stack.pop()
            for direction in self.__c_dir_one:  # Check adjacent cells
                tx, ty = direction(x, y)
                if not self.__out_of_bounds(tx, ty) and self.maze[tx, ty, 0] == 0:  # Check if unvisited
                    return x, y, stack  # Return cell with unvisited neighbour

        return None, None, None  # Return stop values if stack is empty

    def __c_recursive_backtracking(self):
        """Creates maze with recursive backtracking algorithm"""
        stack = list()  # List of visited cells [(x, y), ...]

        x = 2 * randint(0, self.row_count - 1) + 1
        y = 2 * randint(0, self.col_count - 1) + 1
        self.maze[x, y] = [255, 255, 255]  # Mark as visited

        while x:
            walking = True
            while walking:
                stack.append((x, y))
                x, y, walking = self.__c_walk(x, y)
            x, y, stack = self.__c_backtrack(stack)

    def __c_hunt(self, hunt_list):
        """Scans maze for new position"""
        while hunt_list:
            for x in hunt_list:
                finished = True
                for y in range(1, self.col_count_with_walls - 1, 2):
                    if self.maze[x, y, 0] == 0:  # Check if unvisited
                        finished = False
                        for direction in Maze.__shuffled(self.__c_dir_one):  # Check adjacent cells randomly
                            tx, ty = direction(x, y)
                            if not self.__out_of_bounds(tx, ty) and self.maze[tx, ty, 0] == 255:  # Check if visited
                                return tx, ty, hunt_list  # Return visited neighbour of unvisited cell
                if finished:
                    hunt_list.remove(x)  # Remove finished row
                    break  # Restart loop

        return None, None, None  # Return stop values if all rows are finished

    def __c_hunt_and_kill(self):
        """Creates maze with hunt and kill algorithm"""
        hunt_list = list(range(1, self.row_count_with_walls - 1, 2))  # List of unfinished rows [x, ...]

        x = 2 * randint(0, self.row_count - 1) + 1
        y = 2 * randint(0, self.col_count - 1) + 1
        self.maze[x, y] = [255, 255, 255]  # Mark as visited

        while hunt_list:
            walking = True
            while walking:
                x, y, walking = self.__c_walk(x, y)
            x, y, hunt_list = self.__c_hunt(hunt_list)

    def __c_eller(self):
        """Creates maze with Eller's algorithm"""
        row_stack = [0] * self.col_count  # List of set indices [set index, ...]
        set_list = []  # List of set indices with positions [(set index, position), ...]
        set_index = 1

        for x in range(1, self.row_count_with_walls - 1, 2):
            connect_list = []  # List of connections between cells [True, ...]

            # Create row stack
            if row_stack[0] == 0:  # Define first cell in row
                row_stack[0] = set_index
                set_index += 1

            for y in range(1, self.col_count):  # Define other cells in row
                if bool(getrandbits(1)):  # Connect cell with previous cell
                    if row_stack[y] != 0:  # Cell has a set
                        old_index = row_stack[y]
                        new_index = row_stack[y - 1]
                        if old_index != new_index:  # Combine both sets
                            row_stack = [new_index if y == old_index else y for y in row_stack]  # Replace old indices
                            connect_list.append(True)
                        else:
                            connect_list.append(False)
                    else:  # Cell has no set
                        row_stack[y] = row_stack[y - 1]
                        connect_list.append(True)
                else:  # Do not connect cell with previous cell
                    if row_stack[y] == 0:
                        row_stack[y] = set_index
                        set_index += 1
                    connect_list.append(False)

            # Create set list and fill cells
            for y in range(1, self.col_count):
                maze_col = 2 * y + 1
                set_list.append((row_stack[y], maze_col))

                self.maze[x, maze_col] = [255, 255, 255]  # Mark as visited
                if y < self.col_count - 1:
                    if connect_list[y]:
                        self.maze[x, maze_col + 1] = [255, 255, 255]  # Mark as visited

            if x == self.row_count_with_walls - 2:  # Connect all different sets in last row
                for y in range(1, self.col_count):
                    new_index = row_stack[y - 1]
                    old_index = row_stack[y]
                    if new_index != old_index:
                        row_stack = [new_index if y == old_index else y for y in row_stack]  # Replace old indices
                        self.maze[x, 2 * y] = [255, 255, 255]  # Mark as visited
                break  # End loop with last row

            # Reset row stack
            row_stack = [0] * self.col_count

            # Create vertical links
            set_list.sort()
            while set_list:
                sub_set_list = []  # List of set indices with positions for one set index [(set index, position), ...]
                sub_set_index = set_list[0][0]
                while set_list and set_list[0][0] == sub_set_index:  # Create sub list for one set index
                    sub_set_list.append(set_list.pop(0))
                while True:  # Create at least one link for each set index
                    can_break = False
                    link_list = []  # List of links [(set index, column), ...]
                    for sub_set_item in sub_set_list:
                        if bool(getrandbits(1)):  # Create link
                            link_list.append(sub_set_item)
                            can_break = True
                    if can_break:
                        break
                for link in link_list:  # Create links
                    link_set, link_position = link
                    link_stack_position = link_position // 2

                    row_stack[link_stack_position] = link_set  # Assign links to new row stack
                    self.maze[x + 1, link_position] = [255, 255, 255]  # Mark link as visited

    def __c_sidewinder(self):
        """Creates maze with sidewinder algorithm"""
        # Create first row
        for y in range(1, self.col_count_with_walls - 1):
            self.maze[1, y] = [255, 255, 255]

        # Create other rows
        for x in range(3, self.row_count_with_walls, 2):
            row_stack = []  # List of cells without vertical link [y, ...]
            for y in range(1, self.col_count_with_walls - 2, 2):
                self.maze[x, y] = [255, 255, 255]  # Mark as visited
                row_stack.append(y)

                if bool(getrandbits(1)):  # Create vertical link
                    index = randint(0, len(row_stack) - 1)
                    self.maze[x - 1, row_stack[index]] = [255, 255, 255]  # Mark as visited
                    row_stack = []  # Reset row stack
                else:  # Create horizontal link
                    self.maze[x, y + 1] = [255, 255, 255]  # Mark as visited

            # Create vertical link for last cell
            y = self.col_count_with_walls - 2
            self.maze[x, y] = [255, 255, 255]  # Mark as visited
            row_stack.append(y)
            index = randint(0, len(row_stack) - 1)
            self.maze[x - 1, row_stack[index]] = [255, 255, 255]  # Mark as visited

    def __c_prim(self):
        """Creates maze with Prim's algorithm"""
        frontier = list()  # List of unvisited cells [(x, y),...]

        # Start with random cell
        x = 2 * randint(0, self.row_count - 1) + 1
        y = 2 * randint(0, self.col_count - 1) + 1
        self.maze[x, y] = [255, 255, 255]  # Mark as visited

        # Add cells to frontier for random cell
        for direction in self.__c_dir_one:
            tx, ty = direction(x, y)
            if not self.__out_of_bounds(tx, ty):
                frontier.append((tx, ty))
                self.maze[tx, ty] = [1, 1, 1]  # Mark as part of frontier

        # Add and connect cells until frontier is empty
        while frontier:
            x, y = frontier.pop(randint(0, len(frontier) - 1))

            # Connect cells
            for direction in Maze.__shuffled(self.__dir_two):
                tx, ty, bx, by = direction(x, y)
                if not self.__out_of_bounds(tx, ty):
                    if self.maze[tx, ty, 0] == 255:  # Check if visited
                        self.maze[x, y] = self.maze[bx, by] = [255, 255, 255]  # Connect cells
                        break

            # Add cells to frontier
            for direction in self.__c_dir_one:
                tx, ty = direction(x, y)
                if not self.__out_of_bounds(tx, ty):
                    if self.maze[tx, ty, 0] == 0:  # Check if unvisited
                        frontier.append((tx, ty))
                        self.maze[tx, ty] = [1, 1, 1]  # Mark as part of frontier

    def __c_kruskal(self):
        """Creates maze with Kruskal's algorithm"""
        xy_to_set = np.zeros((self.row_count_with_walls, self.col_count_with_walls), dtype=np.uint32)
        set_to_xy = []  # List of sets in order, set 0 at index 0 [[(x, y),...], ...]
        edges = []  # All possible edges
        set_index = 0

        for x in range(1, self.row_count_with_walls - 1, 2):
            for y in range(1, self.col_count_with_walls - 1, 2):
                # Assign sets
                xy_to_set[x, y] = set_index
                set_to_xy.append([(x, y)])
                set_index += 1

                # Create edges
                if not self.__out_of_bounds(x + 2, y):
                    edges.append((x + 1, y, "v"))  # Vertical edge
                if not self.__out_of_bounds(x, y + 2):
                    edges.append((x, y + 1, "h"))  # Horizontal edge

        shuffle(edges)  # Shuffle to pop random edges
        while edges:
            x, y, direction = edges.pop()

            if direction == "v":  # Vertical edge
                x1 = x - 1
                x2 = x + 1
                if xy_to_set[x1, y] != xy_to_set[x2, y]:  # Check if cells are in different sets
                    self.maze[x, y] = self.maze[x1, y] = self.maze[x2, y] = [255, 255, 255]  # Mark as visited

                    new_set = xy_to_set[x1, y]
                    old_set = xy_to_set[x2, y]

                    # Extend new set with old set
                    set_to_xy[new_set].extend(set_to_xy[old_set])

                    # Correct sets in xy sets
                    for pos in set_to_xy[new_set]:
                        xy_to_set[pos] = new_set

            else:  # Horizontal edge
                y1 = y - 1
                y2 = y + 1
                if xy_to_set[x, y1] != xy_to_set[x, y2]:  # Check if cells are in different sets
                    self.maze[x, y] = self.maze[x, y1] = self.maze[x, y2] = [255, 255, 255]  # Mark as visited

                    new_set = xy_to_set[x, y1]
                    old_set = xy_to_set[x, y2]

                    # Extend new set with old set
                    set_to_xy[new_set].extend(set_to_xy[old_set])

                    # Correct sets in xy sets
                    for pos in set_to_xy[new_set]:
                        xy_to_set[pos] = new_set

    def solve(self, start, end, algorithm):
        """Solves maze"""
        if self.maze is None:
            raise Exception("Maze is not assigned\n"
                            "Use \"create\" or \"load_maze\" method to create or load a maze")

        if start == 0:
            start = (0, 0)
        if end == 0:
            end = (self.row_count - 1, self.col_count - 1)

        if not 0 <= start[0] < self.row_count:
            raise Exception("Start row value is out of range")
        if not 0 <= start[1] < self.col_count:
            raise Exception("Start column value is out of range")
        if not 0 <= end[0] < self.row_count:
            raise Exception("End row value is out of range")
        if not 0 <= end[1] < self.col_count:
            raise Exception("End column value is out of range")

        start = tuple([2 * x + 1 for x in start])
        end = tuple([2 * x + 1 for x in end])

        self.solution = self.maze.copy()

        if algorithm == Algorithm.Solve.DEPTH:
            self.__s_depth_first_search(start, end)
        else:
            raise Exception("Wrong algorithm\n"
                            "Use \"Algorithm.Solve.<algorithm>\" to choose an algorithm")

    def __s_walk(self, x, y, stack, visited_cells):
        """Walks over maze"""
        for direction in self.__dir_two:  # Check adjacent cells
            tx, ty, bx, by = direction(x, y)
            if visited_cells[bx, by, 0] == 255:  # Check if unvisited
                visited_cells[bx, by] = visited_cells[tx, ty] = [0, 0, 0]  # Mark as visited
                stack.extend([(bx, by), (tx, ty)])
                return tx, ty, stack, visited_cells, True  # Return new cell and continue walking

        return x, y, stack, visited_cells, False  # Return old cell and stop walking

    def __s_backtrack(self, stack, visited_cells):
        """Backtracks stacks"""
        while stack:
            x, y = stack.pop()
            for direction in self.__s_dir_one:  # Check adjacent cells
                tx, ty = direction(x, y)
                if visited_cells[tx, ty, 0] == 255:  # Check if unvisited
                    stack.append((x, y))
                    return x, y, stack  # Return cell with unvisited neighbour

        return None, None, None  # Return stop values if stack is empty and no new cell was found

    def __s_depth_first_search(self, start, end):
        """Solves maze with depth-first search"""
        visited_cells = self.maze.copy()  # List of visited cells, value of visited cell is [0, 0, 0]
        stack = list()  # List of visited cells [(x, y), ...]

        x, y = start
        stack.append((x, y))
        visited_cells[x, y] = [0, 0, 0]  # Mark as visited

        while x:
            walking = True
            while walking:
                x, y, stack, visited_cells, walking = self.__s_walk(x, y, stack, visited_cells)
                if (x, y) == end:  # Stop if end has been found
                    r, g, b, offset = 255, 0, 0, 255 / len(stack)
                    while stack:  # Color path
                        r -= offset
                        b += offset
                        self.solution[stack.pop()] = [r, g, b]
                    return
            x, y, stack = self.__s_backtrack(stack, visited_cells)

        raise Exception("No solution found")

    def save_maze_as_png(self, file_name="maze.png", upscale_factor=3):
        """Saves maze as png"""
        if self.maze is None:
            raise Exception("Maze is not assigned\n"
                            "Use \"create\" or \"load_maze\" method to create or load a maze")

        img = Image.fromarray(Maze.__upscale(self.maze, upscale_factor), "RGB")
        img.save(file_name, "png")

    def save_maze_as_json(self, file_name="maze.json", fancy=False):
        """Saves maze as json"""
        if self.maze is None:
            raise Exception("Maze is not assigned\n"
                            "Use \"create\" or \"load_maze\" method to create or load a maze")

        with open(file_name, "w") as outfile:
            if fancy:
                dump(self.maze.tolist(), outfile, indent=4)
            else:
                dump(self.maze.tolist(), outfile)

    def save_solution_as_png(self, file_name="solution.png", upscale_factor=3):
        """Saves solution as png"""
        if self.solution is None:
            raise Exception("Solution is not assigned\n"
                            "Use \"solve\" method to solve a maze")

        img = Image.fromarray(Maze.__upscale(self.solution, upscale_factor), "RGB")
        img.save(file_name, "png")

    def save_solution_as_json(self, file_name="solution.json", fancy=False):
        """Saves solution as json"""
        if self.solution is None:
            raise Exception("Solution is not assigned\n"
                            "Use \"solve\" method to solve a maze")

        with open(file_name, "w") as outfile:
            if fancy:
                dump(self.solution.tolist(), outfile, indent=4)
            else:
                dump(self.solution.tolist(), outfile)

    def load_maze_from_png(self, file_name="maze.png"):
        """Loads maze from png"""
        if not isfile(file_name):
            raise Exception("{0} does not exist".format(file_name))

        image = Image.open(file_name)
        self.maze = Maze.__downscale(np.array(image))

    def load_maze_from_json(self, file_name="maze.json"):
        """Loads maze from json"""
        if not isfile(file_name):
            raise Exception("{0} does not exist".format(file_name))

        with open(file_name) as data_file:
            self.maze = np.array(load(data_file))

    def load_solution_from_png(self, file_name="solution.png"):
        """Loads solution from png"""
        if not isfile(file_name):
            raise Exception("{0} does not exist".format(file_name))

        image = Image.open(file_name)
        self.solution = Maze.__downscale(np.array(image))

    def load_solution_from_json(self, file_name="solution.json"):
        """Loads solution from json"""
        if not isfile(file_name):
            raise Exception("{0} does not exist".format(file_name))

        with open(file_name) as data_file:
            self.solution = np.array(load(data_file))

    @staticmethod
    def __upscale(maze, factor):
        """Upscales maze"""
        if factor <= 1:
            return np.array(maze)
        row_count = len(maze)
        col_count = len(maze[0])
        scaled_maze = np.zeros((factor * row_count, factor * col_count, 3), dtype=np.uint8)

        for x in range(0, row_count):
            for y in range(0, col_count):
                for i in range(0, factor):
                    for j in range(0, factor):
                        scaled_maze[factor * x + i, factor * y + j] = maze[x, y]

        return scaled_maze

    @staticmethod
    def __downscale(maze):
        """Downscales maze"""
        row_count = len(maze)
        col_count = len(maze[0])

        factor = 0
        stop = False
        for x in range(1, row_count):
            for y in range(1, col_count):
                if maze[x, y, 0] != 0:
                    stop = True
                    factor = x
                    break
            if stop:
                break
        if factor <= 1:
            return np.array(maze)

        row_count = row_count // factor
        col_count = col_count // factor
        scaled_maze = np.zeros((row_count, col_count, 3), dtype=np.uint8)

        for x in range(0, row_count):
            for y in range(0, col_count):
                scaled_maze[x, y] = maze[x * factor, y * factor]

        return scaled_maze
