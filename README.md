
# 4 In Row - Barak Daniel

## Project Documentation

### Overview

This project is a Python-based server-client application designed to facilitate a versatile gaming experience. It supports a classic game, enabling players to engage either against an AI opponent or another player in a 1v1 setting. The core of the project is split into two main components: `server.py` and `client.py`. The server handles game logic, client connections, match-making, and communication, while the client provides an interface for players to interact with the game server, send moves, and receive game updates.

### Prerequisites

To run this project, ensure you have the following prerequisites installed on your system:

- **Python 3.6 or higher**: The programming language used to develop this application. Available for download from [python.org](https://www.python.org/downloads/).
- **Network connectivity**: Both server and client components require network access to communicate. Ensure your firewall settings allow for the necessary connections.

### Setup Instructions

1. **Download the project files**: Clone or download the project repository to your local machine.

2. **Server setup**:
    - Navigate to the directory containing `server.py`.
    - Open a terminal or command prompt in this directory.
    - Run the server by executing the command: `python server.py`.
    - The server will start and listen for incoming client connections on the designated port (default is 1672 on localhost).

3. **Client setup**:
    - Ensure the server is running before starting a client.
    - Navigate to the directory containing `client.py`.
    - Open a separate terminal or command prompt window in this directory.
    - Start the client application by executing the command: `python client.py`.
    - Follow the on-screen prompts to choose a game mode and begin playing.

### Server Application Details

#### Main Functionalities

- **Multi-threaded client handling**: Utilizes the `threading` module to manage multiple client connections simultaneously, allowing for parallel games.
- **Game modes**: Supports different game modes, including playing against an AI or another player.
- **Dynamic game sessions**: Game sessions are dynamically created and managed, with support for "best of" series and difficulty levels for AI opponents.

#### Key Components

- `putInBoard`: Inserts a player's marker into the specified column of the game board if possible.
- `isBoardFull`: Checks if the game board is completely filled.
- `checkWin`: Evaluates the board to determine if there is a winning condition.
- `bestOf`: Handles the selection of a "best of" series for matches, including input validation and suspension handling for repeated invalid choices.
- `playRounds`: Manages the rounds of gameplay, including tracking scores, moves, and time.
- `handlePlayerMove` and `handleAiMove`: Functions to process player and AI moves, respectively.

#### Network Communication

- Utilizes the `socket` module for TCP/IP communication between the server and clients.
- The server listens on IP address `127.0.0.1` (localhost) and port `1672`.
- Messages between server and client are encoded and decoded using UTF-8 format.

### Client Application Overview

#### Functionality

- **Receives game updates**: Listens for messages from the server to display game status, board state, and results.
- **User input**: Sends player's moves and choices to the server based on game prompts.

#### Interaction Flow

- Upon connecting to the server, the client is prompted to choose a game mode.
- Depending on the selection, the client either enters a match against an AI, waits for a match against another player, or exits.

### Server Component Detailed Description

#### Core Functionalities

##### Game Initialization and Client Handling

- Starting the Server: The server is initialized by creating a socket object and binding it to a host and port. It then listens for incoming connections.

```python
ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1672
ServerSocket.bind((host, port))
ServerSocket.listen(5)
```

- Handling Multiple Clients: Utilizes threading to handle multiple clients simultaneously. Each client connection is handled by a separate thread to ensure that the server can manage multiple games concurrently.

```python
while True:
    Client, address = ServerSocket.accept()
    thread_player = threading.Thread(target=tClient, args=(Client, address))
    thread_player.start()
```

##### Game Modes and Match-making

- Game Mode Selection: Clients are prompted to choose a game mode upon connection. This choice determines whether they will play against the AI, another player, or quit.

```python
def chooseGameMode(connection):
    connection.send(str.encode('Choose a number..
1 - Quit
2 - Play against AI
3 - Play against another player'))
```

- 1v1 Match-making: When a client chooses to play against another player, they are added to a waiting list. Once two players are available, they are paired for a game.

```python
if len(waiting_list_1v1) >= 2:
    player1, player2 = waiting_list_1v1[0], waiting_list_1v1[1]
    play1V1(player1[0], player2[0])
```

#### Gameplay Logic

- Board Management: Includes functions for placing markers on the board, checking for a full board, and converting the board to a string for display.

```python
def putInBoard(board, col, player):
    # Attempts to place a marker and returns result and updated board
```

- Win Condition Checking: Utilizes a comprehensive method to check for horizontal, vertical, and diagonal win conditions.

```python
def checkWin(board):
    # Checks board and returns the winning player or "0" if no win
```

- Game Rounds and AI Logic: Manages the flow of game rounds, including player and AI moves, and determines the outcome of each round.

```python
def playRounds(connection, difficulty, winning_score):
    # Handles the playing of rounds until a winner is determined
```

### Network Communication

- Data Exchange: The server communicates with clients using TCP/IP sockets, sending and receiving encoded messages that represent game moves, choices, and updates.

```python
connection.send(message.encode(FORMAT))
```

### Client Component Detailed Description

#### Functionality

- Connecting to the Server: The client establishes a connection to the server using the specified host and port.

```python
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
port = 1672
client_socket.connect((host, port))
```

- Receiving Messages: Continuously listens for messages from the server, displaying them to the player and handling special commands like "GAME OVER".

```python
def receive_message():
    while True:
        msg = client_socket.recv(1024).decode('utf-8')
        print(msg)
```

- Sending Moves: Allows the player to input moves and sends them to the server. Special commands like "quit" are handled to cleanly exit the game.

```python
msg_to_send = input()
client_socket.send(msg_to_send.encode('utf-8'))
```
