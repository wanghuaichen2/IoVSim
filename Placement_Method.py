#在这里编写你的服务放置方法
import copy
import math
from tqdm import tqdm
import random

from Param_Config import args_parser
random.seed(args_parser().seed)
import MS_DAG as ms_dag
import Vehicle as vehicle


# 根据计算需求升序排序
def get_Sorted_By_limited_resource(MSID_list, MSContainers):

    #实现优先级排序
    ms_list_sorted = sorted(MSContainers,
                            key=lambda ms: args_parser().R2SP_w[0] * ms.limit_core + args_parser().R2SP_w[1] * ms.limit_memory + args_parser().R2SP_w[2] * ms.limit_storage)
    sorted_indices = [ms.MSID for ms in ms_list_sorted]

    return sorted_indices

#对每个MS调用率进行降序排序
def get_Sorted_By_MS_callRate(MSID_list, MS_callRate):
    sorted_indices = sorted(range(len(MS_callRate)), key=lambda i: MS_callRate[i], reverse=True)
    # [MSID, MSID, MSID ... ]
    return sorted_indices


#根据调用图的调用率进行降序排序
def get_Sorted_By_Request_callRate(MS_callRate, Request_MSIDs_List):
    sorted_call_rates = []
    for Request_MSIDs in Request_MSIDs_List:
        sorted_call_rate = sorted(MS_callRate[MSID] for MSID in Request_MSIDs)  # 升序排序
        sorted_call_rates.append((sorted_call_rate, len(Request_MSIDs)))
    # 根据升序排序好的调用率和列表长度进行排序
    sorted_indices = sorted(
        range(len(sorted_call_rates)),
        key=lambda i: (sorted_call_rates[i][0], -sorted_call_rates[i][1]),
        reverse=True
    )
    # [RequestID, RequestID, RequestID ... ]
    return sorted_indices

def RLS(OVs, MSID_list, MS_callRate, MSContainers):
    print("Service placement method : RLS")
    Add_SVs = list()

    for OV in OVs:
        PM_MSID_list = list()
        MS_Num = random.randint(1, len(MSID_list))
        MSIDs_List = random.sample(MSID_list, MS_Num)
        max_core = copy.deepcopy(OV.max_core)
        max_memory = copy.deepcopy(OV.max_memory)
        max_storage = copy.deepcopy(OV.max_storage)
        for MSID in MSIDs_List:
            mscontainers = next((msc for msc in MSContainers if msc.MSID == MSID), None)
            limit_core = mscontainers.limit_core
            limit_memory = mscontainers.limit_memory
            limit_storage = mscontainers.limit_storage
            if (limit_core <= max_core) & (limit_memory <= max_memory) & (
                    limit_storage <= max_storage) & (math.floor(1 if len(PM_MSID_list) == 0 else OV.max_core / len(PM_MSID_list)) != 0):
                PM_MSID_list.append(MSID)
                max_core -= limit_core
                max_memory -= limit_memory
                max_storage -= limit_storage
        Add_SV = vehicle.SV(
            vehicleID=OV.vehicleID, longitudinalDistance=OV.longitudinalDistance,
            speed=OV.speed,
            core=math.floor(OV.max_core/len(PM_MSID_list)),
            memory=math.floor(OV.max_memory/len(PM_MSID_list)),
            storage=math.floor(OV.max_storage/len(PM_MSID_list)),
            acceleration=OV.acceleration, MSIDs=list(), initTheta=args_parser().initTheta)

        Add_SV.MSIDs = copy.deepcopy(MSIDs_List)
        Add_SVs.append(Add_SV)
    return Add_SVs

def MSCRSPM(OVs, MSID_list, MS_callRate, MSContainers):
    print("Service placement method : MSCRSPM")
    Add_SVs = list()
    sorted_MSIDS = get_Sorted_By_MS_callRate(MSID_list, MS_callRate)
    for OV in OVs:
        PM_MSID_list = list()
        max_core = copy.deepcopy(OV.max_core)
        max_memory = copy.deepcopy(OV.max_memory)
        max_storage = copy.deepcopy(OV.max_storage)
        for MSID in sorted_MSIDS:
            mscontainers = next((msc for msc in MSContainers if msc.MSID == MSID), None)
            limit_core = mscontainers.limit_core
            limit_memory = mscontainers.limit_memory
            limit_storage = mscontainers.limit_storage
            if (limit_core <= max_core) & (limit_memory <= max_memory) & (
                    limit_storage <= max_storage) & (math.floor(1 if len(PM_MSID_list) == 0 else OV.max_core / len(PM_MSID_list)) != 0):
                PM_MSID_list.append(MSID)
                max_core -= limit_core
                max_memory -= limit_memory
                max_storage -= limit_storage

        Add_SV = vehicle.SV(
            vehicleID=OV.vehicleID, longitudinalDistance=OV.longitudinalDistance,
            speed=OV.speed,
            core=math.floor(OV.max_core/len(PM_MSID_list)),
            memory=math.floor(OV.max_memory/len(PM_MSID_list)),
            storage=math.floor(OV.max_storage/len(PM_MSID_list)),
            acceleration=OV.acceleration, MSIDs=list(), initTheta=1)

        Add_SV.MSIDs = copy.deepcopy(PM_MSID_list)
        Add_SVs.append(Add_SV)
    return Add_SVs

def R2SP(OVs, MSID_list, MS_callRate, MSContainers):
    print("Service placement method : R2SP")
    Request_MSIDs_List, Request_callGraph_List, Request_urgency_List = ms_dag.get_All_MSs_architecture_data(
        args_parser().config_url)

    Add_SVs = list()
    sorted_MSIDS = get_Sorted_By_limited_resource(MSID_list, MSContainers)

    for OV in OVs:

        PM_MSID_list = list()
        max_core = copy.deepcopy(OV.max_core)
        max_memory  = copy.deepcopy(OV.max_memory)
        max_storage = copy.deepcopy(OV.max_storage)
        for MSID in sorted_MSIDS:
            mscontainers = next((msc for msc in MSContainers if msc.MSID == MSID), None)
            limit_core = mscontainers.limit_core
            limit_memory = mscontainers.limit_memory
            limit_storage = mscontainers.limit_storage
            if (limit_core <= max_core) & (limit_memory <= max_memory) & (limit_storage <= max_storage) & (math.floor(1 if len(PM_MSID_list) == 0 else OV.max_core / len(PM_MSID_list)) != 0):
                PM_MSID_list.append(MSID)
                max_core -= limit_core
                max_memory -= limit_memory
                max_storage -= limit_storage

        Add_SV = vehicle.SV(
            vehicleID=OV.vehicleID, longitudinalDistance=OV.longitudinalDistance,
            speed=OV.speed,
            core=math.floor(OV.max_core/len(PM_MSID_list)),
            memory=math.floor(OV.max_memory/len(PM_MSID_list)),
            storage=math.floor(OV.max_storage/len(PM_MSID_list)),
            acceleration=OV.acceleration, MSIDs=list(), initTheta=1)

        Add_SV.MSIDs = copy.deepcopy(PM_MSID_list)
        Add_SVs.append(Add_SV)
    return Add_SVs

def GMDA(OVs, MSID_list, MS_callRate, MSContainers):
    print("Service placement method : GMDA")
    Request_MSIDs_List, Request_callGraph_List, Request_urgency_List = ms_dag.get_All_MSs_architecture_data(args_parser().config_url)
    Add_SVs = list()
    sorted_RequestID = get_Sorted_By_Request_callRate(MS_callRate, Request_MSIDs_List)

    for OV in tqdm(OVs, desc='Service placement in progress', leave=False):
        PM_MSID_list = list()
        max_core = copy.deepcopy(OV.max_core)
        max_memory = copy.deepcopy(OV.max_memory)
        max_storage = copy.deepcopy(OV.max_storage)
        for index in sorted_RequestID:
            RequestID = sorted_RequestID[index]
            for MSID in Request_MSIDs_List[RequestID]:
                mscontainers = next((msc for msc in MSContainers if msc.MSID == MSID), None)
                limit_core = mscontainers.limit_core
                limit_memory = mscontainers.limit_memory
                limit_storage = mscontainers.limit_storage
                if (limit_core <= max_core) & (limit_memory <= max_memory) & (
                            limit_storage <= max_storage) & (MSID not in PM_MSID_list) & (math.floor(1 if len(PM_MSID_list) == 0 else OV.max_core / len(PM_MSID_list)) != 0):
                    PM_MSID_list.append(MSID)
                    max_core -= limit_core
                    max_memory -= limit_memory
                    max_storage -= limit_storage

        Add_SV = vehicle.SV(
            vehicleID=OV.vehicleID, longitudinalDistance=OV.longitudinalDistance, speed=OV.speed,
            core=math.floor(OV.max_core / len(PM_MSID_list)),
            memory=math.floor(OV.max_memory / len(PM_MSID_list)),
            storage=math.floor(OV.max_storage / len(PM_MSID_list)),
            acceleration=OV.acceleration, MSIDs=list(), initTheta=1)
        Add_SV.MSIDs = copy.deepcopy(PM_MSID_list)
        Add_SVs.append(Add_SV)
    return Add_SVs

def get_MS_placement_strategy(OVs):
    MSID_list, MS_callRate = ms_dag.get_All_MSs_call_data(args_parser().config_url)

    MSContainers = ms_dag.get_MSContainers(len(MSID_list))

    # Add_SVs = RLS(OVs, MSID_list, MS_callRate, MSContainers)
    # Add_SVs = MSCRSPM(OVs, MSID_list, MS_callRate, MSContainers)
    # Add_SVs = R2SP(OVs, MSID_list, MS_callRate, MSContainers)
    Add_SVs = GMDA(OVs, MSID_list, MS_callRate, MSContainers)

    return Add_SVs