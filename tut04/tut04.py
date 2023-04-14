import threading
import queue
import time 

# Queue for for each router to get RoutingTables from neighbouring Routers
RouterQueue={}

# List of all Routers
RouterList=[]

IOlock=threading.Lock()

 # Method to print the routing table of a router
def print_routing_table(CurrRouter,iteration_count,RoutingTable, UpdateList):
    # Acquire the lock before executing the code inside the method
    IOlock.acquire()

    # Define a string of dashes for use in the output formatting
    DASHES = "-" * 41
    # Define a string to represent the router and iteration count for use in the output formatting
    head_string = f"From Router: {CurrRouter} | Iteration Count: {iteration_count}"
    # Print a line of dashes to separate the output
    print(DASHES)
    # Print the header string for this router and iteration count, with proper spacing and alignment
    print(f"| {head_string:<37} |")
    # Print another line of dashes to separate the output
    print(DASHES)
    # Print the table headers for the routing table output
    print("| To Router  | Cost       | Via Router  |")
    print(DASHES)

    # Iterate through each element of the routing table
    for key in RoutingTable:
        # Extract the destination router ID from the element
        to_router = key
        # If the destination router is in the set of recently changed routers, prepend a "*" to the output
        if key in UpdateList:
            to_router = "* " + to_router
        # Otherwise, prepend a space to the output
        else:
            to_router = "  " + to_router
        # Print the routing table entry, with proper spacing and alignment
        print(f"| {to_router:<10} |"
                + f" {RoutingTable[key][1] :<10} |"
                + f" {(RoutingTable[key][0]):<11} |")

    # Print another line of dashes to separate the output
    print(DASHES, end="\n\n")
    # Release the lock
    IOlock.release()

# Function to read the topology from a file
def ReadTopology(graph,WeightMap):
    global RouterList
    # Open the file in read mode
    fd = open('topology.txt', 'r')

    # reading the number of routers
    RouterCount = int(fd.readline())

    # reading the list of routers
    RouterList = fd.readline().split()

    # initializing the adjacency list and the Queues
    for router in RouterList:
        graph[router]=[]
        WeightMap[router]={}
        RouterQueue[router]=queue.Queue()

    # reading the edges
    while True:
        linedata=fd.readline()
        if linedata == 'EOF':
            break
        edge = linedata.split()
        # constructing the adjacency list
        graph[edge[0]].append(edge[1]) 
        graph[edge[1]].append(edge[0]) 
        # constructing weight map
        WeightMap[edge[0]][edge[1]]=int(edge[2])
        WeightMap[edge[1]][edge[0]]=int(edge[2])

# Function to process routing for a single router in a separate thread
def router_thread(CurrRouter, NeighbourList, NeighbourWeights, RouterList):

    # Initialize the routing table
    RoutingTable = {}
    for router in RouterList:
        RoutingTable[router] = (CurrRouter, 1000) # (next_hop_router, distance)
    for router in NeighbourWeights:
        distance = NeighbourWeights[router]
        RoutingTable[router] = (router, distance)
    RoutingTable[CurrRouter] = (CurrRouter, 0) # Set distance to self to 0
    
    # list which will have destination nodes that have been updated in the current iteration
    UpdateList = []

    RouterCount = len(RouterList)
    for i in range(RouterCount - 1):

        # Process all the updates that the neighbouring routers sent
        while not RouterQueue[CurrRouter].empty():
            NeighbourRoutingTable, child_router = RouterQueue[CurrRouter].get()
            for dst_router in NeighbourRoutingTable:
                distance = NeighbourRoutingTable[dst_router][1] + NeighbourWeights[child_router]
                if RoutingTable[dst_router][1] > distance: #checking if the we can reduce the path distance                   
                    UpdateList.append(dst_router)
                    RoutingTable[dst_router] = (child_router, distance)#reduced path distance

        # Print routing table
        print_routing_table(CurrRouter, i, RoutingTable, UpdateList)

        # resetting UpdateList for the next iteration
        UpdateList.clear()

        # Send updates to neighbouring routers
        for router in NeighbourList:
            RouterQueue[router].put((RoutingTable, CurrRouter))

        time.sleep(2) # Wait for 2 seconds between updates



# defining the main function
def main():
    # creating empty dictionaries for graph and weight map
    graph={}
    WeightMap={}

    # parsing the input from topology.txt
    ReadTopology(graph,WeightMap)

    # getting the number of routers
    RouterCount=len(RouterList)

    # printing the structures established
    print("Following is the graph: ",graph)
    print("Following is the weightMap: ",WeightMap)
    print("Following is the list of Routers: ",RouterList)
        
    # creating a list to hold threads for each router 
    threadList=[]
    for i in range(RouterCount):
        # creating thread for each router and adding it to threadList
        threadList.append(threading.Thread(target=router_thread,args=(RouterList[i],graph[RouterList[i]],WeightMap[RouterList[i]],RouterList)))
        # starting the thread
        threadList[i].start()

    # joining the threads 
    for i in range(RouterCount):
        threadList[i].join()

# checking if the script is being run directly and calling the main function
if __name__ == "__main__":
    main()



