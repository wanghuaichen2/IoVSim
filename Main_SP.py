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

import numpy as np


def roulette_wheel_selection(probabilities, n):
    # 累积概率分布
    cumulative_probabilities = np.cumsum(probabilities)

    # 生成 n 个随机数
    random_numbers = np.random.rand(n)

    # 根据累积概率分布确定对应的下标
    indices = np.searchsorted(cumulative_probabilities, random_numbers)

    return indices


if __name__ == '__main__':

    random.seed(args_parser().seed)
    OVNum_lambda = args_parser().OVNum_lambda  # 机会车辆进入数量服从泊松分布
    RVNum_lambda = args_parser().RVNum_lambda  # 请求车辆发送请求服从泊松分布
    AlgorithmName = list()
    Request_MSIDs_List, Request_callGraph_List, Request_urgency_List = ms_dag.get_All_MSs_architecture_data(
        args_parser().config_url)

    OVNum_results = list()
    RVNum_results = list()
    sumresult_aver_req_time = list()
    sumresult_comm_time = list()
    sumresult_failure_count = list()  # 记录失败数量

    # 初始化服务车辆
    init_SVs = list()
    # 初始化请求车辆

    # 给定请求的概率值列表
    # probabilities = [0.50, 0.20, 0.15, 0.15]
    probabilities = [0.10, 0.70, 0.20]
    # 将概率值归一化
    probabilities = np.array(probabilities) / np.sum(probabilities)
    RVNum = np.random.poisson(RVNum_lambda)
    # 获取生成的下标
    requestID_indices = roulette_wheel_selection(probabilities, RVNum)
    init_RVs = vehicle.get_RVs(RVNum)
    i = 0
    for RV in init_RVs:
        RV.requestID = requestID_indices[i]
        RV.timestamp = 0
        RV.deadline = Request_urgency_List[RV.requestID] * random.uniform(0.01, 0.02)
        RV.waitingtime = random.uniform(0, 0.005)
        RV.Request_MSIDs = Request_MSIDs_List[RV.requestID]
        RV.Request_callGraph = Request_callGraph_List[RV.requestID]
        RV.Request_MSs = ms_dag.get_MSs(RV.Request_MSIDs)
        RV.Request_urgency = Request_urgency_List[RV.requestID]
        i += 1

    # 请求的产生: 在道路长度 0-350m 内，随机产生不同数量的请求，分布到请求车辆上，请求车辆数量 <= 请求数量
    # 机会车辆的到来: 每时刻 t 都有一定数量的机会车辆到达该路段，车辆位置为 0m。部署完微服务后，加入到服务车辆列表
    # 服务车辆的离去: 定期删除车辆位置 > 350m 的服务车辆
    for t in range(args_parser().T):
        #  1. 机会车辆到达, 进行微服务部署
        OVNum = 100  #50、100、150、200、250、300、350
        OVs = vehicle.get_OVs(OVNum)
        #分散在道路中
        for OV in OVs:
            OV.longitudinalDistance = random.uniform(0, args_parser().Road_length)    #(m)

        # 2. 将机会车辆部署上微服务容器中
        Add_SVs = PM.get_MS_placement_strategy(OVs)
        init_SVs.extend(Add_SVs)

        # 3. 微服务部署完成，更新服务车辆list
        init_SVs = util.Update_vehicle_location_information(init_SVs)

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
