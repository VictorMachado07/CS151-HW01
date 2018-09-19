from typing import Set, Dict, Tuple, Optional, Sequence, List
import heapq
import math
import time
# This is how we write a type alias in Python
Map = List[List[str]]
# Now we can write load_map in terms of Map:
def load_map(mapfile:str) -> Map:
    with open(mapfile,encoding='utf-8') as infile:
        # This "list comprehension" is a very useful syntactic trick
        return [list(line.rstrip()) for line in infile]

Point = Tuple[int, int]

def get_value(c):
    switcher={
                '🌿':1,
                '🌼':2,
                '🌉':1,
                '🌲':1,
                '🌊':5
    }
    return switcher.get(c,"Invalid symbol")


# Now we can define our function in terms of Points
def find_neighbors(terrain:Map, p:Point) -> List[Tuple[Point, int]]:
    # Python has destructuring assignment.
    # You could just as well write `x = p[0]` and `y = p[1]`.
    # [((0,0),1),((0,1),1)]
    # terrain[y][x] -- row[y]  column[x]
    # Point (a,b)
    x, y = p
    neighbors : List[Tuple[Point,int]] = []
    if (y-1 >= 0):
        neighbors.append(((x,y-1),get_value(terrain[y-1][x])))
    if (x-1 >= 0):
        neighbors.append(((x-1,y),get_value(terrain[y][x-1])))
    if (x+1 < len(terrain[0])):
        neighbors.append(((x+1,y),get_value(terrain[y][x+1])))
    if (y+1 < len(terrain)):
        neighbors.append(((x,y+1),get_value(terrain[y+1][x])))

    # sorted(neighbors, key=lambda cost: cost[1])
    # A. Your code here...
    # Feel free to introduce other variables if they'd be helpful too.
    return sorted(neighbors, key=lambda cost: cost[1])

def pretty_print_path(terrain: Map, path: List[Point]):
    emojis = ['😀','😁','😂','🤣','😃','😄','😅','😆','😉','😊','😋']
    # This is a "dictionary comprehension" like the list comprehension above
    path2len = {location:distance for distance,location in enumerate(path)}
    output = []
    for yy,row in enumerate(terrain):
        row_str = ''
        for xx, cur in enumerate(row):
            if (xx,yy) in path2len:
                row_str += emojis[path2len[(xx,yy)] % len(emojis)]
            else:
                row_str += cur
        output.append(row_str)
    return '\\n'.join(output)


def print_search_result(terrain:Map, result:Tuple[int, int, Optional[List[Point]]]) -> None:
    print("Visited:",result[0])
    if result[2]:
        print("Best path cost:",result[1])
        print(pretty_print_path(terrain, result[2]))
    else:
        print("No path found")

terrain = load_map("terrain.txt")

def breadth_first(terrain:Map, start:Point, goal:Point) -> Tuple[int, int, Optional[List[Point]]]:
    open_list: List[Point] = [start]
    # We'll treat start specially
    best_costs: Dict[Point, Tuple[int, Point]] = {start:(0, start)}
    visit_count = 0
    while open_list:
        # Breadth-first search takes the first thing from the list...
        node = open_list.pop(0)
        visit_count += 1
        neighbors = find_neighbors(terrain, node)

        for neighbor, neighbor_cost in neighbors:
            # B. And does something with each neighbor node (where does the new node go in the list?)
            # Be sure to track the best cost and predecessor for each new node in `best_costs`
            # too, and avoid re-expanding nodes which we've seen before with better costs.
            # need to reopen nodes if this path is better than the path I had before
            # check neighbor isn't in best cost or neighbor is in best cost with worse cost
            # than what I have right now, so put it back in the queue
            # best_costs.get(neighbor, "false") == "false" is equivalent to neighbor not in best_costs
            if (neighbor not in best_costs
                or (best_costs[neighbor][0] > neighbor_cost + best_costs[node][0])):
                open_list.append(neighbor)
                cost2, node2 = best_costs.get(node)
                best_costs[neighbor] = (cost2+neighbor_cost, node)
            pass
        pass
    # C. If any path was found to goal, return the best such path.
    # Otherwise, return:
    # best_costs.get(goal, "false") != "false"
    if (goal in best_costs):
        print("here")
        cost, node = best_costs.get(goal)
        path: List[Point] = [goal]
        tempCost, tempNode = best_costs.get(goal)
        while(tempNode != start):
            path.append(tempNode)
            tempCost, tempNode = best_costs.get(tempNode)
        path.append(start)
        path.reverse()
        return (visit_count, cost, path)
    else:
        return (visit_count, -1, None)

def dijkstra(terrain:Map, start:Point, goal:Point) -> Tuple[int, int, Optional[List[Point]]]:
    open_list: List[Tuple[int, Point]] = [(0, start)]
    best_costs: Dict[Point, Tuple[int, Point]] = {start:(0, start)}
    visit_count = 0
    while open_list:
        # Dijkstra's search uses the priority queue data structure
        cost, node = heapq.heappop(open_list)
        visit_count += 1
        if (node == goal):
            break
        neighbors = find_neighbors(terrain, node)
        for neighbor, neighbor_cost in neighbors:
            # D. And does something with each neighbor node.
            # Hint: `heapq.heappush` may be useful here.
            # Be sure to track the best cost and predecessor for each new node in `best_costs` too!
            # best_costs.get(neighbor, "false") == "false"
            if (neighbor not in best_costs):
                heapq.heappush(open_list, (neighbor_cost + cost,neighbor))
                cost2, node2 = best_costs.get(node)
                best_costs[neighbor] = (cost2+neighbor_cost, node)
                # print(neighbor)
            # else:
            # if neighbor node exists in best cost
                # if neighbor_cost + cost < best_cost[neighbor]
                    #set best cost to new path
                    #push neighbor into queue
            pass
        pass
    if (best_costs.get(goal, "false") != "false"):
        cost, node = best_costs.get(goal)
        path: List[Point] = [goal]
        tempCost, tempNode = best_costs.get(goal)
        while(tempNode != start):
            path.append(tempNode)
            tempCost, tempNode = best_costs.get(tempNode)
        path.append(start)
        path.reverse()
        return (visit_count, cost, path)
    else:
        return (visit_count, -1, None)

def manhattan_distance(p1:Point, p2:Point) -> int:
    # E. Implement it here!  To calculate absolute value in Python, you can use abs(a-b).
    x,y = p1
    gx,gy = p2
    return (abs(gx-x)+abs(gy-y))

def best_first(terrain:Map, start:Point, goal:Point) -> Tuple[int, int, Optional[List[Point]]]:
    # In the open list we use heuristic values as the priority
    open_list: List[Tuple[int, Point]] = [(manhattan_distance(start, goal), start)]
    # But in best_costs we still want to track real costs
    best_costs: Dict[Point, Tuple[int, Point]] = {start:(0, start)}
    visit_count = 0
    while open_list:
        _h, node = heapq.heappop(open_list)
        visit_count += 1
        if (node == goal):
            break
        neighbors = find_neighbors(terrain, node)
        for neighbor, neighbor_cost in neighbors:
            # F. And best-first search also does something with each neighbor node.
            # Hint: `heapq.heappush` is still useful.
            # Be sure to track the best cost and predecessor for each new node in `best_costs`,
            # and use the heuristic value for this node to guide the search.
            nh = manhattan_distance(neighbor, goal)
            # Need to know the best cost to get to node
            # use that info to check if should be visiting that neighbor
            # do your priority based on nh
            # best_costs.get(neighbor, "false") == "false"
            if (neighbor not in best_costs or (best_costs[neighbor][0] > neighbor_cost + best_costs[node][0])):
                heapq.heappush(open_list, (nh,neighbor))
                cost2, node2 = best_costs.get(node)
                best_costs[neighbor] = (cost2+neighbor_cost, node)
            pass
        pass
    if (best_costs.get(goal, "false") != "false"):
        cost, node = best_costs.get(goal)
        path: List[Point] = [goal]
        tempCost, tempNode = best_costs.get(goal)
        while(tempNode != start):
            path.append(tempNode)
            tempCost, tempNode = best_costs.get(tempNode)
        path.append(start)
        path.reverse()
        return (visit_count, cost, path)
    else:
        return (visit_count, -1, None)

def astar(terrain:Map, start:Point, goal:Point) -> Tuple[int, int, Optional[List[Point]]]:
    # G. What do we use as priority values in the open list?
    open_list: List[Tuple[int, Point]] = [(manhattan_distance(start, goal) + 0, start)]
    # In best_costs we still want to track real costs
    best_costs: Dict[Point, Tuple[int, Point]] = {start:(0, start)}
    visit_count = 0
    while open_list:
        _h, node = heapq.heappop(open_list)
        visit_count += 1
        if (node == goal):
            break
        neighbors = find_neighbors(terrain, node)
        for neighbor, neighbor_cost in neighbors:
            # F. And A* also does something with each neighbor node.  You need to calculate both the heuristic value and the cost to get to this neighbor, and do something with the result.
            # Hint: `heapq.heappush` is still useful.
            # Be sure to track the best cost and predecessor for each new node in `best_costs`, and use your combined priority for this node to guide the search.
            # manhattan_distance(neighbor, goal)or (best_costs[neighbor][0] > neighbor_cost + best_costs[node][0])
            nh = manhattan_distance(neighbor, goal) + best_costs[node][0] + neighbor_cost
            if (neighbor not in best_costs):
                heapq.heappush(open_list, (nh,neighbor))
                cost2, node2 = best_costs.get(node)
                best_costs[neighbor] = (cost2+neighbor_cost, node)
            pass
        pass
    if (best_costs.get(goal, "false") != "false"):
        cost, node = best_costs.get(goal)
        path: List[Point] = [goal]
        tempCost, tempNode = best_costs.get(goal)
        while(tempNode != start):
            path.append(tempNode)
            tempCost, tempNode = best_costs.get(tempNode)
        path.append(start)
        path.reverse()
        return (visit_count, cost, path)
    else:
        return (visit_count, -1, None)
