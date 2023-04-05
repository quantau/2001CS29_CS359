import socket
import sys


# calculates the value of the expression provided
def GetResult(message):
    try:
        result = eval(message)
    except:
        error_message = "Please enter a valid integer operand."
        return error_message
    else:
        return result


# all the communication between 1 client and 1 server is performed in this function
def coomunication(connection,address):
    while True:
        try:
            data = connection.recv(1024)
        except KeyboardInterrupt:
            while True:
                inp=input(" You just used Ctrl+C, do you want to exit?\nEnter Y/N\n")
                if(inp=='Y'):
                    print("Bye!")
                    exit(0)
                elif(inp=='N'):
                    print("Aborted program exit.")
                    break
                else:
                    print("Oops! Invalid Input. Please try again.")
        else:
            if not data:
                break
            message = data.decode()
            result = GetResult(message)
            print(
                "Equation received ["
                + message
                + "] from "
                + address[0]
                + ":"
                + str(address[1])
            )
            output = str(result)
            connection.send(output.encode())
            print("Result sent to " + address[0] + ": " + str(address[1]))


def main():

    # creating socket
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as error_message:
        print("Socket Creation Error: " + str(error_message))
        exit(0)

    # binding socket
    try:
        print("Binding the Port: " + str(port))
        s.bind((host, port))
        s.listen(0)
    except socket.error as error_message:
        print("Socket Binding Error: " + str(error_message))
        exit(0)

    # server is listening to the clients
    while True:
        try:
            connection, address = s.accept()
        except KeyboardInterrupt:
            while True:
                inp=input(" You just used Ctrl+C, do you want to exit?\nEnter Y/N\n")
                if(inp=='Y'):
                    print("Bye!")
                    exit(0)
                elif(inp=='N'):
                    print("Aborted program exit.")
                    break
                else:
                    print("Oops! Invalid Input. Please try again.")
        else:
            connection.send("OK".encode())
            print("Connection has been established with " + address[0] + ": " + str(address[1]))
            coomunication(connection,address)
            connection.close()
            print("Connection has been closed with " + address[0] + ": " + str(address[1]))


if __name__ == "__main__":
    main()
