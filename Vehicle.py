import random
import uuid

from Param_Config import args_parser
random.seed(args_parser().seed)
import MS_DAG as ms_dag

# Request Vehicle (RV); 2.Opportunity Vehicle (OV); 3.Service Vehicles (SV);

class RV:
    def __init__(self, vehicleID, longitudinalDistance, speed, acceleration, updata):
        self.vehicleID = vehicleID

        self.longitudinalDistance = longitudinalDistance
        self.speed = speed
        self.acceleration = acceleration
        # 上传数据量
        self.updata = updata
        # Request List
        self.requestID = -1
        # Request MSs
        self.Request_MSs = list()
        self.Request_MSIDs = list()
        self.Request_urgency = 0
        self.Request_callGraph = list()
        #记录请求发送时间
        self.timestamp = -1
        #请求已经被处理
        self.success = False
        #请求截止期限
        self.deadline = 0
        #请求排队时间
        self.waitingtime = 0




    def __repr__(self):
        return f"RV(vehicleID={self.vehicleID}, longitudinalDistance={self.longitudinalDistance}, speed={self.speed}, acceleration={self.acceleration})"

class OV:
    def __init__(self, vehicleID, longitudinalDistance, speed, acceleration, max_core, max_memory, max_storage):
        self.vehicleID = vehicleID
        self.longitudinalDistance = longitudinalDistance
        self.speed = speed
        self.acceleration = acceleration
        # Core、storage、memory
        self.max_core = max_core
        self.max_memory = max_memory
        self.max_storage = max_storage

    def __repr__(self):
        return f"OV(vehicleID={self.vehicleID}, longitudinalDistance={self.longitudinalDistance}, speed={self.speed}, acceleration={self.acceleration})"

# Deploy a collection of microservices
class SV:
    def __init__(self, vehicleID, longitudinalDistance, speed, acceleration, core, memory, storage, MSIDs,  initTheta):
        self.vehicleID = vehicleID
        self.longitudinalDistance = longitudinalDistance
        self.speed = speed
        self.acceleration = acceleration

        # Core、storage、memory
        self.core = core #分配给每个微服务容器的核心数
        self.memory = memory
        self.storage = storage

        self.I = args_parser().I  # 每字节指令数
        self.f = args_parser().f  # 时钟频率（GHz）
        self.IPC = args_parser().IPC # 指令周期
        self.E_parallel = args_parser().E_parallel # 并行效率

        # Deploy microservices list
        self.MSIDs = MSIDs
        # 任务选择参数
        self.index_theta_dict = dict()
        self.initTheta = initTheta

    def get_theta(self, index):
        if index in self.index_theta_dict:
            return self.index_theta_dict[index]
        else:
            self.index_theta_dict[index] = self.initTheta
            return self.index_theta_dict[index]

    def calculate_processing_time(self, dataCalculate):
        # 根据公式计算处理时间
        return ((dataCalculate * self.I) / (self.f * self.IPC * self.core * self.E_parallel)) * 1024 * 10 ** -9

    def __repr__(self):
        return f"sV(vehicleID={self.vehicleID}, longitudinalDistance={self.longitudinalDistance}, speed={self.speed}, acceleration={self.acceleration})"

def get_RVs(num):
    RVs = list()
    for index in range(num):

        vehicleID = index
        longitudinalDistance = random.uniform(0, args_parser().Road_length)    #(0-350m)
        speed = random.uniform(args_parser().speed[0], args_parser().speed[1]) #(m/s)
        acceleration = random.uniform(args_parser().acceleration[0], args_parser().acceleration[1]) # (m/s^2)
        updata = random.randint(args_parser().updata[0],args_parser().updata[1])
        RVs.append(RV(vehicleID, longitudinalDistance, speed, acceleration, updata))
    return RVs


def get_OVs(num):
    OVs = list()
    for index in range(num):

        vehicleID = uuid.uuid1()
        longitudinalDistance = 0    #(m)
        speed = random.uniform(args_parser().speed[0], args_parser().speed[1])                   #(m/s)
        acceleration = random.uniform(args_parser().acceleration[0], args_parser().acceleration[1]) # (m/s^2)

        # Core、storage、memory
        max_core = random.randint(args_parser().max_core[0], args_parser().max_core[1])
        max_memory = random.randint(args_parser().max_memory[0], args_parser().max_memory[1])
        max_storage = random.randint(args_parser().max_storage[0], args_parser().max_storage[1])

        OVs.append(OV(vehicleID, longitudinalDistance, speed, acceleration, max_core, max_memory, max_storage))
    return OVs

def get_SVs(num):
    SVs = list()
    for index in range(num):

        vehicleID = uuid.uuid1()
        longitudinalDistance = random.uniform(0, args_parser().Road_length)    #(m)
        speed = random.uniform(args_parser().speed[0], args_parser().speed[1])    #(m/s)
        acceleration = random.uniform(args_parser().acceleration[0], args_parser().acceleration[1])  # (m/s^2)
        # microservices list
        MSID_list, MS_callRate = ms_dag.get_All_MSs_call_data(args_parser().config_url)
        MS_Num = random.randint(1, len(MSID_list))
        MSIDList = random.sample(MSID_list, MS_Num)

        core = random.randint(args_parser().core[0], args_parser().core[1])
        memory = random.randint(args_parser().memory[0], args_parser().memory[1])
        storage = random.randint(args_parser().storage[0], args_parser().storage[1])

        # 任务选择参数
        initTheta = args_parser().initTheta
        SVs.append(SV(vehicleID, longitudinalDistance, speed, acceleration, core, memory, storage,  MSIDList, initTheta))
    return SVs