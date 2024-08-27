import numpy as np
import pandas as pd
import random

from Param_Config import args_parser

random.seed(args_parser().seed)
np.random.seed(args_parser().seed)
import Util as util
import MS_DAG as ms_dag
import Vehicle as vehicle
import Placement_Method as PM
import Routing_Method as RM
import Target_Value as TV

if __name__ == '__main__':

    random.seed(args_parser().seed)
    AlgorithmName = list()
    Request_MSIDs_List, Request_callGraph_List, Request_urgency_List = ms_dag.get_All_MSs_architecture_data(
        args_parser().config_url)

    OVNum_results = list()
    RVNum_results = list()
    sumresult_aver_req_time = list()
    sumresult_comm_time = list()
    sumresult_failure_count = list()  # 记录失败数量
    # 初始化请求车辆
    init_RVs = vehicle.get_RVs(200)
    for RV in init_RVs:
        RV.requestID, RV.timestamp = random.randint(1, len(Request_MSIDs_List) - 1), 0
        RV.deadline = Request_urgency_List[RV.requestID] * random.uniform(0.01, 0.02)
        RV.waitingtime = random.uniform(0, 0.005)
        RV.Request_MSIDs = Request_MSIDs_List[RV.requestID]
        RV.Request_callGraph = Request_callGraph_List[RV.requestID]
        RV.Request_MSs = ms_dag.get_MSs(RV.Request_MSIDs)
        RV.Request_urgency = Request_urgency_List[RV.requestID]

    #  1. 机会车辆到达, 进行微服务
    OVs = vehicle.get_OVs(100)

    # 初始化服务车辆
    # 2. 将机会车辆部署上微服务容器中
    init_SVs = PM.get_MS_placement_strategy(OVs)
    for SV in init_SVs:
        SV.longitudinalDistance = random.uniform(0, args_parser().Road_length)

    for t in range(1):

        # 4. 服务车辆list更新完成，模拟车辆请求响应
        for RV in init_RVs:
            RV.timestamp = t
            RV.success = False

        # 5. 请求调度
        data = RM.get_request_routing_policy(t, init_RVs, init_SVs)
        # data = (name, solution_dict, update_RVs); solution_dict = (请求车辆id,服务车id) = (vehicleID,vehicleID)

        # 6. 计算优化目标
        result_aver_req_time = list()
        result_comm_time = list()
        result_failure_count = list()  # 记录失败数量
        result_failure_count.append(len(init_RVs))  # 记录总请求数量
        for (name, solution_dict, update_RVs) in data:
            aver_req_time, comm_time, failure_count = TV.get_average_response_time(update_RVs, init_SVs, solution_dict)
            result_aver_req_time.append(aver_req_time)
            result_comm_time.append(comm_time)
            result_failure_count.append(failure_count)
            true_count = sum(1 for rv in update_RVs if rv.success)
            false_count = len(update_RVs) - true_count
            print(f"{t} -- {name} 平均响应时间:{aver_req_time} 额外通信时间:{comm_time}")
            print(f"{t} -- {name} RSU处理请求个数:{false_count} SV处理请求个数: {true_count} 处理失败个数:{failure_count}")
            if t == 0: AlgorithmName.append(name)
        sumresult_aver_req_time.append(result_aver_req_time)
        sumresult_comm_time.append(result_comm_time)
        sumresult_failure_count.append(result_failure_count)
    print(sumresult_aver_req_time)
    print(sumresult_comm_time)
    print(sumresult_failure_count)
    path = "result\\"+ str(args_parser().Swarm_GAP_w)
    df = pd.DataFrame(sumresult_aver_req_time, columns=AlgorithmName)
    df.to_excel(path+'sumresult_aver_req_time.xlsx', index=True)

    df = pd.DataFrame(sumresult_comm_time, columns=AlgorithmName)
    df.to_excel(path+'sumresult_comm_time.xlsx', index=True)

    df = pd.DataFrame(sumresult_failure_count, columns=["RV_Num"]+AlgorithmName)
    df.to_excel(path+'sumresult_failure_count.xlsx', index=True)

    print(f"Config:{args_parser()}")

















