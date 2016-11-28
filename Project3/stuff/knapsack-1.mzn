int: n;
set of int: Items = 1..n;
int: capacity;

array[1..n] of int: profits;
array[1..n] of int: weights;

% setvar
var set of Items: knapsack;
% capacity
constraint sum (i in Items)
               (bool2int(i in knapsack)*weights[i]) <= capacity;

solve maximize sum (i in Items) (bool2int(i in knapsack)*profits[i]) ;

output [show(knapsack),"\n"];
