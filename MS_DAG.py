import copy
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
import random

from Param_Config import args_parser
random.seed(args_parser().seed)

class MSContainer:
    def __init__(self, MSID, limit_core,  limit_memory, limit_storage,callRate):
        self.MSID = MSID
        # 最大 Core、memory、storage、不能超过这个上线。
        self.limit_core = limit_core
        self.limit_memory = limit_memory
        self.limit_storage = limit_storage
        self.callRate = callRate

class MS:
    def __init__(self, MSID, dataCalculate , dataTransferred):
        self.MSID = MSID
        self.dataCalculate = dataCalculate
        self.dataTransferred = dataTransferred



# Visualize the directed acyclic graph of all call requests
def Generate_Request_callGraph(dag):

    # Check if the graph is a directed acyclic graph
    is_dag = nx.is_directed_acyclic_graph(dag)
    # print("Is the graph a DAG?", is_dag)

    # Using hierarchical layout to draw graphics
    def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
        pos = _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)
        return pos
    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None, parsed=[]):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap, vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                     pos=pos, parent=root, parsed=parsed)
        return pos

    # Find the root node of the DAG (the node with in-degree 0)
    roots = [node for node in dag.nodes() if dag.in_degree(node) == 0]

    # If there are multiple root nodes, take the first one
    if roots:
        root = roots[0]
    else:
        root = None

    # Get the position of the hierarchical layout
    pos = hierarchy_pos(dag, root)

    # Drawing a shape
    plt.figure(figsize=(10, 6))
    nx.draw(dag, pos, with_labels=True, node_size=700, node_color='lightblue', arrowsize=20)
    plt.show()

def Generate_AllRequest_callGraph(Request_MSs,Request_callGraph):
    for index in tqdm(range(len(Request_callGraph)), desc='Directed acyclic graph checking', leave=False):
        dag = nx.DiGraph()
        dag.add_nodes_from(Request_MSs[index])
        dag.add_edges_from(Request_callGraph[index])
        Generate_Request_callGraph(dag)
    print("No abnormal directed acyclic graph!")



def get_MSs(Request_MS_list):
    MSs = list()
    for index in Request_MS_list:
        MSID = index
        dataCalculate = random.randint(args_parser().dataCalculate[0], args_parser().dataCalculate[1])
        dataTransferred = random.randint(args_parser().dataTransferred[0], args_parser().dataTransferred[1])

        ms = MS(MSID=MSID, dataCalculate=dataCalculate,
                dataTransferred=dataTransferred)
        MSs.append(ms)
    return copy.deepcopy(MSs)

def get_MSContainers(num):
    MSContainers = list()
    for index in range(num):
        MSID = index
        limit_core = random.randint(args_parser().limit_core[0], args_parser().limit_core[1])
        limit_storage = random.randint(args_parser().limit_storage[0], args_parser().limit_storage[1])
        limit_memory = random.randint(args_parser().limit_memory[0], args_parser().limit_memory[1])
        callRate = random.random()
        mscontainer = MSContainer(MSID=MSID, limit_core=limit_core, limit_storage=limit_storage, limit_memory=limit_memory, callRate=callRate)

        MSContainers.append(mscontainer)
    return MSContainers

def get_All_MSs_architecture_data(url):
    with open(url, 'r') as file:
        config = json.load(file)

    # Request call graph
    Request_MSIDs_List = config['Request_MSIDs_List']
    Request_callGraph = config['Request_callGraph']
    Request_urgency = config['Request_urgency']

    # Visualize the directed acyclic graph of all call requests
    # Generate_AllRequest_callGraph(Request_MSs, Request_callGraph)

    return Request_MSIDs_List, Request_callGraph, Request_urgency

def get_All_MSs_call_data(url):
    with open(url, 'r') as file:
        config = json.load(file)

    MSID_list = config['MSID_list']
    MS_callRate = config['MS_callRate']

    return MSID_list, MS_callRate


