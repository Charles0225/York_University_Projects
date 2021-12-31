from queue import PriorityQueue, Queue
import sys

# open the input map
file = open(sys.argv[2],'r')
# create a dictionary to store the whole graph
map = {}
# create a dictionary to store the distance of each edge
distances = {}
# create a dictionary to store heuristic value of each location
heuristics = {}
# store every edge in map{}
for line in file:
    if line[:3] == "END":
        break
    else:
        line = line[:-1]
        edge = (line.split(' '))
        # add location1 as key
        if edge[0] not in map:
            map[edge[0]] = [(edge[1])]
        else:
            map[edge[0]].append(edge[1])
        # add location2 as key
        if edge[1] not in map:
            map[edge[1]] = [(edge[0])]
        else:
            map[edge[1]].append(edge[0])

        # store the distance of each edge in distances{}
        distances[tuple([edge[0], edge[1]])] = edge[2]
# close the input map
file.close()

# process the heuristic file
# if the command line argument has six or more argument, then the [5] argument is heuristic file
# store the heuristic file in heuristics{}
if len(sys.argv) > 5:
    file2 = open(sys.argv[5],'r')
    for line in file2:
        if line[:3] == "END":
            break
        else:
            line = line[:-1]
            cost = (line.split(' '))
            heuristics[cost[0]] = cost[1]
    file2.close()

# implement get distance function between two locations, order of two arguments doesn't matter
def get_distance(from_, to_):
    if (from_, to_) in distances:
        return distances[(from_, to_)]
    elif (to_, from_) in distances:
        return distances[(to_, from_)]
    else:
        print("no path between "+from_+" and "+to_)
        return 0

# implement print path function
def print_path(solution):
    # if origin is destination, print it
    if len(solution) == 1:
        print("distance: 0 mi")
        print("path:")
        print("origin is destination")
    # if origin is not destination, print the distance and path
    else:
        distance = 0
        # print the total distance
        for i in range(len(solution)-1):
            distance += int(get_distance(solution[i], solution[i+1]))
        print("distance: "+str(distance)+" mi")
        # print each path and its distance
        print("path:")
        for i in range(len(solution)-1):
            print(solution[i]+" to "+solution[i+1]+": "+get_distance(solution[i], solution[i+1])+" mi")
    
# implement each of the four algorithm

# create a queue used for bfs
frontier = Queue()
# create a PriorityQueue used for ucs and astar
q = PriorityQueue()
# create a stack used for dfs
stack = []
# create a list used to store the visited node
reached = []

# implement bfs
def bfs(origin, destination):
    # put origin into frontier
    frontier.put([origin])

    # while frontier is not empty
    while not frontier.empty():
        # pop the last path from frontier
        path = frontier.get()
        # get the tail node from the path
        parent = path[-1]

        # if the node hasn't been visited, put it in visited list, and tranverse its child
        if parent not in reached:
            reached.append(parent)
            # if the node is goal, return the path
            if parent == destination:
                    return path
            # tranverse all its child nodes which has not been visited, and put the paths into the frontier
            for child in map[parent]:           
                if child not in reached:
                    next_path = list(path)
                    next_path.append(child)
                    frontier.put(next_path)

def dfs(origin, destination):
    # append origin to stack
    stack.append([origin])

    # while stack is not empty
    while stack:
        # pop the last path from stack
        path = stack.pop()
        # get the tail node from the path
        parent = path[-1]

        # if the node hasn't been visited, put it in visited list, and tranverse its child
        if parent not in reached:
            reached.append(parent)
            # if the node is goal, return the path
            if parent == destination:
                    return path
            # tranverse all its child nodes which has not been visited, and append the paths to the stack
            for child in map[parent]:          
                if child not in reached:
                    next_path = list(path)
                    next_path.append(child)               
                    stack.append(next_path)
        
def ucs(origin, destination):
    # put origin into priority queue
    q.put((0,[origin]))

    # while queue is not empty
    while not q.empty():
        # pop the path and its distance with the shortest distance from priority queue
        distance, path = q.get()
        # get the tail node from the path
        parent = path[-1]

        # if the node hasn't been visited, put it in visited list, and tranverse its child
        if parent not in reached:
            reached.append(parent)
            # if the node is goal, return the path
            if parent == destination:
                    return path
            # tranverse all its child nodes which has not been visited, 
            # and put the paths and their cumulative distance into the priority queue
            for child in map[parent]:          
                if child not in reached:
                    next_path = list(path)
                    next_path.append(child)              
                    cumulative_distance = distance + int(get_distance(parent, child))
                    q.put((cumulative_distance, next_path))

def a_star(origin, destination):
    # put origin into priority queue
    q.put((0,[origin]))
    
    # while queue is not empty
    while not q.empty():
        # pop the path and its astar cost with the shortest astar cost from priority queue
        distance, path = q.get()
        # get the tail node from the path
        parent = path[-1]

        # if the node hasn't been visited, put it in visited list, and tranverse its child
        if parent not in reached:
            reached.append(parent)
            # if the path is not origin, then get rid of its own heuristics from its astar cost
            # the remaining is just the cumulative cost of this path
            if len(path) > 1:
                distance = distance - int(heuristics[parent])
            # if the node is goal, return the path
            if parent == destination:
                return path
            # tranverse all its child nodes which has not been visited, 
            # and put the paths and their (cumulative distance + heuristic of the last node) into the priority queue
            for child in map[parent]:          
                if child not in reached:
                    next_path = list(path)
                    next_path.append(child)
                    cumulative_distance = distance + int(get_distance(parent, child))
                    heuristic = int(heuristics[child])
                    cost = cumulative_distance + heuristic
                    q.put((cost, next_path))

# an int to identify whether the input algorithm is avaliable
valid_algorithm = 0

# if number of arguments smaller than 5, print error
if len(sys.argv) < 5:
    print("wrong number of argument")
else:
    # if origin and destination both in map, run the algorithm
    if sys.argv[3] in map and sys.argv[4] in map:
        # call one of the four algorithms according to command line argument
        if sys.argv[1] == "ucs":
            solution = ucs(sys.argv[3],sys.argv[4]) 
            valid_algorithm = 1
        elif sys.argv[1] == "bfs":    
            solution = bfs(sys.argv[3],sys.argv[4])  
            valid_algorithm = 1 
        elif sys.argv[1] == "dfs":
            solution = dfs(sys.argv[3],sys.argv[4])
            valid_algorithm = 1   
        elif sys.argv[1] == "astar":
            solution = a_star(sys.argv[3],sys.argv[4])
            valid_algorithm = 1

        # if input is ucs or bfs or dfs or astar
        if valid_algorithm == 1:
            # if there is a solution, call the print_path function with solution, 
            # otherwise, the destination cannot be reached from origin
            if solution:
                print_path(solution)
            else:
                print("distance: infinity")
                print("path:")
                print("none")
        # if input is not ucs or bfs or dfs or astar, print "unsupported search algorithm"  
        else:
            print("unsupported search algorithm")
    # if origin or destination is not in map, print error
    else:
        if sys.argv[3] not in map:
            print("Point of origin not in map")
        if sys.argv[4] not in map:
            print("Point of destination not in map")