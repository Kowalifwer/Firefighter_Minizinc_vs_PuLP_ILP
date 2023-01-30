int: MAX_TIME;
int: budget_defenders;
int: n_nodes;
int: n_edges;
array[EDGES] of NODES: FROM;
array[EDGES] of NODES: TO;
array[NODES] of 0..1: START_FIRES;

set of int: NODES = 1..n_nodes;
set of int: EDGES = 1..n_edges;
set of int: time_range = 1..MAX_TIME;
array[NODES, 0..MAX_TIME] of var 0..1: burn_n_t;
array[NODES, 0..MAX_TIME] of var 0..1: defend_n_t;

% burn cannot unburn after time N1
constraint forall(t in time_range, n in NODES) 
  (burn_n_t[n,t] >= burn_n_t[n,t-1]);

% defender cannot be reallocated after time N2
constraint forall(t in time_range, n in NODES)
  (defend_n_t[n,t] >= defend_n_t[n,t-1]);

% N3
constraint forall(t in time_range, n in NODES) (
  forall(e in EDGES) (
    if n = FROM[e] then
      burn_n_t[n,t] + defend_n_t[n,t] >= burn_n_t[TO[e],t-1]
    elseif n = TO[e] then
      burn_n_t[n,t] + defend_n_t[n,t] >= burn_n_t[FROM[e],t-1]
    else true endif
  )
);

% N4
constraint forall(t in time_range, n in NODES) 
  (burn_n_t[n,t] + defend_n_t[n,t] <= 1);

% N5
constraint forall(t in time_range, n in NODES) (
  burn_n_t[n,t-1] + sum(e in EDGES) (
    if n = FROM[e] then
      burn_n_t[TO[e],t-1]
    elseif n = TO[e] then
      burn_n_t[FROM[e],t-1]
    else 0 endif
  ) >= burn_n_t[n,t]
);

%N6
constraint forall(t in time_range)
  (sum(n in NODES)(defend_n_t[n,t] - defend_n_t[n,t-1]) <= budget_defenders);

% defend at time 0 is always 0 N7
constraint forall(n in NODES) 
  (defend_n_t[n,0] = 0);

% initialize the burn N8
constraint forall(n in NODES)(
  if START_FIRES[n] = 1 then
    burn_n_t[n,0] = 1 
  else
    burn_n_t[n,0] = 0 endif
);

constraint forall(t in time_range) (
  sum(n in NODES)(defend_n_t[n,t] - defend_n_t[n,t-1]) <= budget_defenders
);

solve minimize sum(n in NODES) (burn_n_t[n, MAX_TIME]);