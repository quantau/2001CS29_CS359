import threading
import time
import queue

# List of all Routers
RouterList = []

# Queue for for each router to get RoutingTables from neighbouring Routers
RouterQueue = {}

IOlock = threading.Lock()

# Method to print the routing table of a router
def print_routing_table(CurrRouter, iteration_count, RoutingTable, UpdateList):
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


def print_tuple_list_in_box(data_list, head1, head2):
    # Determine the maximum width of the data in each column
    max_width_col1 = len(max([str(x[0])
                         for x in data_list] + [head1], key=len))
    max_width_col2 = len(max([str(x[1])
                         for x in data_list] + [head2], key=len))

    # Determine the total width of the box
    total_width = max_width_col1 + max_width_col2 + 7

    # Print the top of the box
    print("+", "-" * (total_width-2), "+", sep="")

    # Print the headers
    print("|", head1.center(max_width_col1+2), "|",
          head2.center(max_width_col2+2), "|", sep="")

    # Print a line to separate the headers from the data
    print("|", "-" * (max_width_col1+2), "|",
          "-" * (max_width_col2+2), "|", sep="")

    # Print the data rows
    for item in data_list:
        print("|", str(item[0]).ljust(max_width_col1+2), "|",
              str(item[1]).ljust(max_width_col2+2), "|", sep="")

    # Print the bottom of the box
    print("+", "-" * (total_width-2), "+", sep="")




# Function to read the topology from a file
def ReadTopology(graph):
    global RouterList
    # Open the file in read mode
    fd = open('topology.txt', 'r')

    # reading the number of routers
    RouterCount = int(fd.readline())

    # reading the list of routers
    RouterList = fd.readline().split()

    # initializing the adjacency list and the Queues
    for router in RouterList:
        graph[router] = []
        RouterQueue[router] = queue.Queue()

    # reading the edges
    while True:
        linedata = fd.readline()
        if linedata == 'EOF':
            break
        edge = linedata.split()
        # constructing the adjacency list
        graph[edge[0]].append((edge[1], int(edge[2])))
        graph[edge[1]].append((edge[0], int(edge[2])))
      

# Function to process routing for a single router in a separate thread
def router_thread(CurrRouter, Mygraph, RouterList):
    # Create a dictionary with the current router as the key and the graph as the value
    graph = {}
    graph[CurrRouter] = Mygraph

    # Continuously update the router queue every 2 seconds
    while True:
        # Iterate through each router and add its data to the router queue
        for router, router_distance in Mygraph:
            RouterQueue[router].put((CurrRouter, graph))

        time.sleep(2)

        # Process the data in the router queue
        NewData = False
        while not RouterQueue[CurrRouter].empty():
            NeighbourRouter, NeighbourGraph = RouterQueue[CurrRouter].get()
            # Iterate through each destination router in the neighbor's graph
            for dst_router in NeighbourGraph:
                # If the destination router is not in the current router's graph, add it
                if dst_router not in graph:
                    NewData = True
                    graph[dst_router] = NeighbourGraph[dst_router]

        # If there's no new data, break out of the loop
        if not NewData:
            break

    # Create an empty routing table
    RoutingTable = {}

    # Iterate through each router in the network and set its default distance to 1000
    for Router in RouterList:
        RoutingTable[Router] = (CurrRouter,1000)

    # Iterate through each neighbor router and update its distance and path in the routing table
    VisitedList = []
    for NeighbourRouter, EdgeWeight in graph[CurrRouter]:
        RoutingTable[NeighbourRouter] = (NeighbourRouter, EdgeWeight)

    # Set the current router's distance to 0 in the routing table
    RoutingTable[CurrRouter] = (CurrRouter,0)

    # Lock the input/output to avoid conflicting messages
    IOlock.acquire()
    print("The Routing Table of ", CurrRouter, " is :")
    IOlock.release()

    # Print the current router's routing table
    print_routing_table(CurrRouter, len(VisitedList), RoutingTable, [])

    # Iterate through each router in the network and update its distance and path in the routing table
    while len(VisitedList) < len(RouterList):
        UpdateList = []
        MinDistanceRouter = 0
        MinDistance = 1000
        for Router in RoutingTable:
            # If the router has already been visited, skip it
            if Router in VisitedList:
                continue
            # If the router's distance is less than the current minimum, update the minimum
            if RoutingTable[Router][1] < MinDistance:
                MinDistanceRouter = Router
                MinDistance = RoutingTable[Router][1]

        # Add the router to the visited list
        VisitedList.append(MinDistanceRouter)
 
        # Iterate through each neighbor router and update its distance and path if it's shorter than the current value
        try:
            for NeighbourRouter, EdgeWeight in graph[MinDistanceRouter]:
                CurrDistance = MinDistance+EdgeWeight
                if CurrDistance < RoutingTable[NeighbourRouter][1]:
                    UpdateList.append(NeighbourRouter)
                    RoutingTable[NeighbourRouter] = (MinDistanceRouter, CurrDistance)
        except:
            print("The key error is in",CurrRouter," where ",MinDistanceRouter," key was attempted to be access.")
            print("Following is the graph:", graph)
        else:
            # Lock the input/output to avoid conflicting messages
            print_routing_table(CurrRouter,len(VisitedList),RoutingTable,UpdateList)
    return


# defining the main function
def main():
    # creating empty dictionaries for graph and weight map
    graph = {}

    # parsing the input from topology.txt
    ReadTopology(graph)

    # getting the number of routers
    RouterCount = len(RouterList)

    # printing the structures established
    # print("Following is the graph: ", graph)
    for node in graph:
        print("The edges of",node ,"are:")
        print_tuple_list_in_box(graph[node], 'destination', 'distance')
    print("Following is the list of Routers: ", RouterList)

    # creating a list to hold threads for each router
    threadList = []
    for i in range(RouterCount):
        # creating thread for each router and adding it to threadList
        threadList.append(threading.Thread(target=router_thread, args=(
            RouterList[i], graph[RouterList[i]],  RouterList)))
        # starting the thread
        threadList[i].start()

    # joining the threads
    for i in range(RouterCount):
        threadList[i].join()


# checking if the script is being run directly and calling the main function
if __name__ == "__main__":
    main()
