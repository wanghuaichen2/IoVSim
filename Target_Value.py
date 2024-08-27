import random

from Param_Config import args_parser
random.seed(args_parser().seed)
import Util as util



def get_average_response_time(init_RVs,init_SVs,solution_dict):

    sum_req_time = 0  # updata_time + cal_time
    sum_comm_time = 0

    SV_failure_count = 0

    for RV in init_RVs:

        updata_time = 0
        cal_time = 0
        comm_time = 0

        if RV.success == False:
            # RSU处理的   KB * 8 * 10**3 = 比特   ; Mbps * 10**6 = 比特/s
            updata_time = (RV.updata * 8 * 10**3)/(util.get_bandwidth_bylongitudinalDistance(args_parser().RSU_distance) * 10**6)
            cal_time = 0 # 忽略不计
        else:
            SVID = solution_dict[RV.vehicleID]
            SV = [SV for SV in init_SVs if SV.vehicleID == SVID][0]
            req_MSIDs = RV.Request_MSIDs  # 获取请求包含的微服务集合
            cooperate_SVs = list()

            updata_time = (RV.updata  * 8 * 10**3) / (util.get_bandwidth_bylongitudinalDistance(
                abs(SV.longitudinalDistance - RV.longitudinalDistance))* 10**6)
            # 单个服务车辆是否可以处理完成
            if set(req_MSIDs).issubset(set(SV.MSIDs)):
                cooperate_SVs.append(SV)
                cal_time, comm_time = util.Calculating_MS_processing_time(RV, cooperate_SVs)


            else:  # 查看与邻居车辆合作是否可以处理
                neighbor_SVs = [neighbor_SV for neighbor_SV in init_SVs if
                                (abs(neighbor_SV.longitudinalDistance - SV.longitudinalDistance) <= args_parser().Comm_distance)]
                cooperate_SVs.append(SV)
                cooperate_SVs.extend(neighbor_SVs)
                if util.check_MSs_in_neighbor_SVs(req_MSIDs, cooperate_SVs):
                    cal_time, comm_time = util.Calculating_MS_processing_time(RV, cooperate_SVs)
                else:
                    # 没有邻居车辆可以处理，处理失败，RSU处理请求
                    cal_time = 0
                    # req_time 记录RV与SV
                    updata_time += (RV.updata * 8 * 10**3) / (util.get_bandwidth_bylongitudinalDistance(args_parser().RSU_distance) * 10**6)
        if (cal_time + updata_time) >= RV.deadline:
            SV_failure_count += 1
        #等待时间+上传时间+计算时间
        sum_req_time += (RV.waitingtime + updata_time + cal_time )
        # 总请求的完成时间 sum_req_time
        sum_comm_time += comm_time
    if len(init_RVs) == 0:
        return 0, 0
    else:
        return sum_req_time/len(init_RVs), sum_comm_time, SV_failure_count

def get_one_req_comm_time(RV,init_SVs,SVID):
    comm_time = 0
    # MSs, Request_MSs, Request_callGraph, Request_urgency, MS_priority = ms_dag.get_MSs(url)
    SV = [SV for SV in init_SVs if SV.vehicleID == SVID][0]
    req_MSIDs = RV.Request_MSIDs  # 获取请求包含的微服务集合
    cooperate_SVs = list()

    updata_time = (RV.updata * 8 * 10**3) / (util.get_bandwidth_bylongitudinalDistance(
        abs(SV.longitudinalDistance - RV.longitudinalDistance)) * 10**6)
    # 单个服务车辆是否可以处理完成
    if set(req_MSIDs).issubset(set(SV.MSIDs)):
        cooperate_SVs.append(SV)
        cal_time, comm_time = util.Calculating_MS_processing_time(RV, cooperate_SVs)

    else:  # 查看与邻居车辆合作是否可以处理
        neighbor_SVs = [neighbor_SV for neighbor_SV in init_SVs if
                        (abs(neighbor_SV.longitudinalDistance - SV.longitudinalDistance) <= args_parser().Comm_distance)]
        cooperate_SVs.append(SV)
        cooperate_SVs.extend(neighbor_SVs)
        if util.check_MSs_in_neighbor_SVs(req_MSIDs, cooperate_SVs):
            cal_time, comm_time = util.Calculating_MS_processing_time(RV, cooperate_SVs)
        else:
            # 没有邻居车辆可以处理，处理失败，RSU处理请求
            cal_time = 0
            # req_time 记录RV与SV
            updata_time += (RV.updata * 8 * 10**3) / (util.get_bandwidth_bylongitudinalDistance(args_parser().RSU_distance) * 10**6)

    return (RV.waitingtime + updata_time + cal_time), comm_time