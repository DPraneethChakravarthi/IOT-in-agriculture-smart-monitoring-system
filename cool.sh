#!/bin/bash
clear
#nice little for loop

for f in {1..7}
do
	vcgencmd measure_temp
	sysbench --test=cpu --cpu-max-prime=20000 --num-threads=4 run >/dev/null 2>81
done

vcgencmd measure_temp