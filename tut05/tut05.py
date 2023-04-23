import threading
import time
import queue

# List of all Routers
RouterList = []

# Queue for for each router to get RoutingTables from neighbouring Routers
RouterQueue = {}

IOlock = threading.Lock()


def print_routing_table(CurrRouter, iteration_count, dictionary, UpdateList):
    # Find the maximum length of the keys and the values
    max_key_length = max(len(str(key)) for key in dictionary.keys())
    max_val_length_1 = max(len(str(val[0])) for val in dictionary.values())
    max_val_length_2 = max(len(str(val[1])) for val in dictionary.values())

    # Update the maximum lengths to account for the column headers
    max_key_length = max(len("Destination Router"), max_key_length)
    max_val_length_1 = max(len("Via Router"), max_val_length_1)
    max_val_length_2 = max(len("Distance"), max_val_length_2)

    # Iterate through the dictionary and convert values to strings
    for key, val in dictionary.items():
        val1, val2 = val
        val1 = str(val1)
        val2 = str(val2)

    # Acquire a lock to prevent multiple threads from printing at the same time
    IOlock.acquire()

    # Print the current router and iteration count
    print("Current Router:", CurrRouter,
          "| Current iteration:", iteration_count)

    # Calculate the width of the table
    spaced_line = max_key_length + max_val_length_1 + max_val_length_2 + 8

    # Print the table border
    print(f"+", "-"*(spaced_line), "+", sep="")

    # Print the table headers
    print(f"| {'Destination Router':<{max_key_length}} | {'Via Router':<{max_val_length_1}} | {'Distance':<{max_val_length_2}} |")
    print(f"|{'-'*(max_key_length+2)}|{'-'*(max_val_length_1+2)}|{'-'*(max_val_length_2+2)}|")

    # Print the rows of the table
    for key, value in dictionary.items():
        if key in UpdateList:
            # If the key is in the update list, add an asterisk to the value in the first column
            value = ("* " + value[0], value[1])
        print(
            f"| {key:<{max_key_length}} | {value[0]:<{max_val_length_1}} | {value[1]:<{max_val_length_2}} |")

    # Print the table border
    print(f"+", "-"*(spaced_line), "+", sep="")
    print("\n")

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
