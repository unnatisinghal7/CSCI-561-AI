from copy import deepcopy
import math
import time
import random

#max changes from here
#50+ submission 15,12,8,6,16, 18, 24(best)

size = 5
player_piece =0

#from host.py
def readInput(path="input.txt"):
    with open(path, 'r') as f:
        lines = f.readlines()

        piece_type = int(lines[0])

        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:size+1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[size+1: 2*size+1]]

        return piece_type, previous_board, board

#from host.py
def write_output(action):
    f = open("output.txt", 'w')
    if action == "PASS":
        f.write("PASS")
    else:
        f.write(str(action[0])+','+str(action[1]))
    f.close()

#from host.py
def detect_neighbor(board, i, j):
    neighbors = []
    # Detect borders and add neighbor coordinates
    if i > 0: neighbors.append((i-1, j))
    if i < len(board) - 1: neighbors.append((i+1, j))
    if j > 0: neighbors.append((i, j-1))
    if j < len(board) - 1: neighbors.append((i, j+1))
    return neighbors

#from host.py
def detect_neighbor_ally(board, i, j):
    neighbors = detect_neighbor(board, i, j)  # Detect neighbors
    group_allies = []
    # Iterate through neighbors
    for piece in neighbors:
        # Add to allies list if having the same color
        if board[piece[0]][piece[1]] == board[i][j]:
            group_allies.append(piece)
    return group_allies

#from host.py
def ally_dfs(board, i, j):
    stack = [(i, j)]  # stack for DFS search
    ally_members = []  # record allies positions during the search
    while stack:
        piece = stack.pop()
        ally_members.append(piece)
        neighbor_allies = detect_neighbor_ally(board, piece[0], piece[1])
        for ally in neighbor_allies:
            if ally not in stack and ally not in ally_members:
                stack.append(ally)
    return ally_members

#from host.py
def find_liberty_positions(board, i, j):
    # have to implement set so that we do not count liberty for an element twice
    liberty_places = set()
    ally_members = ally_dfs(board, i, j)
    for member in ally_members:
        neighbors = detect_neighbor(board, member[0], member[1])
        for piece in neighbors:
            # If there is empty space around a piece, it has liberty
            if board[piece[0]][piece[1]] == 0:
                liberty_places.add((piece[0], piece[1]))

    # If none of the pieces in a allied group has an empty space, it has no liberty
    return liberty_places

#from host.py
def find_died_pieces(board, piece_type):
    died_pieces = []

    for i in range(len(board)):
        for j in range(len(board)):
            # Check if there is a piece at this position:
            if board[i][j] == piece_type:
                # The piece die if it has no liberty
                if len(find_liberty_positions(board, i, j)) == 0:
                    died_pieces.append((i,j))
    return died_pieces

def find_new_board(board, i, j, piece_type):
    new_board = deepcopy(board)
    new_board[i][j] = piece_type

    my_dead_pieces = find_died_pieces(new_board, piece_type)
    for piece in my_dead_pieces:
        new_board[piece[0]][piece[1]] = 0
    opponent_dead_pieces = find_died_pieces(new_board, 3-piece_type)
    for piece in opponent_dead_pieces:
        new_board[piece[0]][piece[1]] = 0

    num_my_dead = len(my_dead_pieces)
    num_oppo_dead = len(opponent_dead_pieces)
    return new_board, num_my_dead, num_oppo_dead

def find_valid_moves(piece_type, board, previous_board):
    #we'll currently create a heuristic which is to find coins that are the near cluster of coins
    #remove moves seeing the dead coins
    # result = [] 
    result = set()
    for i in range(size):
        for j in range(size):
            if board[i][j] != 0:
                allies = find_liberty_positions(board, i, j)
                result = result.union(allies)
    safe_moves = []
    for move in result:
        new_board, my_dead_pieces, opponent_dead_pieces = find_new_board(board, move[0], move[1], piece_type)
        if new_board != previous_board and new_board != board:
            safe_moves.append((move, opponent_dead_pieces-my_dead_pieces))

    final_moves = []
    if len(safe_moves)>0:
        safe_moves = sorted(safe_moves, key=lambda x: -x[1])
        for element in safe_moves:
            final_moves.append(element[0])
            
    return final_moves

def heuristic(board, piece_type):
    komi = size/2
    my_coins =0
    opponent_coins = 0
    my_liberty = 0
    opponent_liberty = 0
    my_single_liberty = 0
    opponent_single_liberty = 0
    my_odd_moves = 0
    opponent_odd_moves = 0

    if piece_type == 1:
        opponent_coins +=6
    else:
        my_coins += 6

    for i in range(size):
        for j in range(size):
            if board[i][j] == piece_type:
                if (i+j)%2 != 0:
                    my_odd_moves += 1
                my_coins += 1
                liberty = len(find_liberty_positions(board, i, j))
                my_liberty += liberty
                if liberty <= 1:
                    my_single_liberty += 1
            elif board[i][j] == 3-piece_type:
                if (i+j)%2 != 0:
                    opponent_odd_moves += 1
                opponent_coins += 1
                liberty = len(find_liberty_positions(board, i, j))
                opponent_liberty += liberty
                if liberty <= 1:
                    opponent_single_liberty += 1

    if piece_type == 1: #black
        return 10*(my_coins) - 10*(opponent_coins) \
            + 8.5*my_liberty - 8.5*opponent_liberty \
                +my_odd_moves \
            + 2*opponent_single_liberty - 1.5*my_single_liberty
    else:
        return 10*(my_coins) - 10*(opponent_coins) \
            + 2*opponent_single_liberty - 1.5*my_single_liberty

def count_coins(board, piece_type):
    count = 0
    for i in range(size):
        for j in range(size):
            if(board[i][j]==piece_type):
                count+=1
    return count

def minimax(piece_type, board, previous_board, isMaximizing, alpha, beta, depth):
    
    #here i'll initialize alpha beta values and and do the computation
    if depth == 0:
        return heuristic(board, piece_type), []

    my_coins = count_coins(board, piece_type)
    opponent_coins = count_coins(board, 3-piece_type)

    if my_coins == 0 and opponent_coins == 0:
        return math.inf, [(2,2)]
    elif my_coins == 0 and opponent_coins == 1:
        if board[2][2] == 3-piece_type:
            return math.inf, [(2,1)]
        else:
            return math.inf, [(2,2)]

    if isMaximizing:
        # print("-------------------------Inside Maxximizer-------------------------")
        best = -math.inf
        best_action = []
        for move in find_valid_moves(piece_type, board, previous_board):
            # print(" max move: ", move)
            var = 1
            temp_board = deepcopy(board)
            new_board, my_dead, opponent_dead = find_new_board(temp_board, move[0], move[1], piece_type)
            eval_value, action = minimax(3-piece_type, new_board, board, False, alpha, beta, depth-1)

            eval_value += 5*opponent_dead - 8.5*my_dead
            # print("MAX_ eval: ", eval_value, "  action: ", action, "  move: ", move, " maxx: ", best," best_action: ", best_action)
            
            if eval_value > best:
                best_action = [move] + action
                best = eval_value
                var =2
            if best >= beta:
                var +=1
                return best, best_action
            if best > alpha:
                alpha = best
            
        return best, best_action

    if not isMaximizing:
        # print("-------------------------Inside Minimizer-------------------------")
        best = math.inf
        best_action = []
        for move in find_valid_moves(piece_type, board, previous_board):
            var=1
            temp_board = deepcopy(board)
            new_board, my_dead, opponent_dead  = find_new_board(temp_board, move[0], move[1], piece_type)
            eval_value, action = minimax(3-piece_type, new_board, board, True, alpha, beta, depth-1)
            eval_value += 5*opponent_dead - 8.5*my_dead

            if eval_value < best:
                var = 2
                best_action = [move] + action
                best = eval_value
            if best <= alpha:
                var+=1
                return best, best_action
            if best < beta:
                alpha = eval_value

        return best, best_action

if __name__ == "__main__":
    start_time = time.time()
    piece_type, previous_board, board = readInput()
    depth =2
    x, action = minimax(piece_type, board, previous_board, True, -math.inf, math.inf, depth)
    
    if action == () or action == [()]:
        action = "PASS"
    else: action = action[0]
    write_output(action)

    finish_time = time.time()