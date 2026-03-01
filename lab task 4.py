# Lab 4 - N-Queens Problem (Dynamic)

def print_board(board, n):
    print()
    for i in range(n):
        row = ""
        for j in range(n):
            if board[i][j] == 1:
                row = row + " Q "
            else:
                row = row + " . "
        print(row)
    print()

def is_safe(board, row, col, n):
    
    # left side of current row
    for j in range(col):
        if board[row][j] == 1:
            return False
    
    # upper left diagonal
    i = row
    j = col
    while i >= 0 and j >= 0:
        if board[i][j] == 1:
            return False
        i = i - 1
        j = j - 1
    
    # lower left diagonal
    i = row
    j = col
    while i < n and j >= 0:
        if board[i][j] == 1:
            return False
        i = i + 1
        j = j - 1
    
    return True

def solve_queens(board, col, n):
    
    # If all queens are placed
    if col >= n:
        return True
    
    # placing queen in each row of this column
    for row in range(n):
        
        if is_safe(board, row, col, n):
            
            # Place the queen
            board[row][col] = 1
            print(f"Placed Queen at Row {row + 1}, Column {col + 1}")
            
            # place rest of queens
            if solve_queens(board, col + 1, n):
                return True
            
            board[row][col] = 0
            print(f"Removed Queen from Row {row + 1}, Column {col + 1} (Backtrack)")
    
    return False

# number of queens from user
n = int(input("Enter number of queens (N): "))

board = []
for i in range(n):
    row = []
    for j in range(n):
        row.append(0)
    board.append(row)

print()
print(f"Solving {n}-Queens Problem...")
print("=" * 40)

if solve_queens(board, 0, n):
    print()
    print("Solution Found!")
    print_board(board, n)
else:
    print()
    print("No solution exists")
