#!/bin/bash

export SPARK_WORKER_INSTANCES=4
export SPARK_WORKER_CORES=5
export /root/spark-2.4.0-bin-hadoop2.7

$SPARK_HOME/sbin/stop-all.sh
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-slave.sh spark://DESKTOP-AH218KE.localdomain:7077

/root/spark-2.4.0-bin-hadoop2.7/bin/spark-submit --num-executors 5  --driver-memory 1g --executor-memory 1g --master spark://DESKTOP-AH218KE.localdomain:7077 ./jumble_solver.py