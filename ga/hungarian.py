import pickle

def hungarian_math_team(matrix):
    INF = 100 # infinity
    size = len(matrix)
    rowindex = [-1] * size
        
    m = [[INF - matrix[row][col] for col in range(size)] for row in range(size)]
    # transforms minimization problem to a maximization problem
    
    def assign(row, col):
        """Specific to math team: don't want people to do same round twice"""
        for r in range(row - row % 3, row - row % 3 + 3):
            for c in range(col - col % 5, col - col % 5 + 5):
                if r != row or c != col:
                    m[r][c] += INF
    
    def unassign(row, col):
        """Reverses the assignment effect"""
        for r in range(row - row % 3, row - row % 3 + 3):
            for c in range(col - col % 5, col - col % 5 + 5):
                if r != row or c != col:
                    m[r][c] -= INF
                    
    for row in range(size):
        swaps = [-1] * size
        mins = [INF] * size
        visited = [False] * size
        markedrow = row
        markedcol = -1
        
        while markedrow != -1:
            col = -1
            for ccol in range(size):
                if not visited[ccol]:
                    cur = m[markedrow][ccol]
                    if cur < mins[ccol]:
                        mins[ccol] = cur
                        swaps[ccol] = markedcol
                    if col == -1 or mins[ccol] < mins[col]:
                        col = ccol
                        
            delta = mins[col]
            for ccol in range(size):
                if visited[ccol]:
                    for r in range(size):
                        m[r][ccol] += delta
                    for c in range(size):
                        m[rowindex[ccol]][c] -= delta
                else:
                    mins[ccol] -= delta
            for c in range(size):
                m[row][c] -= delta
            
            visited[col] = True
            markedcol = col
            markedrow = rowindex[col]
                
        while swaps[col] != -1:
            rowindex[col] = rowindex[swaps[col]]
            unassign(rowindex[swaps[col]], swaps[col])
            assign(rowindex[col], col)
            col = swaps[col]
                
        rowindex[col] = row
        assign(rowindex[col], col)
        
    return [(rowindex[col], col) for col in range(size)]

def generate_matrix(scores, team):
    return [[scores[person][round] for round in range(6) for i in range(5)] for person in team for i in range(3)]
    
def generate_table(matrix, players, round_picks):
    ret = []
    for i in range(len(players)):
        ret.append([0] * 6)
    for pick in round_picks:
        ret[pick[0]//3][pick[1]//5] = matrix[pick[0]][pick[1]]
    return ret

def results(scores, players):
    res = ''
    matrix = generate_matrix(scores, players)
    table = generate_table(matrix, players, hungarian_math_team(matrix))
    l = max(len(p) for p in players) + 1
    for i in range(len(players)):
        res += players[i] + ':' + ' ' * (l - len(players[i]))
        for j in range(len(table[i])):
            if table[i][j]:
                res += 'Round' + str(j + 1) + ': ' + str(table[i][j]) + ', '
        res += 'Total: ' + str(sum(table[i])) + '\n'
    res += 'Team total: ' + str(sum(sum(table[i]) for i in range(len(table))))
    return res


if __name__ == "__main__":
    scores = {
        'Matt': [2, 4, 6, 2, 2, 2],
        'Ashvin': [4, 4, 6, 4, 4, 4],
        'Donald': [6, 2, 4, 2, 6, 2],
        'Will': [6, 2, 2, 6, 2, 2],
        'Richard': [2, 2, 0, 2, 0, 2],
        'Ning': [4, 2, 4, 4, 4, 2],
        'Amelia': [6, 4, 6, 4, 6, 6],
        'Saavan': [4, 6, 2, 2, 4, 2],
        'George': [6, 6, 4, 6, 6, 6],
        'Kevin': [2, 4, 4, 6, 6, 4]
    }

    players = ['Matt', 'Ashvin', 'Donald', 'Will', 'Ning', 'Amelia', 'Saavan', 'Richard', 'George', 'Kevin']

    print(results(scores, players))

    import time 
    
    s = time.time()
    for i in range(3000):
        results(scores, players)
    print(time.time() - s)
