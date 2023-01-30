from minizinc import Instance, Model, Solver
from helper import to_readable_string

def solve_firefighter_MINIZINC(MAX_TIME, budget_defenders, n_nodes, n_edges, FROM, TO, START_FIRES, verbose=False):
    firefighter = Model("firefighter.mzn")
    solver = Solver.lookup("cbc")
    instance = Instance(solver, firefighter)
    instance["MAX_TIME"] = MAX_TIME
    instance["budget_defenders"] = budget_defenders
    instance["n_nodes"] = n_nodes
    instance["n_edges"] = n_edges
    instance["FROM"] = [i+1 for i in FROM] # 0-indexed to 1-indexed
    instance["TO"] = [i+1 for i in TO] # 0-indexed to 1-indexed
    instance["START_FIRES"] = START_FIRES

    result = instance.solve()

    if verbose:
        burn = result.solution.burn_n_t
        defend = result.solution.defend_n_t

        print("BURN NODES MINIZINC:")
        for i in range(n_nodes):
            print(f"Node {i+1}:", end=" ")
            for j in range(MAX_TIME):
                print(to_readable_string(burn[i][j]), end="")
            print()

        print("DEFEND NODES MINIZINC:")
        for i in range(n_nodes):
            print(f"Node {i+1}:", end=" ")
            for j in range(MAX_TIME):
                print(to_readable_string(defend[i][j]), end="")
            print()

    solve_time_ms = round(result.statistics['flatTime'].microseconds / 1e+3 + result.statistics['solveTime'].microseconds / 1e+3, 5)
    print(f"MINIZINC --- TOTAL NODES BURNING: {result.objective}/{n_nodes} at time={MAX_TIME}. Time taken: {solve_time_ms} ms.")

    return {"execution_time": solve_time_ms, "status": result.status, "result": result}