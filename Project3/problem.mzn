include "alldifferent.mzn";
include "bin_packing_capa.mzn";

int: nServers;
int: nVms;
int: nJobs;
int: LB;
set of int: Servers = 1..nServers;

array [1..nServers] of int: res1Server;
array [1..nServers] of int: res2Server;
array [1..nVms] of int: res1Vms;
array [1..nVms] of int: res2Vms;
array [1..nJobs] of 1..nVms: jobStart;
array [1..nJobs] of 1..nVms: jobEnd;

array[1..nVms] of var 1..nServers: vmAssignment;

var set of Servers: servers;
%array[1..nServers] of var bool: servers;

constraint forall(i in vmAssignment) (i in servers);
%constraint forall(i in vmAssignment) (servers[i]);

%constraint forall (s in 1..nServers) (
%    sum (v in 1..nVms) ( (if (vmAssignment[v] == s) then res1Vms[v] else 0 endif) ) <= res1Server[s] /\
%    sum (v in 1..nVms) ( (if (vmAssignment[v] == s) then res2Vms[v] else 0 endif) ) <= res2Server[s] 
%);
constraint bin_packing_capa(res1Server, vmAssignment, res1Vms);
constraint bin_packing_capa(res2Server, vmAssignment, res2Vms);

constraint forall (j in 1..nJobs) (
    alldifferent([ vmAssignment[i] | i in jobStart[j]..jobEnd[j] ])
);


constraint card(servers) == LB;
%solve minimize card(servers);

%constraint sum(servers) >= LB;
%solve minimize sum(servers);

solve satisfy;

output [show(vmAssignment[i]) ++ " " | i in 1..nVms];



