int: juro=1;
int: duracao=20;
array [0..duracao] of var int: saldo;
var bool: a;
var int: x;
bool: b=false;
bool: c=true;
constraint saldo[0]=10;
constraint forall (i in 1..duracao)( 
  %saldo[i] = saldo[i-1] + 2.00000000000
  saldo[i] = saldo[i-1] + juro
);
constraint a \/ (b /\ c);
constraint if(a) (x = 3) (x = 2);

solve satisfy;
%output ["saldo = " ++ show(i) ++ " = " ++ show(saldo[i]) ++ "\n" | i in 0..duracao];
%output a;