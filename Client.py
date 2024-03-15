# Barak Daniel 205436959

import threading
import socket
import time
import os
FORMAT = 'utf-8'

ClientSocket = socket.socket()
host = '127.0.0.1'
port = 1672

print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

def receive_message():
    while True:
        try:
            msg = ClientSocket.recv(1024).decode(FORMAT)
            if len(msg) != 0:
                print(msg)
            if "GAME OVER" in msg or "GG" in msg or msg == "Client chose to quit" or msg == "Invalid input, closing connection\n" or "can't have more than 5 players" in msg:
                # Notify the user
                print("Exiting the game.")
                # Close the socket from within the thread
                ClientSocket.close()
                # Exit the program
                exit(0)
        except Exception as e:
            print("An error occurred:", str(e))
            # In case of any exception, close the socket and exit
            ClientSocket.close()
            exit(1)

# Start the listening thread
thread = threading.Thread(target=receive_message)
thread.start()

while True:
    # Main thread handles user input
    try:
        msg2 = input()
        if msg2 == 'Quit' or msg2 == 'quit':
            ClientSocket.send('Quit'.encode(FORMAT))
            print("Exiting the game.")

            ClientSocket.close()
            exit(0)
        else:
            ClientSocket.send(msg2.encode(FORMAT))
    except EOFError:
        exit(0)

