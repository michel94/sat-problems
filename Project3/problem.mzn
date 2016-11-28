include "alldifferent.mzn";
int: nServers;
int: nVms;
int: nJobs;
set of int: Servers = 1..nServers;
output [ show(nServers),"\n"];

array [1..nServers] of int: res1Server;
array [1..nServers] of int: res2Server;
array [1..nVms] of int: res1Vms;
array [1..nVms] of int: res2Vms;
array [1..nJobs] of 1..nVms: jobStart;
array [1..nJobs] of 1..nVms: jobEnd;

var set of int: Items = 1..nServers;
array[1..nVms] of var 1..nServers: vmAssignment;

var set of Servers: servers;

constraint forall(i in vmAssignment) (i in servers);
constraint forall (s in 1..nServers) (
    sum (v in 1..nVms) ( (if (vmAssignment[v] == s) then res1Vms[v] else 0 endif) ) <= res1Server[s] /\
    sum (v in 1..nVms) ( (if (vmAssignment[v] == s) then res2Vms[v] else 0 endif) ) <= res2Server[s]
);
constraint forall (j in 1..nJobs) (
    alldifferent([ vmAssignment[i] | i in jobStart[j]..jobEnd[j] ])
);

solve minimize card(servers);

output [show(vmAssignment), "\n", show(servers),"\n"];
