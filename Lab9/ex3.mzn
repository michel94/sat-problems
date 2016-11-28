float saldoInicial;
var float: juro;
float crescimento = 0.1;
int duracao;
array [0..duracao] of var float: saldo;
constraint saldo[0] = saldoInicial
constraint saldo[duracao] = saldoInicial * (1 + crescimento);
constraint forall (i in 1..duracao)
  (saldo[i] = saldo[i-1] * (1+juro));
solve satisfy;
output ["saldo " ++ show(i) ++ " = " + show(saldo[i]) ++ "\n" | i in 0..duracao]