from graph_generator import generate_random_firefighter_graph_data, draw_graph
from firefighter_pulp import solve_firefighter_PULP
from firefighter_minizinc import solve_firefighter_MINIZINC
from helper import run_function_with_timeout
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import time

class ExecutedGraphData():
    def __init__(self, graph_data, execution_time, status, result, algorithm):
        self.graph_data = graph_data
        self.graph_type = graph_data["type"]
        self.execution_time = execution_time
        self.status = status
        self.result = result
        self.algorithm = algorithm
    
    def draw_graph(self):
        draw_graph(*self.graph_data["draw_graph_params"])
    
    def __str__(self):
        return f"execution_time={self.execution_time}, status={self.status}"

    def __repr__(self):
        return f"execution_time={self.execution_time}, status={self.status}"

##METHODS THAT CAN BE USED ON THE LISTS OF ExecutedGraphData instances
def average_execution_time(rundata: list[ExecutedGraphData]) -> float:  # consider also status timeout
    return round(sum([data.execution_time for data in rundata]) / len(rundata), 5)

def graph_data_from_list(*run_datas: list[ExecutedGraphData]) -> dict:
    run_datas = [i for i in run_datas if i]  # remove empty lists (if any)
    if not run_datas:
        return {}
    
    first_run_data = run_datas[0]
    type_to_data = {}
    for i, obj in enumerate(first_run_data):
        graph_type = obj.graph_type
        if graph_type not in type_to_data:
            type_to_data[obj.graph_type] = []
        
        all_times = [run_data[i].execution_time for run_data in run_datas]
        type_to_data[obj.graph_type].append(tuple(all_times))
    return type_to_data

class Pipeline():
    def __init__(self, n_nodes_range, n_runs, timeout):
        self.n_nodes_range = n_nodes_range
        self.n_runs = n_runs
        self.timeout = timeout
        self.run_data = {}
        self.graphs = [generate_random_firefighter_graph_data(self.n_nodes_range) for _ in range(self.n_runs)]
        print(f"Instantiating pipeline and generating {self.n_runs} graphs for the first time...")
    
    @property
    def get_algs(self):
        return list(self.run_data.keys())
    
    @property
    def previously_run_alg(self):
        return self.get_algs[-1] if self.get_algs else None

    def run(self, alg):
        print(f"Running pipeline for {alg}...")
        for graph in self.graphs:
            populate_data = graph["solver_data"]
            data = {}
            if alg == "pulp":
                data = run_function_with_timeout(self.timeout, "pulp", solve_firefighter_PULP, **populate_data)
            elif alg == "minizinc":
                data = run_function_with_timeout(self.timeout, "minizinc", solve_firefighter_MINIZINC, **populate_data)
            else:
                raise Exception("Invalid algorithm. Please choose from: {}".format(self.algs))
            
            if not data:
                data = {"execution_time": self.timeout*1000, "status": "timeout", "result": None}
            
            if alg not in self.run_data:
                self.run_data[alg] = []
            self.run_data[alg].append(ExecutedGraphData(graph, **data, algorithm=alg))

    def get_rundata_for_alg(self, alg=None):
        alg = alg if alg else self.previously_run_alg
        return self.run_data[alg] if alg else None
    
    def get_present_algs(self):
        return [alg for alg in self.run_data if alg in self.run_data]
    
    @property
    def get_nonempty_rundatas(self):
        return {k:v for k,v in self.run_data.items() if v}
    
    def generate_graph(self):  # inspiration from https://stackoverflow.com/questions/21654635/scatter-plots-in-pandas-pyplot-how-to-plot-by-category
        if not self.run_data:
            raise Exception("No data to generate graph. Please run pipeline first.")

        non_empty_rundatas = self.get_nonempty_rundatas

        graph_data = graph_data_from_list(*non_empty_rundatas.values())
        total_readings = sum([len(objs) for objs in graph_data.values()])

        start_frame = np.zeros((total_readings, len(non_empty_rundatas)))
        
        graph_types = []
        index = 0
        graph_type_to_quantity_map = {"":""} 
        for graph_type, objs in graph_data.items():
            graph_types.extend([graph_type] * len(objs))
            graph_type_to_quantity_map[graph_type] = len(objs)
            for times in objs:
                start_frame[index] = [t for t in times]
                index += 1
        
        data = pd.DataFrame(
            start_frame,
            index=range(total_readings),
            columns=tuple(non_empty_rundatas.keys()),
        )
        data["type"] = graph_types
        
        f, ax = plt.subplots(figsize=(7, 7))
        if len(non_empty_rundatas) == 1:
            ax.set(xscale="log", xlabel=f"{self.get_algs[0].title()} search time", ylabel="type")
            sns.barplot(x=self.get_algs[0], y="type", data=data, ax=ax)
        else:
            ax.set(xscale="log", yscale="log", xlabel=f"{self.get_algs[0].title()} search time", ylabel=f"{self.get_algs[1].title()} search time")
            sns.scatterplot(x=self.get_algs[0], y=self.get_algs[1], data=data, hue="type", ax=ax, s=25)

        intervals = [1, 10, 100, 1000, 10000] #up to 10 seconds
        ax.set_xticks(intervals)
        ax.set_xlim(left=1, right=11000)
        if len(non_empty_rundatas) > 1:
            ax.set_ylim(bottom=1, top=11000)
            ax.set_yticks(intervals)
        
        def format_func(value, tick_number):
            if value == 1:
                return "0"
            elif value <= 100:
                return f"{value}ms"
            else:
                return f"{int(value/1000)}s"

        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_func))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_func))

        ax.legend(loc='upper left', ncol=1, title="Graph variant", title_fontsize=12, fontsize=10, frameon=True, shadow=True, fancybox=True)
        plt.show()
    
    def print_result_tuples(self):
        graph_data = graph_data_from_list(*self.get_nonempty_rundatas.values())
        print(graph_data)

pipeline = Pipeline(n_nodes_range=(25, 100), n_runs=200, timeout=10)
pipeline.run("minizinc")
pipeline.run("pulp")
pipeline.generate_graph()