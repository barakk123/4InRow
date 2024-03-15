# Barak Daniel 205436959

import threading
import socket
import os
import json
import random
import time
FORMAT = 'utf-8'

waiting_list_1v1 = []
suspension_multipliers = {}

def putInBoard(board, col, player):  # 0 for success, -1 if the column is full or invalid
    if 0 <= col <= 6:
        for row in range(len(board)-1, -1, -1):  # Start from the bottom row and go upwards
            if board[row][col] == "0":
                board[row][col] = player
                return 0, board  # Successfully placed the player's marker
        return -1, board  # The column is full
    else:
        return -1, board  # The chosen column is outside of the valid range


def isBoardFull(board): #return 1 if board is full
    full_board = True
    for i in range(6):
        for j in range(7):
            if board[i][j] == "0":
                full_board = False
    if full_board:
        return 1
    return 0

def boardToString(board):
    row_separator = "-" * 29 + "\n"  # Creates a row separator of dashes
    board_str = row_separator
    for row in board:
        # Creates a string for the current row with spaces and vertical bars
        row_str = "| " + " | ".join(row) + " |" + "\n"
        board_str += row_str + row_separator
    return board_str

def printBoard(board, connection):
    print(boardToString(board))
    connection.send(boardToString(board).encode(FORMAT))

def checkWinCon(board, start_row, start_col, delta_row, delta_col):
    """
    Checks if there's a winning condition starting from a specific cell and moving in a specified direction.
    """
    player = board[start_row][start_col]
    if player not in ["1", "2"]:  # If the starting cell is not occupied by a player, no need to check further.
        return False
    for step in range(1, 4):  # Check the next 3 cells in the specified direction.
        row = start_row + step * delta_row
        col = start_col + step * delta_col
        if board[row][col] != player:
            return False
    return player  # Returns the player number if a win is found.

def checkWin(board):
    # Check horizontal lines
    for i in range(6):
        for j in range(4):  # Only need to check starting from columns 0 to 3 for horizontal win
            result = checkWinCon(board, i, j, 0, 1)
            if result:
                return result

    # Check vertical lines
    for i in range(3):  # Only need to check starting from rows 0 to 2 for vertical win
        for j in range(7):
            result = checkWinCon(board, i, j, 1, 0)
            if result:
                return result

    # Check diagonal (down-right) lines
    for i in range(3):
        for j in range(4):
            result = checkWinCon(board, i, j, 1, 1)
            if result:
                return result

    # Check diagonal (up-right) lines
    for i in range(3, 6):
        for j in range(4):
            result = checkWinCon(board, i, j, -1, 1)
            if result:
                return result

    return "0"  # If no win condition is found, return "0".

def bestOf(connection):
    initial_prompt = (
        'Please choose the best of series for the match (odd numbers like 1, 3, 5, 7...).\n'
        'If you choose an inappropriate value 5 times in a row, you will be suspended for one minute.\n'
        'For each subsequent set of 5 inappropriate choices, the suspension time will double.\n'
    )
    connection.send(str.encode(initial_prompt))
    
    invalid_count = 0
    if connection not in suspension_multipliers:
        suspension_multipliers[connection] = 1
    
    while True:
        try:
            total_games = int(connection.recv(2048).decode(FORMAT))
            # Ensure the chosen number is odd and greater than 1
            if total_games >= 1 and total_games % 2 == 1:
                # Calculate wins required for a majority
                wins_required = (total_games // 2) + 1
                success_msg = f"You chose a best of {total_games} series. First to {wins_required} wins takes the match.\n"
                connection.send(success_msg.encode(FORMAT))
                return wins_required  # Return wins required to win the series
            else:
                raise ValueError
        except ValueError:
            invalid_count += 1
            handleInvalidChoice(invalid_count, connection)

def handleInvalidChoice(invalid_count, connection):
    # Ensure modifying the multiplier specific to this user
    if invalid_count % 5 == 0:
        suspension_time = 60 * suspension_multipliers[connection]
        suspension_msg = (
            f"Invalid choice made 5 times. You are suspended for {suspension_time} seconds. "
            "Wait for the suspension to end before trying again."
        )
        print(suspension_msg)
        connection.send(suspension_msg.encode(FORMAT))
        time.sleep(suspension_time)
        try_again_msg = "Suspension is over. You can try choosing again now:"
        connection.send(try_again_msg.encode(FORMAT))

        # Double the suspension time for the next round of invalid inputs
        suspension_multipliers[connection] *= 2

    else:
        retry_msg = "Invalid choice. Please choose an odd number for the best of series. Try again:"
        connection.send(retry_msg.encode(FORMAT))


#TCP PRIVATE COMMUNICATION ON PORT NUMBER 1672 WITH IP ADDRESS 127.0.0.1

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1672
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)

def chooseGameMode(connection):
    connection.send(str.encode('Choose a number..\n1 - Quit\n2 - Play against AI\n3 - Play against another player'))
    choice = connection.recv(2048).decode(FORMAT)
    return choice

def chooseDifficulty(connection):
    connection.send(str.encode('Choose a number..\n1 - EASY mode\n2 - HARD mode'))
    difficulty = connection.recv(2048).decode(FORMAT)
    return difficulty

def playRounds(connection, difficulty, winning_score):
    win_count_player = 0
    win_count_ai = 0
    total_moves_player = 0  # Total moves made by the player
    total_moves_ai = 0      # Total moves made by the AI
    total_time = 0          # Total time for all rounds
    total_moves_all = 0     # Total moves made by both players combined
    first_round = True  # Initialize first round flag
    while win_count_player < winning_score and win_count_ai < winning_score:
        board = [["0"] * 7 for _ in range(6)]
        print(f'ROUND NUMBER: {win_count_player + win_count_ai + 1} IS STARTING NOW')
        
        connection.send(f"\nROUND NUMBER: {win_count_player + win_count_ai + 1} IS STARTING NOW\nFor your convenience here is the empty starting board:\n".encode(FORMAT))
        printBoard(board, connection)
        
        # Play the round
        winner, round_moves_player, round_moves_ai, round_time = playSingleRound(connection, board, difficulty)
        total_time += round_time  # Accumulate round time to total time

        if winner == "1":
            win_count_player += 1
            total_moves_player += round_moves_player
            total_moves_ai += round_moves_ai
        elif winner == "2":
            win_count_ai += 1
            total_moves_ai += round_moves_ai
            total_moves_player += round_moves_player
        
        total_moves_all += round_moves_player + round_moves_ai  # Update total moves by both players combined
        
        # Send round summary to client
        sendRoundSummary(connection, win_count_player, win_count_ai, winner, round_moves_player, round_moves_ai, total_moves_player, total_moves_ai, round_time, first_round)
        first_round = False  # Update flag after the first round

    # Send total time after all rounds are over
    total_summary = f"Total time: {total_time} seconds\n"
    connection.send(total_summary.encode(FORMAT))
    return win_count_player, win_count_ai


def sendRoundSummary(connection, win_count_player, win_count_ai, winner, round_moves_player, round_moves_ai, total_moves_player, total_moves_ai, round_time, is_first_round):
    summary = f"Round Over\nYour wins: {win_count_player}\nAI wins: {win_count_ai}\n"
    if winner == "1":
        summary += f"You won this round in {round_moves_player} moves!\n"
    elif winner == "2":
        summary += f"AI won this round in {round_moves_ai} moves!\n"
    else:
        summary += "It's a draw!\n"
    summary += f"Total moves made in this round: {round_moves_player + round_moves_ai}\n"
    summary += f"Round time: {round_time} seconds\n\n"

    # Display total moves made by the winner and total moves made by both players combined
    if not is_first_round:
        total_moves_all = total_moves_player + total_moves_ai
        if win_count_player == win_count_ai:
            summary += f"Total moves made by both players: {total_moves_all}\n"
        else:
            summary += f"Total moves made by the winner: {total_moves_player}\n"
            summary += f"Total moves made by both players: {total_moves_all}\n"
    
    connection.send(summary.encode(FORMAT))





def handlePlayerMove(connection, board):
    valid_move = False
    while not valid_move:
        connection.send(str.encode('\nChoose a column between 0-6:'))
        try:
            chosen_column = int(connection.recv(2048).decode(FORMAT))
            if 0 <= chosen_column <= 6:
                result, updated_board = putInBoard(board, chosen_column, "1")
                if result == 0:
                    valid_move = True
                    printBoard(updated_board, connection)

                    return True  # Move was successful
                else:
                    connection.send(str.encode('Column full or invalid, please try again.\n'))
            else:
                connection.send(str.encode('Please choose a valid column between 0-6.\n'))
        except ValueError:
            connection.send(str.encode('Invalid input, please enter a number between 0-6.\n'))
    return False

def checkPotentialWin(board, player):
    # This function checks if the player can win in the next move, and returns the column if they can.
    for col in range(7):
        # Make a copy of the board to simulate the move
        board_copy = [row[:] for row in board]
        result, board_copy = putInBoard(board_copy, col, player)
        if result == 0 and checkWin(board_copy) == player:
            return col
    return None

def handleAiMove(board, difficulty, connection):
    if difficulty == "1":  # Easy mode: Random choice
        valid_move = False
        while not valid_move:
            chosen_column = random.randint(0, 6)
            result, updated_board = putInBoard(board, chosen_column, "2")
            if result == 0:
                valid_move = True
                connection.send(str.encode('AI move:\n'))
                printBoard(updated_board, connection)
    elif difficulty == "2":  # Hard mode
        valid_move = False
        while not valid_move:
            # Step 1: Check if AI can win in the next move
            ai_win_col = checkPotentialWin(board, "2")
            if ai_win_col is not None:
                chosen_column = ai_win_col
            
            # Step 2: Check if the opponent can win in their next move and block them
            elif checkPotentialWin(board, "1") is not None:
                chosen_column = checkPotentialWin(board, "1")
            
            # Step 3: Otherwise, prefer the center column if it's not already taken
            elif board[0][3] == "0":
                chosen_column = 3
            
            # Step 4: If none of the above, choose a random column
            else:
                chosen_column = random.randint(0, 6)
            
            # Attempt to make the chosen move
            result, updated_board = putInBoard(board, chosen_column, "2")
            if result == 0:
                valid_move = True
                connection.send(str.encode('AI move:\n'))
                printBoard(updated_board, connection)

def playSingleRound(connection, board, difficulty):
    round_moves_player = 0  # Track moves made by the player in this round
    round_moves_ai = 0      # Track moves made by the AI in this round
    round_start_time = time.time()  # Start time for this round

    round_finished = False
    while not round_finished:
        # Player's turn
        player_move_success = handlePlayerMove(connection, board)
        round_moves_player += 1  # Increment player moves for this round
        if player_move_success:
            if checkWin(board) == "1":
                round_finished = True  # Player wins
            elif isBoardFull(board):
                round_finished = True  # Board is full, check for a draw after AI's move

        # AI's turn, if round not finished
        if not round_finished:
            handleAiMove(board, difficulty, connection)
            round_moves_ai += 1  # Increment AI moves for this round
            if checkWin(board) == "2":
                round_finished = True  # AI wins
            elif isBoardFull(board):
                round_finished = True  # Board is full

    round_end_time = time.time()  # End time for this round
    round_time = round_end_time - round_start_time  # Calculate round time

    # If the board is full and no one won, it's a draw
    if isBoardFull(board):
        return "0", round_moves_player, round_moves_ai, round_time
    elif checkWin(board) == "1":
        return "1", round_moves_player, round_moves_ai, round_time  # Player wins
    elif checkWin(board) == "2":
        return "2", round_moves_player, round_moves_ai, round_time  # AI wins

def tClient(connection, address):
    try:
        choice = chooseGameMode(connection)
        if choice == "1" or choice == "quit" or choice == "Quit":
            print("Client chose to quit")
            connection.send(str.encode("Client chose to quit"))
        elif choice == "2":
            print("Client chose to play")
            difficulty = chooseDifficulty(connection)
            winning_score = bestOf(connection)
            win_count_player, win_count_ai = playRounds(connection, difficulty, winning_score)

            game_over_message = f"GAME OVER\nPlayer 1 has {win_count_player} wins\nPlayer 2 (AI) has {win_count_ai} wins\nGG\n"
            print("GAME OVER")
            connection.send(game_over_message.encode(FORMAT))

        elif choice == "3":
            global waiting_list_1v1
            waiting_list_1v1.append((connection, address))
            
            if len(waiting_list_1v1) >= 2:
                player1, player2 = waiting_list_1v1[0], waiting_list_1v1[1]
                waiting_list_1v1 = waiting_list_1v1[2:]
                play1V1(player1[0], player2[0])  
            else:
                connection.send(str.encode("Waiting for another player..."))
        else:
            connection.send(str.encode("Invalid input, closing connection\n"))
            connection.close()
    except (ConnectionResetError, socket.error) as e:
        print(f"Connection lost with {address}. Reason: {str(e)}")

def sendMessage(connection, message):
    connection.send(message.encode(FORMAT))
def play1V1(player1_conn, player2_conn):
    def sendBoard():
        board_str = boardToString(board_game)
        player1_conn.send(f"Your turn:\n{board_str}".encode(FORMAT))
        player2_conn.send(f"Opponent's turn:\n{board_str}".encode(FORMAT))

    def getPlayerMove(player_conn):
        player_conn.send('Your move (enter column number 0-6): '.encode(FORMAT))
        move = player_conn.recv(1024).decode(FORMAT).strip()
        return int(move)

    board_game = [["0"] * 7 for _ in range(6)]
    current_player, other_player = player1_conn, player2_conn
    player_turn = "1"
    game_over = False

    # Initialize metrics tracking
    start_time = time.time()
    moves_player1 = 0
    moves_player2 = 0

    while not game_over:
        sendBoard()
        try:
            player_move = getPlayerMove(current_player)
            result, _ = putInBoard(board_game, player_move, player_turn)
            if result == -1:
                current_player.send('Invalid move. Try again.\n'.encode(FORMAT))
                continue

            # Update moves count based on current player
            if player_turn == "1":
                moves_player1 += 1
            else:
                moves_player2 += 1

            if isBoardFull(board_game):
                game_over = True
                sendMessage(player1_conn, "Draw!")
                sendMessage(player2_conn, "Draw!")

            winner = checkWin(board_game)
            if winner != "0":
                game_over = True
                if winner == "1":
                    sendMessage(player1_conn, "Congratz! You Won!")
                    sendMessage(player2_conn, "You Lost.")
                else:
                    sendMessage(player1_conn, "You Lost.")
                    sendMessage(player2_conn, "Congratz! You Won!")

                # Calculate elapsed time
                end_time = time.time()
                elapsed_time = end_time - start_time
                
                # Send metrics to both players
                metrics_message = f"Game Over.\nPlayer 1 moves: {moves_player1}\nPlayer 2 moves: {moves_player2}\nElapsed time: {elapsed_time:.2f} seconds.\n"
                sendMessage(player1_conn, metrics_message)
                sendMessage(player2_conn, metrics_message)

                sendMessage(player1_conn, "Closing connection")
                sendMessage(player2_conn, "Closing connection")
                player1_conn.close()
                player2_conn.close()
                return

            # Switch player turns
            current_player, other_player = other_player, current_player
            player_turn = "2" if player_turn == "1" else "1"
        except ValueError:
            current_player.send("Invalid input. Please enter a number.\n".encode(FORMAT))

    player1_conn.close()
    player2_conn.close()


while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    thread_player = threading.Thread(target=tClient, args=(Client, address))
    if threading.active_count() > 5:
        Client.send("Can't have more than 5 players".encode(FORMAT))
        print(
            "Connection denied, can't have more than 5 players" + "| IP: " + str(address[0]) + "| port: " + str(
                address[1]))
        Client.close()
    else:
        print("Connection has been established" + "| IP: " + str(address[0]) + "| port: " + str(
            address[1]))
        print("Total number of connected players: ", threading.active_count())

        thread_player.start()
        
ServerSocket.close()