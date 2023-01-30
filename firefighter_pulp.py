from pulp import LpProblem, LpVariable, LpInteger, lpSum, LpMinimize, value, PULP_CBC_CMD
from helper import to_readable_string

#create a python script that will randomize the input parameters
def solve_firefighter_PULP(MAX_TIME, budget_defenders, n_nodes, n_edges, FROM, TO, START_FIRES, verbose=False):
    lp_firefighter = LpProblem("Firefighter", LpMinimize)
    NODES = range(n_nodes)
    EDGES = range(n_edges)
    time_range_func = lambda x: range(x, MAX_TIME + 1)
    time_range = time_range_func(1)

    burn_n_t = LpVariable.dicts("b", (NODES, time_range_func(0)), 0, 1, LpInteger)
    defend_n_t = LpVariable.dicts("d", (NODES, time_range_func(0)), 0, 1, LpInteger)

    obj = lpSum(burn_n_t[n][MAX_TIME] for n in NODES)
    lp_firefighter += obj, "Objective_Function"

    # burn cannot unburn after time N1
    for t in time_range:
        for n in NODES:
            lp_firefighter += burn_n_t[n][t] >= burn_n_t[n][t-1]

    # constraint N2
    for t in time_range:
        for n in NODES:
            lp_firefighter += defend_n_t[n][t] >= defend_n_t[n][t-1]

    # constraint N3
    for t in time_range:
        for n in NODES:
            for e in EDGES:
                if n == FROM[e]:
                    lp_firefighter += burn_n_t[n][t] + defend_n_t[n][t] >= burn_n_t[TO[e]][t-1]
                elif n == TO[e]:
                    lp_firefighter += burn_n_t[n][t] + defend_n_t[n][t] >= burn_n_t[FROM[e]][t-1]
                else: lp_firefighter += True

    # constraint N4
    for t in time_range:
        for n in NODES:
            lp_firefighter += defend_n_t[n][t] + burn_n_t[n][t] <= 1

    # constraint N5
    for t in time_range:
        for n in NODES:
            total_sum = burn_n_t[n][t-1] #initialize sum at the CURRENT node, but previous timestep. THEN do the same for all the neighbour NODES.
            for e in EDGES: #account for neighbours
                if n == FROM[e]:
                    total_sum += burn_n_t[TO[e]][t-1]
                elif n == TO[e]:
                    total_sum += burn_n_t[FROM[e]][t-1]
                else: total_sum += 0
            lp_firefighter += total_sum >= burn_n_t[n][t]

    # constraint N6
    for t in time_range:
        lp_firefighter += lpSum(defend_n_t[n][t] - defend_n_t[n][t-1] for n in NODES) <= budget_defenders

    #cnstraint N7
    for n in NODES:
        lp_firefighter += defend_n_t[n][0] == 0

    # constraint N8
    for n in NODES:
        if START_FIRES[n] == 1:
            lp_firefighter += burn_n_t[n][0] == 1
        else:
            lp_firefighter += burn_n_t[n][0] == 0

    if verbose:
        lp_firefighter.solve()
    else:
        lp_firefighter.solve(PULP_CBC_CMD(msg=0))

    if verbose:
        print("BURN NODES PULP:")
        for n in NODES:
            print(f"Node {n+1}:", end=" ")
            for t in time_range(0):
                print(to_readable_string(int(value(burn_n_t[n][t]))), end="")
            print()

        print("DEFEND NODES PULP:")
        for n in NODES:
            print(f"Node {n+1}:", end=" ")
            for t in time_range(0):
                print(to_readable_string(int(value(defend_n_t[n][t]))), end="")
            print()

    print(f"PULP --- TOTAL NODES BURNING: {int(value(lp_firefighter.objective))}/{len(NODES)} at time={MAX_TIME}. Time taken: {round(lp_firefighter.solutionTime * 1000, 5)} ms.")
    return {"execution_time": round(lp_firefighter.solutionTime * 1000, 5), "status": lp_firefighter.sol_status , "result": lp_firefighter}