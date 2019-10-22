# Vaibhav Bafna (vbafna@umich.edu)
# 10/22/19
# Coda Maze 

# dependencies
import requests
import json
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from collections import deque


# helper function for retrying requests --> courtesy of https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def requests_retry_session(
        retries=5,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
    ):
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session


# used to represent navigation through the maze
class Point:
    # initialize points
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 0


class CodaMaze:

    # initialize maze
    def __init__(self):
        url = "https://maze.coda.io/maze"
        response = requests_retry_session().post(url=url, data={})
        response_dict = response.json()

        self.maze_id = response_dict['id']
        self.N = response_dict['height']
        self.visited_matrix = [[0 for x in range(self.N)] for y in range(self.N)]
        self.stack = []
        self.path = []

        coda_maze = [[0 for x in range(self.N)] for y in range(self.N)]
        
        for x in range(0, self.N):
            for y in range(0, self.N):
                if self.is_open_position(x, y):
                    coda_maze[x][y] = 1

        self.coda_maze = coda_maze
        print("Solving maze with id: {}".format(self.maze_id))


    # check to see if given position is valid or not
    def is_open_position(self, x, y):
        url = "https://maze.coda.io/maze/{}/check?x={}&y={}".format(self.maze_id, x ,y)
        response = requests_retry_session().get(url=url, params={})
            
        if response.status_code == 200:
            return True
        else:
            return False

    def print_maze(self): 
        print("Coda Maze:")
        for i in self.coda_maze: 
            for j in i: 
                print(str(j) + " ", end ="") 
            print("") 

    # main function to solve maze
    def is_coda_maze_solvable(self):
        x = 0
        y = 0

        point = Point(x, y)
        self.stack.append(point)
        self.path.append({"x": point.x, "y": point.y})

        while (self.stack):
            temp_point = self.stack[-1]
            x = temp_point.x
            y = temp_point.y
            direction = temp_point.direction

            temp_point.direction += 1
            self.stack.pop()
            self.stack.append(temp_point)

            self.path.pop()
            self.path.append({"x": x, "y": y})

            if (x == self.N - 1 and y == self.N - 1):
                return True

            # look up
            if (direction == 0):
                if (x - 1 >= 0 and self.coda_maze[x - 1][y] and self.visited_matrix[x - 1][y] == 0):
                    new_point = Point(x - 1, y)
                    self.visited_matrix[x - 1][y] = 1
                    self.stack.append(new_point)
                    self.path.append({"x": x - 1, "y": y})

            # look left
            elif (direction == 1):
                if (y - 1 >= 0 and self.coda_maze[x][y - 1] and self.visited_matrix[x][y - 1] == 0):
                    new_point = Point(x, y - 1)
                    self.visited_matrix[x][y - 1] = 1
                    self.stack.append(new_point)
                    self.path.append({"x": x, "y": y - 1})

            # look down
            elif (direction == 2):
                if (x + 1 < self.N and self.coda_maze[x + 1][y] and self.visited_matrix[x + 1][y] == 0):
                    new_point = Point(x + 1, y)
                    self.visited_matrix[x + 1][y] = 1
                    self.stack.append(new_point)
                    self.path.append({"x": x + 1, "y": y})

            # look right
            elif (direction == 3):
                if (y + 1 < self.N and self.coda_maze[x][y + 1] and self.visited_matrix[x][y + 1] == 0):
                    new_point = Point(x, y + 1)
                    self.visited_matrix[x][y + 1] = 1
                    self.stack.append(new_point)
                    self.path.append({"x": x, "y": y + 1})

            # if nowhere to go, unmark
            else:
                self.visited_matrix[new_point.x][new_point.y] = 0
                self.stack.pop()
                self.path.pop()

        return False

    
    # post solution to Coda's server
    def send_coda_solution(self):
        url = "https://maze.coda.io/maze/{}/solve".format(self.maze_id)
        response = requests_retry_session().post(url=url, data=json.dumps(self.path))
        print(response.text)


    # print solution
    def print_maze_solution(self):
        print("Ordered set of moves: {}".format(coda_maze.path))


# Note: I decided to print the maze as well as the solution response text
# just because I belive it's helpful information when running the program.
coda_maze = CodaMaze()
coda_maze.print_maze()
coda_maze.is_coda_maze_solvable()
coda_maze.send_coda_solution()
coda_maze.print_maze_solution()
