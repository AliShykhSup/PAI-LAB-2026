# Lab 3 - Water Jug Problem using DFS

# We have 2 jugs
# Jug1 can hold 4 liters
# Jug2 can hold 3 liters
# Goal: Get exactly 2 liters in Jug1

jug1 = 0
jug2 = 0
jug1_capacity = 4
jug2_capacity = 3
target = 2

visited_states = []
solution_path = []

def print_state(step, rule, j1, j2):
    print(f"Step {step}: {rule}")
    print(f"         Jug1 = {j1} liters, Jug2 = {j2} liters")
    print()

def solve(j1, j2, steps):
    
    if j1 == target:
        print("Goal Reached!")
        return True
    
    state = (j1, j2)
    if state in visited_states:
        return False
    
    visited_states.append(state)
    solution_path.append((j1, j2))
    
    # Rule 1: Fill Jug1
    new_j1 = jug1_capacity
    new_j2 = j2
    if (new_j1, new_j2) not in visited_states:
        print_state(steps, "Fill Jug1", new_j1, new_j2)
        if solve(new_j1, new_j2, steps + 1):
            return True
    
    # Rule 2: Fill Jug2
    new_j1 = j1
    new_j2 = jug2_capacity
    if (new_j1, new_j2) not in visited_states:
        print_state(steps, "Fill Jug2", new_j1, new_j2)
        if solve(new_j1, new_j2, steps + 1):
            return True
    
    # Rule 3: Empty Jug1
    new_j1 = 0
    new_j2 = j2
    if (new_j1, new_j2) not in visited_states:
        print_state(steps, "Empty Jug1", new_j1, new_j2)
        if solve(new_j1, new_j2, steps + 1):
            return True
    
    # Rule 4: Empty Jug2
    new_j1 = j1
    new_j2 = 0
    if (new_j1, new_j2) not in visited_states:
        print_state(steps, "Empty Jug2", new_j1, new_j2)
        if solve(new_j1, new_j2, steps + 1):
            return True
    
    # Rule 5: Pour Jug1 into Jug2
    pour_amount = min(j1, jug2_capacity - j2)
    new_j1 = j1 - pour_amount
    new_j2 = j2 + pour_amount
    if (new_j1, new_j2) not in visited_states:
        print_state(steps, "Pour Jug1 into Jug2", new_j1, new_j2)
        if solve(new_j1, new_j2, steps + 1):
            return True
    
    # Rule 6: Pour Jug2 into Jug1
    pour_amount = min(j2, jug1_capacity - j1)
    new_j1 = j1 + pour_amount
    new_j2 = j2 - pour_amount
    if (new_j1, new_j2) not in visited_states:
        print_state(steps, "Pour Jug2 into Jug1", new_j1, new_j2)
        if solve(new_j1, new_j2, steps + 1):
            return True
    
    return False

print("Water Jug Problem - DFS Solution")
print("=" * 40)
print(f"Jug1 capacity: {jug1_capacity} liters")
print(f"Jug2 capacity: {jug2_capacity} liters")
print(f"Target: {target} liters in Jug1")
print("=" * 40)
print()

print_state(0, "Start", 0, 0)
solve(0, 0, 1)
