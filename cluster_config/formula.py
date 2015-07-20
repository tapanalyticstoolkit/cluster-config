# Simple MB, GB and TB to Bytes calculator
KiB = 1024
MiB = KiB * 1024
GiB = MiB * 1024
TiB = GiB * 1024

cdh = {}
atk = {}

hosts = cluster.yarn.nodemanager.hosts.all()
max_cores = 0
max_memory = 0
for key in hosts:
    if hosts[key].numCores > max_cores:
        max_cores = hosts[key].numCores
    if hosts[key].totalPhysMemBytes > max_memory:
        max_memory = hosts[key].totalPhysMemBytes

###### These values are gathered by the tool from Cluster ######
NUM_NM_WORKERS = len(hosts)
NM_WORKER_CORES = max_cores
NM_WOKER_MEM = max_memory

NUM_THREADS	= 1 # This should be set to the maximum number of munti-tanent users
OVER_COMMIT_FACTOR = 1.30
MAX_JVM_MEMORY = 32768 * MiB
MEM_FRACTION_FOR_HBASE = 0.20
MEM_FRACTION_FOR_OTHER_SERVICES	= 0.20
MAPREDUCE_JOB_COUNTERS_MAX = 500

atk["intel.taproot.analytics.engine.spark.conf.properties.spark.driver.maxPermSize"] = 512 * MiB

atk["intel.taproot.analytics.engine.spark.conf.properties.spark.yarn.driver.memoryOverhead"] = 384 * MiB

atk["intel.taproot.analytics.engine.spark.conf.properties.spark.yarn.executor.memoryOverhead"] = 384 * MiB

cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_INCREMENT_ALLOCATION_MB"] = 512 * MiB

cdh["YARN.NODEMANAGER.NODEMANAGER_BASE.YARN_NODEMANAGER_RESOURCE_CPU_VCORES"] = NM_WORKER_CORES

cdh["YARN.GATEWAY.GATEWAY_BASE.YARN_APP_MAPREDUCE_AM_RESOURCE_CPU_VCORES"] = 1

cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_JOB_COUNTERS_LIMIT"] = MAPREDUCE_JOB_COUNTERS_MAX
cdh["YARN.NODEMANAGER.NODEMANAGER_BASE.NODEMANAGER_MAPRED_SAFETY_VALVE"] = \
    "<property><name>mapreduce.job.counters.max</name><value>%d</value></property>" %(MAPREDUCE_JOB_COUNTERS_MAX)
cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.RESOURCEMANAGER_MAPRED_SAFETY_VALVE"] = \
    cdh["YARN.NODEMANAGER.NODEMANAGER_BASE.NODEMANAGER_MAPRED_SAFETY_VALVE"]
cdh["YARN.JOBHISTORY.JOBHISTORY_BASE.JOBHISTORY_MAPRED_SAFETY_VALVE"] = \
    cdh["YARN.NODEMANAGER.NODEMANAGER_BASE.NODEMANAGER_MAPRED_SAFETY_VALVE"]

MEM_FOR_OTHER_SERVICES = int(NM_WOKER_MEM * MEM_FRACTION_FOR_OTHER_SERVICES)
MEM_FOR_HBASE_REGION_SERVERS = min(MAX_JVM_MEMORY, int(MEM_FOR_OTHER_SERVICES * OVER_COMMIT_FACTOR))
MEM_PER_NM = NM_WOKER_MEM - MEM_FOR_OTHER_SERVICES - MEM_FOR_HBASE_REGION_SERVERS

cdh["HBASE.REGIONSERVER.REGIONSERVER_BASE.HBASE_REGIONSERVER_JAVA_HEAPSIZE"] = \
    int(MEM_FOR_HBASE_REGION_SERVERS / OVER_COMMIT_FACTOR)

cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_MAXIMUM_ALLOCATION_MB"] = \
    (
        int(MEM_PER_NM -
            max(
                atk["intel.taproot.analytics.engine.spark.conf.properties.spark.driver.maxPermSize"],
                atk["intel.taproot.analytics.engine.spark.conf.properties.spark.yarn.driver.memoryOverhead"],
                atk["intel.taproot.analytics.engine.spark.conf.properties.spark.yarn.executor.memoryOverhead"]
            ) * 3
        ) / cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_INCREMENT_ALLOCATION_MB"]
    ) * cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_INCREMENT_ALLOCATION_MB"]

cdh["YARN.NODEMANAGER.NODEMANAGER_BASE.YARN_NODEMANAGER_RESOURCE_MEMORY_MB"] = \
    cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_MAXIMUM_ALLOCATION_MB"]

cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_MEMORY_MB"] = \
    min(
        (
            (cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_MAXIMUM_ALLOCATION_MB"] / NM_WORKER_CORES)
            / cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_INCREMENT_ALLOCATION_MB"]
        ) * cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_INCREMENT_ALLOCATION_MB"],
        MAX_JVM_MEMORY
    )

cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_REDUCE_MEMORY_MB"] = \
    min(
        2 * cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_MEMORY_MB"],
        MAX_JVM_MEMORY
    )

cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_JAVA_OPTS_MAX_HEAP"] = \
    int(cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_MEMORY_MB"] / OVER_COMMIT_FACTOR)

cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_REDUCE_JAVA_OPTS_MAX_HEAP"] = \
    2 * cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_JAVA_OPTS_MAX_HEAP"]

cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_MINIMUM_ALLOCATION_MB"] = \
    cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_MEMORY_MB"]

cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_MAXIMUM_ALLOCATION_VCORES"] = \
    cdh["YARN.NODEMANAGER.NODEMANAGER_BASE.YARN_NODEMANAGER_RESOURCE_CPU_VCORES"]

cdh["YARN.GATEWAY.GATEWAY_BASE.YARN_APP_MAPREDUCE_AM_RESOURCE_MB"] = \
    cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_MEMORY_MB"]

cdh["YARN.GATEWAY.GATEWAY_BASE.YARN_APP_MAPREDUCE_AM_MAX_HEAP"] = \
    cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_JAVA_OPTS_MAX_HEAP"]

CONTAINERS_ACCROSS_CLUSTER = \
    int(
        cdh["YARN.NODEMANAGER.NODEMANAGER_BASE.YARN_NODEMANAGER_RESOURCE_MEMORY_MB"]
        / (
            (
                cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_MEMORY_MB"] + 2 *
                max(
                    atk["intel.taproot.analytics.engine.spark.conf.properties.spark.yarn.driver.memoryOverhead"],
                    atk["intel.taproot.analytics.engine.spark.conf.properties.spark.yarn.executor.memoryOverhead"],
                    cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_INCREMENT_ALLOCATION_MB"]
                ) / cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_INCREMENT_ALLOCATION_MB"]
            )
            * cdh["YARN.RESOURCEMANAGER.RESOURCEMANAGER_BASE.YARN_SCHEDULER_INCREMENT_ALLOCATION_MB"]
        ) * NUM_NM_WORKERS
    )

GIRAPH_WORKERS_ACCROSS_CLUSTER = CONTAINERS_ACCROSS_CLUSTER - 1

atk["intel.taproot.analytics.engine.spark.conf.properties.spark.yarn.numExecutors"] = \
    int((CONTAINERS_ACCROSS_CLUSTER - NUM_THREADS) / NUM_THREADS)

atk["intel.taproot.analytics.engine.spark.conf.properties.spark.executor.memory"] = \
    cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_MEMORY_MB"]

atk["intel.taproot.analytics.engine.spark.conf.properties.spark.executor.cores"] = \
    (cdh["YARN.NODEMANAGER.NODEMANAGER_BASE.YARN_NODEMANAGER_RESOURCE_CPU_VCORES"] * NUM_NM_WORKERS - NUM_THREADS)\
    / (NUM_THREADS * atk["intel.taproot.analytics.engine.spark.conf.properties.spark.yarn.numExecutors"])

atk["intel.taproot.analytics.engine.spark.conf.properties.spark.driver.memory"] = \
    cdh["YARN.GATEWAY.GATEWAY_BASE.YARN_APP_MAPREDUCE_AM_RESOURCE_MB"]

atk["intel.taproot.analytics.api.giraph.mapreduce.map.memory.mb"] = \
    cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_MEMORY_MB"] / MiB

atk["intel.taproot.analytics.api.giraph.giraph.maxWorkers"] = \
    int((GIRAPH_WORKERS_ACCROSS_CLUSTER - NUM_THREADS - 1) / NUM_THREADS) - 1

atk["intel.taproot.analytics.api.giraph.mapreduce.map.java.opts.max.heap"] = \
    "-Xmx%sm" %(cdh["YARN.GATEWAY.GATEWAY_BASE.MAPREDUCE_MAP_JAVA_OPTS_MAX_HEAP"] / MiB)




