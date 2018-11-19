# Insert your code here
import math


class MazeError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message


class Maze(object):
    def __init__(self, file):
        datas = []
        for line in open(file):
            data = []
            for c in line:
                if not c.isspace():
                    if c.isdigit():
                        data.append(int(c))
                    else:
                        raise MazeError('Incorrect input.')
            if len(data):
                datas.append(data)
        Maze.valid_input(datas)
        self.filename = file.split('.')[0]
        self.datas = datas
        self.visited = []
        self.analysed = False
        self.height = len(datas)
        self.width = len(datas[0])
        self.augment_graph = [[False for i in range(self.width + 1)] for i in range(self.height + 1)]
        self.count_neighbors = [[0 for i in range(self.width + 1)] for i in range(self.height + 1)]
        self.augment_graph_gates = []
        self.cur_del_sec_set = []
        self.entry_exit_path = []

    # validate the input data
    @staticmethod
    def valid_input(data):
        if len(data) < 2 or len(data) > 41:
            raise MazeError('Incorrect input.')
        size = len(data[0])
        for line in data:
            if len(line) != size or len(line) < 2 or len(line) > 31:
                raise MazeError('Incorrect input.')
            if line[-1] in [1, 3]:
                raise MazeError('Input does not represent a maze.')
        if 2 in data[-1] or 3 in data[-1]:
            raise MazeError('Input does not represent a maze.')

    def connected(self, row, col):
        result = []
        if row > 0 and self.datas[row - 1][col] in [2, 3]:  # top
            result.append((row - 1, col))
        if col > 0 and self.datas[row][col - 1] in [1, 3]:  # left
            result.append((row, col - 1))
        if self.datas[row][col] in [1, 3]:
            result.append((row, col + 1))
        if self.datas[row][col] in [2, 3]:
            result.append((row + 1, col))
        return result

    def dfs_walls(self, row, col):
        self.visited[row][col] = True
        candidates = self.connected(row, col)
        for point in candidates:
            if not self.visited[point[0]][point[1]]:
                self.dfs_walls(point[0], point[1])

    def dfs_walls_wrapper(self):
        height = len(self.datas)
        width = len(self.datas[0])
        self.visited = [[False for i in range(width)] for i in range(height)]
        count = 0
        for i in range(height):
            for j in range(width):
                if (not self.visited[i][j]) and len(self.connected(i, j)):
                    count = count + 1
                    self.dfs_walls(i, j)
        return count

    def count_gates(self):
        count = 0
        for i in range(len(self.datas[0])-1):
            if (0, i+1) not in self.connected(0, i):
                count = count + 1
                self.augment_graph_gates.append((0, i+1))
        for i in range(len(self.datas) - 1):
            if (i+1, 0) not in self.connected(i, 0):
                count = count + 1
                self.augment_graph_gates.append((i + 1, 0))
            if (i+1, len(self.datas[0]) - 1) not in self.connected(i, len(self.datas[0])-1):
                count = count + 1
                self.augment_graph_gates.append((i + 1, len(self.datas[0])))
        for i in range(len(self.datas[0]) - 1):
            if (len(self.datas) - 1, i+1) not in self.connected(len(self.datas) - 1, i):
                count = count + 1
                self.augment_graph_gates.append((len(self.datas), i + 1))
        return count

    def block_edge_tile(self):
        for i in range(len(self.visited)):
            for j in range(len(self.visited[0])):
                if i == 0 or j == 0 or i == len(self.visited) -1 or j == len(self.visited[0])-1:
                    if (i,  j) not in self.augment_graph_gates:
                        self.visited[i][j] = True

    def transfer_gate(self, row1, col1, row2, col2):
        if row1 == row2 and (row1 == 0 or row1 == self.height):
            return True
        if col1 == col2 and (col1 == 0 or col1 == self.width):
            return True
        return False

    def inaccessible(self):
        count = 0
        for i in range(1, len(self.visited)-1):
            for j in range(1, len(self.visited[0]) - 1):
                if not self.visited[i][j]:
                    count = count + 1
        return count

    def reacheable(self, row, col):
        result = []
        r = len(self.visited)
        c = len(self.visited[0])
        if row != 0 and col != c - 1 and self.datas[row-1][col] not in [2, 3] and not self.transfer_gate(row, col + 1, row, col):
                result.append((row, col+1))
        if row != 0 and col != 0 and self.datas[row-1][col-1] not in [1, 3] and not self.transfer_gate(row-1, col, row, col):
                result.append((row-1, col))
        if row != 0 and col != 0 and self.datas[row-1][col-1] not in [2, 3]and not self.transfer_gate(row, col-1, row, col):
                result.append((row, col-1))
        if col != 0 and row != r - 1 and self.datas[row][col-1] not in [1, 3] and not self.transfer_gate(row+1, col, row, col):
                result.append((row+1, col))
        return result

    def dfs_augment_graph(self, row, col):
        self.visited[row][col] = True
        candidates = self.reacheable(row, col)
        self.count_neighbors[row][col] = len(candidates)
        for c in candidates:
            if not self.visited[c[0]][c[1]]:
                self.dfs_augment_graph(c[0], c[1])

    def dfs_augment_graph_wrapper(self):
        self.visited = [[False for i in range(self.width + 1)] for i in range(self.height + 1)]
        self.block_edge_tile()
        connected_component = 0
        for gate in self.augment_graph_gates:
            if not self.visited[gate[0]][gate[1]]:
                connected_component = connected_component + 1
                self.dfs_augment_graph(gate[0], gate[1])
        inaccessible = self.inaccessible()
        return inaccessible, connected_component

    def have_next(self):
        for i in range(1, len(self.count_neighbors)-1):
            for j in range(1, len(self.count_neighbors[0])-1):
                if self.count_neighbors[i][j] == 1:
                    return True
        return False

    def next(self):
        for i in range(1, self.height):
            for j in range(1, self.width):
                if self.count_neighbors[i][j] == 1:
                    return i, j

    def dfs_cul_de_sacs(self, row, col):
        self.visited[row][col] = True
        self.cur_del_sec_set.append((row, col))
        candidates = self.reacheable(row, col)
        for c in candidates:
            if self.count_neighbors[c[0]][c[1]] < 0 and not self.visited[c[0]][c[1]]:
                self.dfs_cul_de_sacs(c[0], c[1])

    def find_cul_de_sacs(self):
        while self.have_next():
            row, col = self.next()
            neighbors = self.reacheable(row, col)
            self.count_neighbors[row][col] = -1
            for c in neighbors:
                self.count_neighbors[c[0]][c[1]] = self.count_neighbors[c[0]][c[1]] - 1
        self.visited = [[False for i in range(self.width + 1)] for i in range(self.height + 1)]
        count = 0
        for i in range(1, len(self.count_neighbors)-1):
            for j in range(1, len(self.count_neighbors[0])-1):
                if self.count_neighbors[i][j] < 0 and not self.visited[i][j]:
                    self.dfs_cul_de_sacs(i, j)
                    count = count + 1
        return count

    def dfs_find_path(self, row, col, path):
        self.visited[row][col] = True
        path.append((row, col))
        candidate = self.reacheable(row, col)
        for c in candidate:
            if not self.visited[c[0]][c[1]] and (c[0], c[1]) not in self.cur_del_sec_set\
                    and (self.count_neighbors[c[0]][c[1]] == 2 or (c[0], c[1]) in self.augment_graph_gates):
                self.dfs_find_path(c[0], c[1], path)

    def find_entry_exit_path(self):
        self.visited = [[False for i in range(self.width + 1)] for i in range(self.height + 1)]
        paths = 0
        for c in self.augment_graph_gates:
            if not self.visited[c[0]][c[1]]:
                path = []
                self.dfs_find_path(c[0], c[1], path)
                if path[0] in self.augment_graph_gates and path[-1] in self.augment_graph_gates and len(path) >= 2:
                    paths = paths + 1
                    self.entry_exit_path.append(path)
        return paths

    def _analyse(self):
        self.analysed = True
        gates = self.count_gates()
        walls = self.dfs_walls_wrapper()
        inaccessible_points, accessible_areas = self.dfs_augment_graph_wrapper()
        cul_de_sacs = self.find_cul_de_sacs()
        paths = self.find_entry_exit_path()
        return gates, walls, inaccessible_points, accessible_areas, cul_de_sacs, paths

    def analyse(self):
        gates, walls_connected, inaccessible_points, accessible_areas, cul_de_sacs, paths  = self._analyse()
        Maze.print_analyse_result(gates, walls_connected, inaccessible_points, accessible_areas, cul_de_sacs, paths)

    @staticmethod
    def print_analyse_result(gates, walls_connected, inaccessible_points, accessible_areas, cul_de_sacs, paths):
        if gates == 0:
            print("The maze has no gate.")
        elif gates == 1:
            print("The maze has a single gate.")
        else:
            print("The maze has " + str(gates) + " gates.")
        if walls_connected == 0:
            print("The maze has no wall.")
        elif walls_connected == 1:
            print("The maze has walls that are all connected.")
        else:
            print("The maze has " + str(walls_connected) + " sets of walls that are all connected.")
        if inaccessible_points == 0:
            print('The maze has no inaccessible inner point.')
        elif inaccessible_points == 1:
            print('The maze has a unique inaccessible inner point.')
        else:
            print('The maze has '+str(inaccessible_points)+' inaccessible inner points.')
        if accessible_areas == 0:
            print('The maze has no accessible area.')
        elif accessible_areas == 1:
            print('The maze has a unique accessible area.')
        else:
            print('The maze has ' + str(accessible_areas) + ' accessible areas.')
        if cul_de_sacs == 0:
            print('The maze has no accessible cul-de-sac.')
        elif cul_de_sacs == 1:
            print('The maze has accessible cul-de-sacs that are all connected.')
        else:
            print('The maze has ' + str(cul_de_sacs) + ' sets of accessible cul-de-sacs that are all connected.')
        if paths == 0:
            print('The maze has no entry-exit path with no intersection not to cul-de-sacs.')
        elif paths == 1:
            print('The maze has a unique entry-exit path with no intersection not to cul-de-sacs.')
        else:
            print('The maze has ' + str(paths)+ ' entry-exit paths with no intersections not to cul-de-sacs.')

    def on_path(self, startr, startc, endr, endc):
        for p in self.entry_exit_path:
            if (startr, startc) in p and (endr, endc) in p and\
                    math.fabs(p.index((startr, startc)) - p.index((endr, endc))) == 1:
                return True
        return False

    def display(self):
        if not self.analysed:
            self._analyse()
        file = open(self.filename+".tex", 'wt')
        file.write('\\documentclass[10pt]{article}\n')
        file.write('\\usepackage{tikz}\n')
        file.write('\\usetikzlibrary{shapes.misc}\n')
        file.write('\\usepackage[margin=0cm]{geometry}\n')
        file.write('\\pagestyle{empty}\n')
        file.write('\\tikzstyle{every node}=[cross out, draw, red]\n\n')
        file.write('\\begin{document}\n\n')
        file.write('\\vspace*{\\fill}\n')
        file.write('\\begin{center}\n')
        file.write('\\begin{tikzpicture}[x=0.5cm, y=-0.5cm, ultra thick, blue]\n')
        file.write('% Walls\n')

        for r in range(len(self.datas)):
            start = 0
            end = start
            while end < len(self.datas[0]) - 1:
                end = start
                while True:
                    connected = self.connected(r, end)
                    if (r, end + 1) not in connected:
                        break
                    end = end + 1
                if end != start:
                    file.write('    \\draw ('+str(start)+","+str(r)+") -- (" + str(end)+","+str(r)+");\n")
                start = end + 1
        for c in range(len(self.datas[0])):
            start = 0
            end = start
            while end < len(self.datas) - 1:
                end = start
                while True:
                    connected = self.connected(end, c)
                    if (end + 1, c) not in connected:
                        break
                    end = end + 1
                if end != start:
                    file.write('    \\draw ('+str(c)+","+str(start)+") -- (" + str(c)+","+str(end)+");\n")
                start = end + 1
        file.write('% Pillars\n')
        for i in range(len(self.datas)):
            for j in range(len(self.datas[0])):
                if len(self.connected(i, j)) == 0:
                    file.write('    \\fill[green] (' + str(j) + ',' + str(i) + ') circle(0.2);\n')
        file.write('% Inner points in accessible cul-de-sacs\n')
        for i in range(len(self.datas)):
            for j in range(len(self.datas[0])):
                if (i+1, j+1) in self.cur_del_sec_set:
                    file.write('    \\node at (' + str(j + 0.5) + ',' + str(i + 0.5) + ')')
                    file.write(' {};\n')
        file.write('% Entry-exit paths without intersections\n')
        for r in range(len(self.augment_graph)):
            start = 0
            end = start
            while end < len(self.augment_graph[0]) - 1:
                end = start
                while True:
                    if not self.on_path(r, end, r, end + 1):
                        break
                    end = end + 1
                if end != start:
                    file.write('    \\draw[dashed, yellow] (' + str(start - 0.5) + ',' + str(r - 0.5) + ')')
                    file.write(' -- (' + str(end - 0.5) + ',' + str(r - 0.5) + ');\n')
                start = end + 1
        for c in range(len(self.augment_graph[0])):
            start = 0
            end = start
            while end < len(self.augment_graph) - 1:
                end = start
                while True:
                    if not self.on_path(end, c, end + 1, c):
                        break
                    end = end + 1
                if end != start:
                    file.write('    \\draw[dashed, yellow] (' + str(c - 0.5) + ','+ str(start - 0.5) + ')')
                    file.write(' -- (' + str(c - 0.5) + ',' + str(end - 0.5) + ');\n')
                start = end + 1

        file.write('\\end{tikzpicture}\n')
        file.write('\\end{center}\n')
        file.write('\\vspace*{\\fill}\n')
        file.write('\n')
        file.write('\\end{document}\n')
        file.close()
