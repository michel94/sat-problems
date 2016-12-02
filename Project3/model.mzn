include "alldifferent.mzn";
include "nvalue_fn.mzn";
include "bin_packing_capa.mzn";

int: nServers;
int: nVms;
int: nJobs;
int: LB;
int: UB;

array [1..nServers] of int: res1Server;
array [1..nServers] of int: res2Server;
array [1..nVms] of int: res1Vms;
array [1..nVms] of int: res2Vms;
array [1..nJobs] of 1..nVms: jobStart;
array [1..nJobs] of 1..nVms: jobEnd;

array[1..nVms] of var 1..nServers: vmAssignment;

constraint bin_packing_capa(res1Server, vmAssignment, res1Vms);
constraint bin_packing_capa(res2Server, vmAssignment, res2Vms);

constraint forall (j in 1..nJobs) (
    alldifferent([ vmAssignment[i] | i in jobStart[j]..jobEnd[j] ])
);

constraint nvalue(vmAssignment) <= UB;
constraint nvalue(vmAssignment) >= LB;
solve minimize nvalue(vmAssignment);

output [show(vmAssignment[i]) ++ " " | i in 1..nVms];


