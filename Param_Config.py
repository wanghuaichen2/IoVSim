import argparse

def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=1, help="随机数种子")
    parser.add_argument('--config_url', type=str, default="DAG_config.json", help="DAG配置文件路径")

    #服务放置算法
    parser.add_argument('--R2SP_w', type=list, default=[1, 1, 1], help="R2SP：W_1、W_2、w_3、W_4")


    #请求路由算法
    parser.add_argument('--initTheta', type=float, default=0.0, help="SV请求选择阈值")
    parser.add_argument('--Swarm_GAP_w', type=list, default=[1, 100, 1, 1], help="Swarm_GAP：W_1、W_2、w_3、W_4")
    parser.add_argument('--Swarm_GAP_n', type=int, default=2, help="Swarm_GAP")

    #设置 MS
    parser.add_argument('--limit_core', type=list, default=[1, 4], help="MSContainer 最小分配核心（个）")
    parser.add_argument('--limit_memory', type=list, default=[1, 2], help="MSContainer 最小分配内存（GB）")
    parser.add_argument('--limit_storage', type=list, default=[4, 16], help="MSContainer 最小分配存储（GB）")
    parser.add_argument('--dataCalculate', type=list, default=[50, 80], help="MS需要计算数据量（KB）")
    parser.add_argument('--dataTransferred', type=list, default=[10, 20], help="MS需要通信数据量（KB）")


    #设置初始化车辆
    parser.add_argument('--speed', type=list, default=[10, 20], help="初始化车辆速度m/s")
    parser.add_argument('--acceleration', type=list, default=[-0.2, 0.2], help="初始化车辆加速度m^2/s")
    # 设置 RV
    parser.add_argument('--RVNum_lambda', type=int, default=200, help="请求车辆数量服从泊松分布lambda")
    parser.add_argument('--updata', type=list, default=[50, 80], help="RV上传的数据量（KB）")

    # 设置 OV
    parser.add_argument('--OVNum_lambda', type=int, default=4, help="机会车辆数量服从泊松分布")
    parser.add_argument('--max_core', type=list, default=[32, 64], help="OV 最大核心（个）")
    parser.add_argument('--max_memory', type=list, default=[16, 32], help="OV 最大内存（GB）")
    parser.add_argument('--max_storage', type=list, default=[32, 64], help="OV 最大存储（GB）")


    # 设置 SV
    parser.add_argument('--InitSVNum', type=int, default=100, help="初始化服务车辆数量")

    parser.add_argument('--I', type=float, default=1.5, help="每字节指令数")
    parser.add_argument('--f', type=float, default=3.5, help="时钟频率（GHz）")
    parser.add_argument('--IPC', type=float, default=2.0, help="指令周期")
    parser.add_argument('--E_parallel', type=float, default=0.9, help="并行效率")

    parser.add_argument('--core', type=list, default=[1, 4], help="为每个微服务容器分配的核心数[1,4]")
    parser.add_argument('--memory', type=list, default=[1, 2], help="为每个微服务容器分配的内存(GB)")
    parser.add_argument('--storage', type=list, default=[2, 8], help="为每个微服务容器分配的存储(GB)")


    # 设置 RSU
    parser.add_argument('--RSU_B', type=float, default=10.0, help="带宽(MHz)")
    parser.add_argument('--RSU_I', type=float, default=1.5, help="每字节指令数")
    parser.add_argument('--RSU_f', type=float, default=3.5, help="时钟频率（GHz）")
    parser.add_argument('--RSU_IPC', type=float, default=2.0, help="指令周期")
    parser.add_argument('--RSU_E_parallel', type=float, default=0.9, help="并行效率")
    parser.add_argument('--RSU_distance', type=float, default=1000, help="车辆与RSU之间距离")


    # 环境参数
    parser.add_argument('--T', type=int, default=1, help="模拟环境持续时间（s）")
    parser.add_argument('--Road_length', type=int, default=1000, help="模拟环境道路长度")
    parser.add_argument('--Comm_distance', type=int, default=20, help="车辆之间通信距离")

    #网络配置
    parser.add_argument('--B', type=float, default=20.0, help="带宽(MHz)")
    parser.add_argument('--SNR', type=float, default=20.0, help="信噪比(dB)")


    # 解析参数
    args = parser.parse_args()

    return args
