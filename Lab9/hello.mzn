float: saldoInicial;
float: juro;
var float : saldoFinal;
constraint saldoFinal = saldoInicial * (1 + juro);
solve satisfy;
output ["saldoFinal= " ++ show(saldoFinal)]
