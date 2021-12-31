# use math library if needed
import math

def get_child_boards(player, board):
    """
    Generate a list of succesor boards obtained by placing a disc 
    at the given board for a given player
   
    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that will place a disc on the board
    board: the current board instance

    Returns
    -------
    a list of (col, new_board) tuples,
    where col is the column in which a new disc is placed (left column has a 0 index), 
    and new_board is the resulting board instance
    """
    res = []
    for c in range(board.cols):
        if board.placeable(c):
            tmp_board = board.clone()
            tmp_board.place(player, c)
            res.append((c, tmp_board))
    return res


def evaluate(player, board):
    """
    This is a function to evaluate the advantage of the specific player at the
    given game board.

    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the specific player
    board: the board instance

    Returns
    -------
    score: float
        a scalar to evaluate the advantage of the specific player at the given
        game board
    """
    adversary = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
    # Initialize the value of scores
    # [s0, s1, s2, s3, --s4--]
    # s0 for the case where all slots are empty in a 4-slot segment
    # s1 for the case where the player occupies one slot in a 4-slot line, the rest are empty
    # s2 for two slots occupied
    # s3 for three
    # s4 for four
    score = [0]*5
    adv_score = [0]*5

    # Initialize the weights
    # [w0, w1, w2, w3, --w4--]
    # w0 for s0, w1 for s1, w2 for s2, w3 for s3
    # w4 for s4
    weights = [0, 1, 4, 16, 1000]

    # Obtain all 4-slot segments on the board
    seg = []
    invalid_slot = -1
    left_revolved = [
        [invalid_slot]*r + board.row(r) + \
        [invalid_slot]*(board.rows-1-r) for r in range(board.rows)
    ]
    right_revolved = [
        [invalid_slot]*(board.rows-1-r) + board.row(r) + \
        [invalid_slot]*r for r in range(board.rows)
    ]
    for r in range(board.rows):
        # row
        row = board.row(r) 
        for c in range(board.cols-3):
            seg.append(row[c:c+4])
    for c in range(board.cols):
        # col
        col = board.col(c) 
        for r in range(board.rows-3):
            seg.append(col[r:r+4])
    for c in zip(*left_revolved):
        # slash
        for r in range(board.rows-3):
            seg.append(c[r:r+4])
    for c in zip(*right_revolved): 
        # backslash
        for r in range(board.rows-3):
            seg.append(c[r:r+4])
    # compute score
    for s in seg:
        if invalid_slot in s:
            continue
        if adversary not in s:
            score[s.count(player)] += 1
        if player not in s:
            adv_score[s.count(adversary)] += 1
    reward = sum([s*w for s, w in zip(score, weights)])
    penalty = sum([s*w for s, w in zip(adv_score, weights)])
    return reward - penalty


def minimax(player, board, depth_limit):
    """
    Minimax algorithm with limited search depth.

    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that needs to take an action (place a disc in the game)
    board: the current game board instance
    depth_limit: int
        the tree depth that the search algorithm needs to go further before stopping
    max_player: boolean

    Returns
    -------
    placement: int or None
        the column in which a disc should be placed for the specific player
        (counted from the most left as 0)
        None to give up the game
    """
    # record the player which call the minimax function as max player
    max_player = player
    # record the player which is the adversary as next player
    next_player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
    # initialize the action taken to be none
    placement = None
    # record the initial depth limit
    init_depth = depth_limit

### Please finish the code below ##############################################
###############################################################################
    def value(player, board, depth_limit):
        if depth_limit == 0 or board.terminal():
            # if the depth limit is reached or the board is in terminal state,
            # return the evaluated utility
            return evaluate(max_player, board)
        if player == max_player:
            # if player is max player, run max_value
            return max_value(max_player,board,depth_limit-1)
        else:
            # if player is min player, run min_value
            return min_value(next_player,board,depth_limit-1)        

    def max_value(player, board, depth_limit):
        # initialize max value as -inf
        v = -math.inf
        # for each successor board of current board
        for child in get_child_boards(player, board):
            # get the value of the board, which is the min of its child
            node = value(next_player, child[1], depth_limit)
            if node > v:
                # if a node is greater than current max value, replace it
                v = node
                nonlocal init_depth
                # having a depth of initial depth - 1 means that
                # it is the very first call of recursion, which means
                # it is the root node of game tree, so we record the action 
                # which leads to the best value when we are on the root.
                if depth_limit == init_depth - 1:
                    nonlocal placement
                    placement = child[0]
        return v
    
    def min_value(player, board, depth_limit):
        # initialize min value as inf
        v = math.inf
        # for each successor board of current board
        for child in get_child_boards(player, board):
            # get the minimum of maxs of its child
            v = min(v, value(max_player, child[1], depth_limit))
        return v
   
    # run the minimax tree as "player" being the maximizer
    score = value(player, board, depth_limit)

###############################################################################
    return placement


def alphabeta(player, board, depth_limit):
    """
    Minimax algorithm with alpha-beta pruning.

     Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that needs to take an action (place a disc in the game)
    board: the current game board instance
    depth_limit: int
        the tree depth that the search algorithm needs to go further before stopping
    alpha: float
    beta: float
    max_player: boolean


    Returns
    -------
    placement: int or None
        the column in which a disc should be placed for the specific player
        (counted from the most left as 0)
        None to give up the game
    """
    # record the player which call the minimax function as max player
    max_player = player
    # record the player which is the adversary as next player
    next_player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
    # initialize the action taken to be none
    placement = None
    # record the initial depth limit
    init_depth = depth_limit

### Please finish the code below ##############################################
###############################################################################
    # initialize max's best option on path to root as -inf
    alpha = -math.inf
    # initialize min's best option on path to root as inf
    beta = math.inf

    def value(player, board, depth_limit, alpha, beta):
        if depth_limit == 0 or board.terminal():
            # if the depth limit is reached or the board is in terminal state,
            # return the evaluated utility
            return evaluate(max_player, board)
        if player == max_player:
            # if player is max player, run max_value
            return max_value(max_player,board,depth_limit-1, alpha, beta)
        else:
            # if player is min player, run min_value
            return min_value(next_player,board,depth_limit-1, alpha, beta)

    def max_value(player, board, depth_limit, alpha, beta):
        # initialize max value as -inf
        v = -math.inf
        # for each successor board of current board
        for child in get_child_boards(player, board):
            # get the value of the board, which is the min of its child
            node = value(next_player, child[1], depth_limit, alpha, beta)
            if node > v:
                # if a node is greater than current max value, replace it
                v = node
                nonlocal init_depth
                # having a depth of initial depth - 1 means that
                # it is the very first call of recursion, which means
                # it is the root node of game tree, so we record the action 
                # which leads to the best value when we are on the root.
                if depth_limit == init_depth - 1:
                    nonlocal placement
                    placement = child[0]
            # if current max value of this node already greater than current min value of minimizer above it, 
            # then that minimizer will definitely not choose this branch,
            # because the max value will never go down. Therefore, just return current max value and skip the rest
            if v >= beta:
                return v
            # keep updating max's best option 
            alpha = max(alpha, v)
        return v
    
    def min_value(player, board, depth_limit, alpha, beta):
        # initialize min value as inf
        v = math.inf
        # for each successor board of current board
        for child in get_child_boards(player, board):
            # get the minimum of maxs of its child
            v = min(v, value(max_player, child[1], depth_limit, alpha, beta))
            # if current min value of this node already samller than current max value of maximizer above it, 
            # then that maximizer will definitely not choose this branch,
            # because the min value will never go up. Therefore, just return current min value and skip the rest
            if v<= alpha:
                return v
            # keep updating min's best option 
            beta = min(beta, v)
        return v

    # run the minimax tree with alphabeta pruning as "player" being the maximizer
    score = value(player, board, depth_limit, alpha, beta)
###############################################################################
    return placement


def expectimax(player, board, depth_limit):
    """
    Expectimax algorithm.
    We assume that the adversary of the initial player chooses actions
    uniformly at random.
    Say that it is the turn for Player 1 when the function is called initially,
    then, during search, Player 2 is assumed to pick actions uniformly at
    random.

    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that needs to take an action (place a disc in the game)
    board: the current game board instance
    depth_limit: int
        the tree depth that the search algorithm needs to go before stopping
    max_player: boolean

    Returns
    -------
    placement: int or None
        the column in which a disc should be placed for the specific player
        (counted from the most left as 0)
        None to give up the game
    """
    # record the player which call the minimax function as max player
    max_player = player
    # record the player which is the adversary as next player
    next_player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
    # initialize the action taken to be none
    placement = None
    # record the initial depth limit
    init_depth = depth_limit

### Please finish the code below ##############################################
###############################################################################
    def value(player, board, depth_limit):
        if depth_limit == 0 or board.terminal():
            # if the depth limit is reached or the board is in terminal state,
            # return the evaluated utility
            return evaluate(max_player, board)
        if player == max_player:
            # if player is max player, run max_value
            return max_value(max_player,board,depth_limit-1)
        else:
            # if player is random player, run min_value(as exp_value)
            return min_value(next_player,board,depth_limit-1)

    def max_value(player, board, depth_limit):
        # initialize max value as -inf
        v = -math.inf
        # for each successor board of current board
        for child in get_child_boards(player, board):
            # get the value of the board, which is the min of its child
            node = value(next_player, child[1], depth_limit)
            if node > v:
                # if a node is greater than current max value, replace it
                v = node
                nonlocal init_depth
                # having a depth of initial depth - 1 means that
                # it is the very first call of recursion, which means
                # it is the root node of game tree, so we record the action 
                # which leads to the best value when we are on the root.
                if depth_limit == init_depth - 1:
                    nonlocal placement
                    placement = child[0]
        return v
    
    def min_value(player, board, depth_limit):
        # initialize expected value as 0
        v = 0
        # for each successor board of current board
        for child in get_child_boards(player, board):
            # here we assume uniformly random, so we just devide the sum of all board value by number of boards
            v = v + value(max_player, child[1], depth_limit)
            v = v/len(get_child_boards(player, board))
        return v

    # run the minimax tree with alphabeta pruning as "player" being the maximizer
    score = value(player, board, depth_limit)
###############################################################################
    return placement


if __name__ == "__main__":
    from game_gui import GUI
    import tkinter

    algs = {
        "Minimax": minimax,
        "Alpha-beta pruning": alphabeta,
        "Expectimax": expectimax
    }

    root = tkinter.Tk()
    GUI(algs, root)
    root.mainloop()