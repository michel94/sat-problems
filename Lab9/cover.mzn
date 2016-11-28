int: nVert = 4;
array [1..nVert] of set of int: arcos = [{2,3,4}, {1}, {1}, {1}];
array [1..nVert] of var bool: cobertura;

constraint forall (u in 1..nVert)
  (forall (v in arcos[u])
    (cobertura[u] \/ cobertura[v]));

solve minimize sum(u in 1..nVert) (cobertura[u]);
output ["vertice " ++ show(u) ++ " = " ++ show(cobertura[u]) ++ "\n" | u in 1..nVert]
