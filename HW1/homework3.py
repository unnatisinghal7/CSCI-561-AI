from collections import deque
from math import sqrt
import sys
import heapq
import time

start_time = time.time()

# processing input file
f =  open('input.txt', 'r')
lines = f.readlines()
algo = lines[0].rstrip('\n')
dim = lines[1].rstrip('\n')
startingNode = lines[2].rstrip('\n')
endingNode = lines[3].rstrip('\n')
numOfNodes = int(lines[4].rstrip('\n'))
nodes = []
nodesDict = {}

#converting nodes to integer tuple dictionary
for i in range(numOfNodes):
    nodes.append(lines[5+i].rstrip('\n'))
    elements = nodes[i].split(' ')
    elements = [int(i) for i in elements]
    elementstuple = tuple(elements)
    nodesDict[elementstuple[0:3]] = elementstuple[3:]

f.close()

action = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1), (1,1,0), (1,-1,0), (-1,1,0), (-1,-1,0), (1,0,1), (1,0,-1), (-1,0,1), (-1,0,-1), (0,1,1), (0,1,-1), (0,-1,1), (0,-1,-1)]

def processNode(node):
    elements = node.split(' ')
    elements = [int(i) for i in elements]
    return tuple(elements)

startnode = processNode(startingNode)
endnode = processNode(endingNode)
dimensions = processNode(dim)

def isValid(node):
    return node[0]<dimensions[0] and node[1]<dimensions[1] and node[2]<dimensions[2] and node[0]>=0 and node[1]>=0 and node[2]>=0

def find_neighbors(node):
    neighbors = []
    for nextElement in nodesDict[node]:
        neighbors.append(tuple(map(lambda i, j: i + j, node, action[nextElement-1])))
    return neighbors

def callBFS():
    #initializing variables
    predecessor = {}
    visited = {}
    for key in nodesDict:
        visited[key] = False
    queue = deque()
    #to store distance from startnode
    distance = {}
    for key in nodesDict:
        distance[key] = sys.maxsize
        predecessor[key] = (-1,-1,-1)
        
    #starting the bfs
    queue.append(startnode)
    visited[startnode] = True
    distance[startnode] = 0

    while(len(queue) != 0):
        currElement = queue[0]
        queue.popleft()

        #finding the neighbors
        neighbors = find_neighbors(currElement)

        #traversing the neighbors
        for neighbor in neighbors:
            if isValid(neighbor) and visited[neighbor] == False:
                visited[neighbor] = True
                distance[neighbor] = distance[currElement] +1
                predecessor[neighbor] = currElement
                queue.append(neighbor)
                
                if neighbor == endnode:
                    return predecessor

    return 'FAIL'

def callUCS():
    #creating tuple of cost, id and parent
    startingnode = (0,)+startnode+startnode

    #we also have to initialize the cost of each node ie distance
    distanceDict={}
    
    visited = {}

    #initializing cost of startnode
    distanceDict[startnode] = startingnode
    queue = []
    heapq.heappush(queue, distanceDict[startnode])

    while(len(queue)>0):
        #pop the top element
        currElement = heapq.heappop(queue)

        if currElement in visited and visited[currElement][0] < currElement[0]:
            continue

        visited[currElement[1:4]] = currElement
        if currElement[1:4] == endnode:
            return distanceDict

        #finding the neighbors
        neighbors = []
        for nextElement in nodesDict[currElement[1:4]]:
            neighbors.append(tuple(map(lambda i, j: i + j, currElement[1:4], action[nextElement-1])))

        #tracking neighbor index from current element
        index =-1
        #traversing the neighbors
        for neighbor in neighbors:
            index+=1
            if isValid(neighbor) and neighbor not in visited:
                #get potential new distance from start to neighbor
                relativeDistance = 10 if nodesDict[currElement[1:4]][index]<7 else 14
                newDistance = currElement[0] + relativeDistance

                neighbor_node = (newDistance,)+neighbor+currElement[1:4]
                if (neighbor in distanceDict and distanceDict[neighbor][0] > newDistance) or \
                ((neighbor not in visited) and (neighbor not in distanceDict)):
                    distanceDict[neighbor]=neighbor_node
                    heapq.heappush(queue, neighbor_node)
                    distanceDict[neighbor] = neighbor_node

    return 'FAIL'

def heuristic(node1, node2):
    a = node1[0]-node2[0]
    b = node1[1]-node2[1]
    c = node1[2]-node2[2]
    return sqrt(a*a + b*b + c*c)

def callAStar():
    #creating tuple of cost=cost+parent_h, id, parent, action taken and parent_heuristic
    startingnode = (0,)+startnode+startnode+(0,)+(0,)

    queue = []  #work as open List
    visited = {}    #work as closed list with whole cost
    
    #taking distacneDict to store dictionary for the queue ie open list
    distanceDict = {}

    #initializing cost of startnode
    heapq.heappush(queue, startingnode)
    distanceDict[startnode] = startingnode

    while(len(queue)>0):
        #pop the top element
        currElement = heapq.heappop(queue)

        # remove already visited node with lower distance
        if currElement[1:4] in visited and visited[currElement[1:4]][0] < currElement[0]:
            if currElement[1:4] in distanceDict and distanceDict[currElement[1:4]][0] < currElement[0]:
                continue
        
        visited[currElement[1:4]] = currElement
        if currElement[1:4] == endnode:
            return visited
        
        neighbors = find_neighbors(currElement[1:4])

        #tracking neighbor index from current element
        index =-1
        #traversing the neighbors
        for neighbor in neighbors:
            index+=1
            if isValid(neighbor) and neighbor not in visited:
                #get potential new distance from start to neighbor
                relativeDistance = 10 if nodesDict[currElement[1:4]][index]<7 else 14
                newDistance = currElement[0] + relativeDistance - currElement[-1] + int(heuristic(endnode, neighbor))

                neighbor_node=(newDistance,)+neighbor+currElement[1:4]+(relativeDistance,)+(int(heuristic(endnode, neighbor)),)
                if (neighbor in distanceDict and distanceDict[neighbor][0] > newDistance) or \
                ((neighbor not in visited) and (neighbor not in distanceDict)):
                    heapq.heappush(queue,neighbor_node)
                    distanceDict[neighbor] = neighbor_node

    return 'FAIL'

if algo == 'BFS':
    result = callBFS()

    #output formatting
    f = open("output.txt", "w")
    if(result == 'FAIL'):
        f.write('FAIL')
    else:
        #traversing for the path from endnode
        path = []
        element = endnode
        while element!=startnode:
            path.append(element)
            element = result[element]
        path.append(startnode)
        path.reverse()

        f.write(str(len(path)-1)+'\n')
        f.write(str(len(path)))
        for element in range(len(path)):
            f.write('\n')
            temp=''
            for j in path[element]:
                temp+=str(j)+' '
            if element==0:
                temp+='0'
            else:
                temp+='1'
            f.write(temp)
    f.close()
    

if algo == 'UCS':
    result = callUCS()

    f = open("output.txt", "w")
    if result == 'FAIL':
        f.write('FAIL')
    else:
        #traversing for the path from endnode
        totalCost = result[endnode][0]
        path = []
        element = result[endnode][4:]
        elementTuple = endnode
        prevCost = totalCost
        while element!=startnode:
            elementCost = prevCost - result[element][0]
            path.append(elementTuple+(elementCost,))
            elementTuple = element
            prevCost = result[element][0]
            element = result[element][4:]
        elementCost = prevCost - result[element][0]
        path.append(elementTuple+(elementCost,))
        path.append(startnode + (0,))
        path.reverse()

        f.write(str(totalCost)+'\n')
        f.write(str(len(path)))
        for element in path:
            f.write('\n')
            item=''
            for i in element:
                item = item +str(i)+' '
            f.write(item[:-1])
    f.close()


if algo == 'A*':
    result = callAStar()

    f = open("output.txt", "w")
    if result == 'FAIL':
        f.write('FAIL')
    else:
        #traversing for the path from endnode
        totalCost = result[endnode][0]-result[endnode][-1]
        path = []
        element = endnode
        elementCost = result[element][-2]
        while element!=startnode:
            path.append(element+(elementCost,))
            element = result[element][4:7]
            elementCost = result[element][-2]
        path.append(element+(elementCost,))
        path.reverse()

        f.write(str(totalCost)+'\n')
        f.write(str(len(path)))
        for element in path:
            f.write('\n')
            item=''
            for i in element:
                item = item +str(i)+' '
            f.write(item[:-1])
    f.close()


print("seconds taken: ", time.time()-start_time)