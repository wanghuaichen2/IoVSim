#在这里编写你的请求路由方法
import copy
import random

from Param_Config import args_parser
random.seed(args_parser().seed)
import Target_Value as TV
import Util as util
def RSU_Only(t, init_RVs, init_SVs):
    update_RVs = copy.deepcopy(init_RVs)
    # 请求由RSU处理
    solution_dict = {}
    return solution_dict, update_RVs

def Random_Route(t, init_RVs, init_SVs):
    update_RVs = copy.deepcopy(init_RVs)
    # 查看每个服务车辆捕获请求，决定是否处理
    solution_dict = {}
    for SV in init_SVs:
        SV_longitudinalDistance = SV.longitudinalDistance
        SV_MSIDs = SV.MSIDs
        SV_requestRVs = list()  # 记录附近的请求车辆
        # 范围内是否有请求
        for RV in update_RVs:
            length = abs(SV_longitudinalDistance - RV.longitudinalDistance)
            if length >= args_parser().Comm_distance:  # 过滤通信范围
                continue
            # 过滤请求已经处理的车辆
            if RV.success:
                continue
            SV_requestRVs.append(RV)


        if len(SV_requestRVs) == 0:  #没有当前车辆需要处理的请求，下一辆车
            continue
        else:
            Select_RV = random.choice(SV_requestRVs)
            Select_requestRVID = Select_RV.vehicleID
            # 获得请求的首个微服务，需要从此微服务进入
            requestMSID = Select_RV.Request_MSIDs[0]
            if requestMSID in SV_MSIDs:  # 符合条件
                solution_dict[Select_requestRVID] = SV.vehicleID
                Select_RV.success = True
    return solution_dict, update_RVs

def old_Random_Route(t, init_RVs, init_SVs):
    update_RVs = copy.deepcopy(init_RVs)
    # 查看每个服务车辆捕获请求，决定是否处理
    solution_dict = {}
    for SV in init_SVs:
        SV_longitudinalDistance = SV.longitudinalDistance
        SV_MSIDs = SV.MSIDs
        SV_requestRVs = list()  # 记录附近的请求车辆
        # 范围内是否有请求
        for RV in update_RVs:
            length = abs(SV_longitudinalDistance - RV.longitudinalDistance)
            if length >= args_parser().Comm_distance:  # 过滤通信范围
                continue
            # 获得请求的首个微服务，需要从此微服务进入
            requestMSID = RV.Request_MSIDs[0]
            if requestMSID not in SV_MSIDs:  # 过滤不符合条件
                continue
            # 过滤请求已经处理的车辆
            if RV.success:
                continue
            SV_requestRVs.append(RV)


        if len(SV_requestRVs) == 0:  #没有当前车辆需要处理的请求，下一辆车
            continue
        else:
            Select_requestRVID = random.choice(SV_requestRVs).vehicleID
            solution_dict[Select_requestRVID] = SV.vehicleID
            [RV for RV in SV_requestRVs if RV.vehicleID == Select_requestRVID][0].success = True
    return solution_dict, update_RVs

def Distance_prioritize(t, init_RVs, init_SVs):
    update_RVs = copy.deepcopy(init_RVs)
    # 查看每个服务车辆捕获请求，决定是否处理
    solution_dict = {}
    for SV in init_SVs:
        SV_longitudinalDistance = SV.longitudinalDistance
        SV_MSIDs = SV.MSIDs
        SV_requestRVs = list()  # 记录附近的请求车辆
        # 范围内是否有请求
        for RV in update_RVs:
            length = abs(SV_longitudinalDistance - RV.longitudinalDistance)
            if length >= args_parser().Comm_distance:  # 过滤通信范围
                continue
            # 获得请求的首个微服务，需要从此微服务进入
            requestMSID = RV.Request_MSIDs[0]
            if requestMSID not in SV_MSIDs:  # 过滤不符合条件
                continue
            # 过滤请求已经处理的车辆
            if RV.success:
                continue
            SV_requestRVs.append(RV)


        if len(SV_requestRVs) == 0:  #没有当前车辆需要处理的请求，下一辆车
            continue
        else:
            Select_requestRVID = min(SV_requestRVs, key=lambda RV: abs(SV_longitudinalDistance-RV.longitudinalDistance )).vehicleID
            solution_dict[Select_requestRVID] = SV.vehicleID
            [RV for RV in SV_requestRVs if RV.vehicleID == Select_requestRVID][0].success = True
    return solution_dict, update_RVs

def Swarm_old_GAP_NoComm(t,init_RVs,init_SVs):
    update_RVs = copy.deepcopy(init_RVs)
    # 查看每个服务车辆捕获请求，决定是否处理
    solution_dict = {}
    for SV in init_SVs:
        SV_longitudinalDistance = SV.longitudinalDistance
        SV_MSIDs = SV.MSIDs
        SV_requestRVs = list()  # 记录附近的请求车辆
        # 范围内是否有请求
        for RV in update_RVs:
            length = abs(SV_longitudinalDistance - RV.longitudinalDistance)
            if length >= args_parser().Comm_distance:  # 过滤通信范围
                continue
            # 获得请求的首个微服务，需要从此微服务进入
            requestMSID = RV.Request_MSIDs[0]
            if requestMSID not in SV_MSIDs:  # 过滤不符合条件
                continue
            # 过滤请求已经处理的车辆
            if RV.success:
                continue
            SV_requestRVs.append(RV)

        #没有该服务车辆没有接收到请求
        if len(SV_requestRVs) == 0:  # 没有车辆处理该请求，下一辆车
            continue

        # 构建选择概率模型
        w_1 = args_parser().Swarm_GAP_w[0]
        w_2 = args_parser().Swarm_GAP_w[1]
        w_3 = args_parser().Swarm_GAP_w[2]
        w_4 = args_parser().Swarm_GAP_w[3]

        Select_Max_Ps_dict = {}
        for requestRV in SV_requestRVs:
            # 计算请求刺激Request_urgency
            Strength = w_1 * ((3 - (t - requestRV.timestamp))/3) + w_2 * (requestRV.Request_urgency)
            #计算阈值
            Theta = w_3 * (abs(SV_longitudinalDistance - requestRV.longitudinalDistance)) + w_4 * requestRV.deadline
            Select_P = (Theta ** args_parser().Swarm_GAP_n) / (
                        (Theta ** args_parser().Swarm_GAP_n) + (Strength ** args_parser().Swarm_GAP_n))
            Select_Max_Ps_dict[requestRV.vehicleID] = Select_P

        if len(Select_Max_Ps_dict) == 0:  # 车辆不处理该请求
            continue
        else:
            Select_requestRVID = max(Select_Max_Ps_dict, key=Select_Max_Ps_dict.get)
            [RV for RV in SV_requestRVs if RV.vehicleID == Select_requestRVID][0].success = True

            solution_dict[Select_requestRVID] = SV.vehicleID


    return solution_dict, update_RVs

def Swarm_GAP_NoComm(t,init_RVs,init_SVs):
    update_RVs = copy.deepcopy(init_RVs)
    # 查看每个服务车辆捕获请求，决定是否处理
    solution_dict = {}
    for SV in init_SVs:
        SV_longitudinalDistance = SV.longitudinalDistance
        SV_MSIDs = SV.MSIDs
        SV_requestRVs = list()  # 记录附近的请求车辆
        # 范围内是否有请求
        for RV in update_RVs:
            length = abs(SV_longitudinalDistance - RV.longitudinalDistance)
            if length >= args_parser().Comm_distance:  # 过滤通信范围
                continue
            # 获得请求的首个微服务，需要从此微服务进入
            requestMSID = RV.Request_MSIDs[0]
            if requestMSID not in SV_MSIDs:  # 过滤不符合条件
                continue
            # 过滤请求已经处理的车辆
            if RV.success:
                continue
            SV_requestRVs.append(RV)

        #没有该服务车辆没有接收到请求
        if len(SV_requestRVs) == 0:  # 没有车辆处理该请求，下一辆车
            continue

        # 构建选择概率模型
        w_1 = args_parser().Swarm_GAP_w[0]
        w_2 = args_parser().Swarm_GAP_w[1]
        w_3 = args_parser().Swarm_GAP_w[2]
        w_4 = args_parser().Swarm_GAP_w[3]

        Select_Max_Ps_dict = {}
        for requestRV in SV_requestRVs:
            # 计算请求刺激Request_urgency
            Strength = w_1 * (requestRV.waitingtime) + w_2 * (1/requestRV.Request_urgency) + w_3 * (args_parser().Comm_distance - abs(SV_longitudinalDistance - requestRV.longitudinalDistance))
            #计算阈值
            Theta = w_4 * requestRV.deadline

            Select_P = (Strength ** args_parser().Swarm_GAP_n) / (
                        (Theta ** args_parser().Swarm_GAP_n) + (Strength ** args_parser().Swarm_GAP_n))

            Select_Max_Ps_dict[requestRV.vehicleID] = Select_P

        if len(Select_Max_Ps_dict) == 0:  # 车辆不处理该请求
            continue
        else:
            Select_requestRVID = max(Select_Max_Ps_dict, key=Select_Max_Ps_dict.get)
            [RV for RV in SV_requestRVs if RV.vehicleID == Select_requestRVID][0].success = True

            solution_dict[Select_requestRVID] = SV.vehicleID


    return solution_dict, update_RVs

def Swarm_GAP_Comm(t,init_RVs,init_SVs):
    update_RVs = copy.deepcopy(init_RVs)
    # 查看每个服务车辆捕获请求，决定是否处理
    solution_dict = {}
    for SV in init_SVs:
        SV_longitudinalDistance = SV.longitudinalDistance
        SV_MSIDs = SV.MSIDs
        SV_requestRVs = list()  # 记录附近的请求车辆
        # 范围内是否有请求
        for RV in update_RVs:
            length = abs(SV_longitudinalDistance - RV.longitudinalDistance)
            if length >= args_parser().Comm_distance:  # 过滤通信范围
                continue
            # 获得请求的首个微服务，需要从此微服务进入
            requestMSID = RV.Request_MSIDs[0]
            if requestMSID not in SV_MSIDs:  # 过滤不符合条件
                continue
            # 过滤请求已经处理的车辆
            if RV.success:
                continue
            SV_requestRVs.append(RV)

        #没有该服务车辆没有接收到请求
        if len(SV_requestRVs) == 0:  # 没有车辆处理该请求，下一辆车
            continue

        # 获得邻居服务车辆
        neighbor_SVs = [neighbor_SV for neighbor_SV in init_SVs if
                        (abs(neighbor_SV.longitudinalDistance - SV_longitudinalDistance) <= args_parser().Comm_distance)]

        # 构建选择概率模型
        w_1 = args_parser().Swarm_GAP_w[0]
        w_2 = args_parser().Swarm_GAP_w[1]
        w_3 = args_parser().Swarm_GAP_w[2]
        w_4 = args_parser().Swarm_GAP_w[3]

        Select_Max_Ps_dict = {}
        for requestRV in SV_requestRVs:
            cooperate_SVs = list()
            cooperate_SVs.append(SV)
            cooperate_SVs.extend(neighbor_SVs)
            if not util.check_MSs_in_neighbor_SVs(requestRV.Request_MSIDs, cooperate_SVs):
                continue
            # 计算阈值
            Strength = w_1 * (requestRV.waitingtime) + w_2 * (1/requestRV.Request_urgency) + w_3 * (args_parser().Comm_distance - abs(SV_longitudinalDistance - requestRV.longitudinalDistance))
            # Theta = w_4 * SV.get_theta(requestRV.requestID)
            # Theta = w_4 * (requestRV.deadline - SV.get_theta(requestRV.requestID))
            Theta = w_4 * (requestRV.deadline)
            # 计算请求刺激
            Select_P = (Strength**args_parser().Swarm_GAP_n) / ((Theta**args_parser().Swarm_GAP_n) + (Strength**args_parser().Swarm_GAP_n))
            Select_Max_Ps_dict[requestRV.vehicleID] = Select_P
        if len(Select_Max_Ps_dict) == 0:  # 车辆不处理该请求
            continue
        else:
            Select_requestRVID = max(Select_Max_Ps_dict, key=Select_Max_Ps_dict.get)
            select_RV = [RV for RV in SV_requestRVs if RV.vehicleID == Select_requestRVID][0]
            solution_dict[Select_requestRVID] = SV.vehicleID
            select_RV.success = True

            #阈值更新
            req_time, comm_time = TV.get_one_req_comm_time(select_RV, init_SVs, SV.vehicleID)
            k2 = (select_RV.deadline - req_time)/select_RV.deadline
            SV.index_theta_dict[select_RV.requestID] = k2
            # SV.index_theta_dict[select_RV.requestID] = (SV.get_theta(select_RV.requestID) + (args_parser().initTheta - (w_4 * k2)))/2
    return solution_dict, update_RVs

def Swarm_GAP_RouletteComm(t,init_RVs,init_SVs):
    update_RVs = copy.deepcopy(init_RVs)
    # 查看每个服务车辆捕获请求，决定是否处理
    solution_dict = {}
    for SV in init_SVs:
        SV_longitudinalDistance = SV.longitudinalDistance
        SV_MSIDs = SV.MSIDs
        SV_requestRVs = list()  # 记录附近的请求车辆
        # 范围内是否有请求
        for RV in update_RVs:
            length = abs(SV_longitudinalDistance - RV.longitudinalDistance)
            if length >= args_parser().Comm_distance:  # 过滤通信范围
                continue
            # 获得请求的首个微服务，需要从此微服务进入
            requestMSID = RV.Request_MSIDs[0]
            if requestMSID not in SV_MSIDs:  # 过滤不符合条件
                continue
            # 过滤请求已经处理的车辆
            if RV.success:
                continue
            SV_requestRVs.append(RV)

        #没有该服务车辆没有接收到请求
        if len(SV_requestRVs) == 0:  # 没有车辆处理该请求，下一辆车
            continue

        # 获得邻居服务车辆
        neighbor_SVs = [neighbor_SV for neighbor_SV in init_SVs if
                        (abs(neighbor_SV.longitudinalDistance - SV_longitudinalDistance) <= args_parser().Comm_distance)]

        # 构建选择概率模型
        w_1 = args_parser().Swarm_GAP_w[0]
        w_2 = args_parser().Swarm_GAP_w[1]
        w_3 = args_parser().Swarm_GAP_w[2]
        w_4 = args_parser().Swarm_GAP_w[3]

        Select_Max_Ps_dict = {}
        for requestRV in SV_requestRVs:
            cooperate_SVs = list()
            cooperate_SVs.append(SV)
            cooperate_SVs.extend(neighbor_SVs)
            if not util.check_MSs_in_neighbor_SVs(requestRV.Request_MSIDs, cooperate_SVs):
                continue
            # 计算阈值
            Strength = w_1 * (requestRV.waitingtime) + w_2 * (1/requestRV.Request_urgency) + w_3 * (args_parser().Comm_distance - abs(SV_longitudinalDistance - requestRV.longitudinalDistance))
            Theta = SV.get_theta(requestRV.requestID)
            # 计算请求刺激
            Select_P = (Strength**args_parser().Swarm_GAP_n) / ((Theta**args_parser().Swarm_GAP_n) + (Strength**args_parser().Swarm_GAP_n))
            Select_Max_Ps_dict[requestRV.vehicleID] = Select_P
        if len(Select_Max_Ps_dict) == 0:  # 车辆不处理该请求
            continue
        else:
            Select_requestRVID = util.roulette_wheel_selection(Select_Max_Ps_dict)
            select_RV = [RV for RV in SV_requestRVs if RV.vehicleID == Select_requestRVID][0]
            solution_dict[Select_requestRVID] = SV.vehicleID
            select_RV.success = True

            #阈值更新
            req_time, comm_time = TV.get_one_req_comm_time(select_RV, init_SVs, SV.vehicleID)
            k2 = (select_RV.deadline - req_time)/select_RV.deadline
            # SV.index_theta_dict[select_RV.requestID] = SV.get_theta(select_RV.requestID) - (w_4 * k2)
            SV.index_theta_dict[select_RV.requestID] = (SV.get_theta(select_RV.requestID) + (args_parser().initTheta - (w_4 * k2)))/2
    return solution_dict, update_RVs

# 请求调度策略 solution_map (请求车辆id,服务车id)
def get_request_routing_policy(t,init_RVs,init_SVs):
    # 随机路由
    data = []
    solution_dict_ro, update_RVs_ro = RSU_Only(t, init_RVs, init_SVs)
    data.append(("RSUs_Only", solution_dict_ro, update_RVs_ro))

    solution_dict_rr, update_RVs_rr = Random_Route(t, init_RVs, init_SVs)
    data.append(("Random_Route", solution_dict_rr, update_RVs_rr))
    # 距离优先路由：服务车辆优先选择距离自己进的服务
    solution_dict_distance, update_RVs_distance = Distance_prioritize(t, init_RVs, init_SVs)
    data.append(("Distance_prioritize", solution_dict_distance, update_RVs_distance))
    # 智能体间不通讯：智能体独立决策
    solution_dict_swarm, update_RVs_swarm = Swarm_GAP_NoComm(t,init_RVs,init_SVs)
    data.append(("Swarm_GAP_NoComm", solution_dict_swarm, update_RVs_swarm))
    # 智能体共享决策：智能体相互辅助决策
    solution_dict_swarm_Comm, update_RVs_swarm_Comm = Swarm_GAP_Comm(t, init_RVs, init_SVs)
    data.append(("Swarm_GAP_Comm", solution_dict_swarm_Comm, update_RVs_swarm_Comm))

    # solution_dict_swarm_Comm, update_RVs_swarm_Comm = Swarm_GAP_RouletteComm(t, init_RVs, init_SVs)
    # data.append(("Swarm_GAP_Comm", solution_dict_swarm_Comm, update_RVs_swarm_Comm))
    return data