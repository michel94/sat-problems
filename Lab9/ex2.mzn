float: saldoInicial=10.0;
float: juro=0.4;
int: duracao=3;
array [0..duracao] of var float:saldo;
constraint saldo[0]=saldoInicial;
constraint forall (i in 1..duracao)( 
  saldo[i] = saldo[i-1] * (1+juro)
);

solve satisfy;
output ["saldo = " ++ show(i) ++ " = " ++ show(saldo[i]) ++ "\n" | i in 0..duracao];
