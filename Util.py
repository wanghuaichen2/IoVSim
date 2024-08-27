from collections import defaultdict, deque
import heapq
from tqdm import tqdm
import math
import numpy as np
import matplotlib.pyplot as plt
import random

from Param_Config import args_parser
random.seed(args_parser().seed)
np.random.seed(args_parser().seed)


# 拓扑排序算法
def topological_sort(microservice_dict,dag):
    adj_list = defaultdict(list)
    in_degree = defaultdict(int)
    for u, v in dag:
        adj_list[u].append(v)
        in_degree[v] += 1

    queue = deque([node for node in microservice_dict if in_degree[node] == 0])
    topo_order = []

    while queue:
        node = queue.popleft()
        topo_order.append(node)
        for neighbor in adj_list[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return topo_order

# 单个车辆多核并行计算
def SingleSV_calculate_parallel_processing_time(topo_order, microservice_dict, RV, SV):
    """
    计算多个微服务容器在单个服务车辆上的并行处理时间。

    :param topo_order: 微服务的拓扑顺序（DAG中的拓扑排序）
    :param microservice_dict: 微服务ID到微服务对象的映射
    :param SV: 单个服务车辆对象
    :return: 总处理时间
    """

    # 初始化每个微服务容器的核心空闲时间
    container_core_heap = {}
    for ms_id in SV.MSIDs:
        container_core_heap[ms_id] = [0] * SV.core

    task_end_time = defaultdict(int)
    total_processing_time = 0

    for ms_id in topo_order:
        ms = microservice_dict[ms_id]

        # 检查该服务车辆是否可以处理该微服务
        if ms_id not in SV.MSIDs:
            raise ValueError(f"服务车辆无法处理微服务ID: {ms_id}")

        core_heap = container_core_heap[ms_id]
        processing_time = SV.calculate_processing_time(ms.dataCalculate)

        # 分配核心
        cores_to_allocate = heapq.nsmallest(SV.core, core_heap)
        earliest_available_core = max(cores_to_allocate)
        start_time = max(earliest_available_core, task_end_time[ms_id])
        finish_time = start_time + processing_time
        total_processing_time = max(total_processing_time, finish_time)

        # 更新核心的空闲时间
        for _ in range(SV.core):
            heapq.heappushpop(core_heap, finish_time)

        # 更新所有后续节点的开始时间
        for neighbor in [v for u, v in RV.Request_callGraph if u == ms_id]:
            task_end_time[neighbor] = max(task_end_time[neighbor], finish_time)

    return total_processing_time

# 多个车辆多核并行计算
def MultipleSV_calculate_parallel_processing_time(topo_order, microservice_dict, RV, cooperate_SVs):
    """
        计算多个服务车辆协同处理多个微服务容器的并行处理时间。

        :param topo_order: 微服务的拓扑顺序（DAG中的拓扑排序）
        :param microservice_dict: 微服务ID到微服务对象的映射
        :param RV: 请求的调用图对象，存储微服务之间的依赖关系
        :param cooperate_SVs: 服务车辆列表，包含所有合作服务车辆
        :return: 总处理时间和各服务车辆之间的通信时间

       请求规则：
        1.如果该微服务没有上游微服务，则选择index=0的服务车辆处理

        2.如果该微服务有上游微服务，则该微服务首先选择上游微服务所在的服务车辆处理，
          如果该服务车辆无法处理该微服务，则先选择index=0的服务车辆，
          如果index=0的服务车辆无法处理，则选择距离最近且能处理的服务车辆。

        3.服务车辆之间的数据传输必须通过index=0的服务车辆进行中转。
        总之就是让通信时间最短，但是index=0必须首先考虑。

        """

    # 初始化所有服务车辆的核心空闲时间
    core_heaps = {sv: {ms_id: [0] * sv.core for ms_id in sv.MSIDs} for sv in cooperate_SVs}
    task_end_time = defaultdict(int)
    total_processing_time = 0
    total_communication_time = 0
    MSID_SV = {}

    for ms_id in topo_order:
        ms = microservice_dict[ms_id]

        # 获取前置微服务节点
        predecessors = [u for u, v in RV.Request_callGraph if v == ms_id]
        selected_sv = None
        processing_time = float('inf')
        start_time = float('inf')
        communication_time = 0

        if not predecessors:
            # 如果没有前置微服务，选择index=0的服务车辆处理
            selected_sv = cooperate_SVs[0]
            processing_time = selected_sv.calculate_processing_time(ms.dataCalculate)
            MSID_SV[ms_id] = selected_sv
            cores_to_allocate = heapq.nsmallest(selected_sv.core, core_heaps[selected_sv][ms_id])
            earliest_available_core = max(cores_to_allocate)
            start_time = max(earliest_available_core, task_end_time[ms_id])
        else:
            # 如果有前置微服务，选择上游微服务所在的服务车辆处理
            upstream_sv = MSID_SV.get(ms_id,None)
            if upstream_sv and ms_id in upstream_sv.MSIDs:
                selected_sv = upstream_sv
                processing_time = selected_sv.calculate_processing_time(ms.dataCalculate)
                MSID_SV[ms_id] = selected_sv
                cores_to_allocate = heapq.nsmallest(selected_sv.core, core_heaps[selected_sv][ms_id])
                earliest_available_core = max(cores_to_allocate)
                start_time = max(task_end_time[predecessors[0]], earliest_available_core)
            else:
                # 如果上游服务车辆无法处理，则尝试index=0的服务车辆
                if ms_id in cooperate_SVs[0].MSIDs:
                    selected_sv = cooperate_SVs[0]
                    processing_time = selected_sv.calculate_processing_time(ms.dataCalculate)
                    MSID_SV[ms_id] = selected_sv
                    cores_to_allocate = heapq.nsmallest(selected_sv.core, core_heaps[selected_sv][ms_id])
                    earliest_available_core = max(cores_to_allocate)
                    start_time = max(task_end_time[predecessors[0]], earliest_available_core)
                else:
                    # 如果index=0的服务车辆也无法处理，选择距离最近且能处理的服务车辆
                    min_start_time = float('inf')
                    for sv in cooperate_SVs[1:]:
                        if ms_id in sv.MSIDs:
                            cores_to_allocate = heapq.nsmallest(sv.core, core_heaps[sv][ms_id])
                            earliest_available_core = max(cores_to_allocate)
                            candidate_start_time = max(task_end_time[predecessors[0]], earliest_available_core)
                            # 计算双段通信时间 (上游到index=0，再到选定的服务车辆)
                            if sv != cooperate_SVs[0]:
                                # 上游到index=0
                                longitudinalDistance_upstream_to_0 = abs(
                                    sv.longitudinalDistance - cooperate_SVs[0].longitudinalDistance)
                                ra_upstream_to_0 = get_bandwidth_bylongitudinalDistance(
                                    longitudinalDistance_upstream_to_0)
                                transfer_time_upstream_to_0 = (ms.dataTransferred * 8 * 10**3) / (ra_upstream_to_0 * 10**6)

                                # index=0到选定的服务车辆
                                longitudinalDistance_0_to_sv = abs(
                                    cooperate_SVs[0].longitudinalDistance - sv.longitudinalDistance)
                                ra_0_to_sv = get_bandwidth_bylongitudinalDistance(longitudinalDistance_0_to_sv)
                                transfer_time_0_to_sv = (ms.dataTransferred * 8 * 10**3) / (ra_0_to_sv * 10**6)

                                # 总通信时间
                                communication_time = transfer_time_upstream_to_0 + transfer_time_0_to_sv
                                candidate_start_time += communication_time

                            if candidate_start_time < min_start_time:
                                min_start_time = candidate_start_time
                                selected_sv = sv
                                processing_time = selected_sv.calculate_processing_time(ms.dataCalculate)
                                MSID_SV[ms_id] = selected_sv
                                start_time = candidate_start_time
                                total_communication_time += communication_time

        # 计算完成时间
        finish_time = start_time + processing_time
        total_processing_time = max(total_processing_time, finish_time)

        # 更新核心的空闲时间
        for _ in range(selected_sv.core):
            heapq.heappushpop(core_heaps[selected_sv][ms_id], finish_time)

        # 更新当前节点的结束时间
        task_end_time[ms_id] = finish_time

    return total_processing_time, total_communication_time


#计算总的处理时间（处理+通信）和 额外通信时间 total_comm_time
def Calculating_MS_processing_time(RV, cooperate_SVs):
    # 创建一个字典来存储微服务的ID到对象的映射
    microservices = RV.Request_MSs
    microservice_dict = {ms.MSID: ms for ms in microservices}
    # 获取拓扑排序的顺序
    topo_order = topological_sort(microservice_dict, RV.Request_callGraph)
    total_comm_time = 0
    if len(cooperate_SVs) == 1:
        total_processing_time = SingleSV_calculate_parallel_processing_time(
            topo_order, microservice_dict, RV, cooperate_SVs[0])
    else:
        total_processing_time, total_comm_time = MultipleSV_calculate_parallel_processing_time(
            topo_order, microservice_dict, RV, cooperate_SVs)

    return total_processing_time, total_comm_time

#更新车辆位置信息
def Update_vehicle_location_information(init_SVs):
    # 使用列表推导式过滤出车辆行驶距离 > 350m的对象
    filtered_SVs = [SV for SV in init_SVs if SV.longitudinalDistance < args_parser().Road_length]
    init_SVs = filtered_SVs
    # 更新车辆位置信息
    for SV in tqdm(init_SVs, desc='Service Vehicle Updating', leave=False):
        # 更新车辆位置: 时间乘以车辆行驶速度，
        SV.longitudinalDistance += (SV.speed * 1)
        # 更新速度: 初始速度加上加速度乘以时间
        SV.speed += (SV.acceleration * 1)

        if SV.speed < 0:
            SV.speed = 0

        # 更新加速度: 随机
        if SV.speed == 0:
            SV.acceleration = random.uniform(0, args_parser().acceleration[1])
        else:
            SV.acceleration = random.uniform(args_parser().acceleration[0], args_parser().acceleration[1])  # (m/s^2)
    return init_SVs

def get_bandwidth_bylongitudinalDistance(distance):
    B = args_parser().B  # (MHz)
    RSU_B = args_parser().RSU_B
    SNR = args_parser().SNR  # (S/N 100)
    if distance < 100:
        if distance < 50:
            return (B + 1) * math.log((1 + SNR), 2)
        else:
            return B * math.log((1 + SNR), 2)
    if distance >= 100:
        return RSU_B * math.log((1 + SNR), 2)

def get_RSU_calculate_processing_time(dataCalculate):
    # 根据公式计算处理时间
    return ((dataCalculate * args_parser().RSU_I) / (args_parser().RSU_f * args_parser().RSU_IPC * args_parser().core * args_parser().RSU_E_parallel)) * 1024 * 10 ** -9

def check_MSs_in_neighbor_SVs(req_MSIDs, cooperate_SVs):
    for MSID in req_MSIDs:
        found = False
        for SV in cooperate_SVs:
            if MSID in SV.MSIDs:
                found = True
                break
        if not found:
            return False
    return True

#轮盘赌
def roulette_wheel_selection(Select_Max_Ps_dict):
    total_sum = sum(Select_Max_Ps_dict.values())
    r = random.uniform(0, total_sum)
    cumulative_sum = 0

    for key, probability in Select_Max_Ps_dict.items():
        cumulative_sum += probability
        if r < cumulative_sum:
            return key


def get_OVNum_poisson_plt(lambda_value,results):
    # 统计每个数值的出现次数
    counts = np.bincount(results)
    values = np.arange(len(counts))

    # 绘制直方图
    plt.bar(values, counts, alpha=0.75, edgecolor='black')
    plt.title('Histogram of Poisson Distributed Numbers (λ={})'.format(lambda_value))
    plt.xlabel('Number of Events')
    plt.ylabel('Frequency')
    plt.xticks(values)  # 确保 x 轴标签与值匹配
    plt.grid(True)
    plt.show()



