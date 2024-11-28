该项目模拟生成车辆协同计算环境，并在该环境下实现微服务部署和请求路由，后续详细说明陆续更新...

- Vehicle.py
  - 定义了"请求车辆"、"机会车辆"和"服务车辆"类，实现了get_XXX方法实现对象的定义，属性赋值。
- MS_DAG.py
  - 定义了"微服务"和"微服务容器"类，实现功能：从DAG_config.json中获得微服务调用图、调用率等信息。
- Util.py
  - 定义仿真环境运行的规则，如："更新车辆位置信息"、"计算多个服务车辆协同处理多个微服务容器的并行处理时间"等。
- Target_Value.py
  - 目标函数类，计算"请求响应时延"和"通信时间"。
- Routing_Method.py
  - 在这里编写你的请求路由方法。
  - 已经实现的方法有：
    - Random_Route
    - Distance_prioritize
    - Swarm_GAP_NoComm
    - Swarm_GAP_Comm
    - Swarm_GAP_RouletteComm
- Placement_Method.py
  - 在这里编写你的服务放置方法。
  - 已经实现的方法有：
    - RLS
    - MSCRSPM
    - R2SP
    - GMDA
- Param_Config.py
  - 存放仿真环境的配置参数。
- Main_XXX.py
  - 模拟仿真环境的执行过程
  - Main.py：实现车辆协同环境下服务部署和请求路由过程。
  - Main_SP.py: 实现车辆协同环境下服务部署过程。
- DAG_config.json
  - 存储微服务信息。
- dataset_processing/Main_CallGraph.py
  - 处理阿里云集群跟踪数据集，获得微服务调用图，将调用图信息保存到dataset_processing/filtered_call_graph.csv。
