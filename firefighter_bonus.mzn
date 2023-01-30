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
array[NODES, 0..MAX_TIME] of var bool: burn_n_t;
array[NODES, 0..MAX_TIME] of var bool: defend_n_t;

% burn cannot unburn after time N1
constraint forall(t in time_range, n in NODES) 
  (bool2int(burn_n_t[n,t]) >= bool2int(burn_n_t[n,t-1]));

% defender cannot be reallocated after time N2
constraint forall(t in time_range, n in NODES)
  (bool2int(defend_n_t[n,t]) >= bool2int(defend_n_t[n,t-1]));

% N3
constraint forall(t in time_range, n in NODES) (
  forall(e in EDGES) (
    if n = FROM[e] then
      bool2int(burn_n_t[n,t]) + bool2int(defend_n_t[n,t]) >= bool2int(burn_n_t[TO[e],t-1])
    elseif n = TO[e] then
      bool2int(burn_n_t[n,t]) + bool2int(defend_n_t[n,t]) >= bool2int(burn_n_t[FROM[e],t-1])
    else true endif
  )
);

% N4
constraint forall(t in time_range, n in NODES) 
  (bool2int(burn_n_t[n,t]) + bool2int(defend_n_t[n,t]) <= 1);

% N5
constraint forall(t in time_range, n in NODES) (
  bool2int(burn_n_t[n,t-1]) + sum(e in EDGES) (
    if n = FROM[e] then
      bool2int(burn_n_t[TO[e],t-1])
    elseif n = TO[e] then
      bool2int(burn_n_t[FROM[e],t-1])
    else 0 endif
  ) >= bool2int(burn_n_t[n,t])
);

%N6
constraint forall(t in time_range)
  (sum(n in NODES)(bool2int(defend_n_t[n,t]) - bool2int(defend_n_t[n,t-1])) <= budget_defenders);

% defend at time 0 is always 0 N7
constraint forall(n in NODES) 
  (bool2int(defend_n_t[n,0]) = 0);

% initialize the burn N8
constraint forall(n in NODES)(
  if START_FIRES[n] = 1 then
    bool2int(burn_n_t[n,0]) = 1 
  else
    bool2int(burn_n_t[n,0]) = 0 endif
);

constraint forall(t in time_range) (
  sum(n in NODES)(bool2int(defend_n_t[n,t]) - bool2int(defend_n_t[n,t-1])) <= budget_defenders
);

solve minimize sum(n in NODES) (bool2int(burn_n_t[n, MAX_TIME]));