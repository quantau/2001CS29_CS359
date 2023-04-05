import socket
import sys

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = sys.argv[1]
port = int(sys.argv[2])

try:
    c.connect((host, port)) # trying to connect to the server    
except socket.error as message:
    print("Socket Connection Error: " + str(message))
    exit(0)
else:
    print("Waiting for ack from server.")
    ack=c.recv(1024).decode()
    print("Connected to Server. Server sent " + ack + "\n")


while True:
    inp = input("Please enter the message to the server: ")
    c.send(inp.encode())

    answer = c.recv(1024)
    print("Server replied: " + answer.decode())
    inp = input("Do you wish to continue? Y/N\n")
    if (inp == "N"):
        break

c.close()
