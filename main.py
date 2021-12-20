# id唯一标识一个节点，index则体现变量的顺序
from queue import Queue
from graphviz import Digraph
from boolexp import *


class Vertex:
    def __init__(self):
        self.low = None
        self.high = None
        self.index = ''
        self.value = ''
        self.id = ''
        self.mark = ''
        # self.count = ''


class AND:
    def __init__(self, exp1, exp2):
        self.type = 'AND'
        self.exp1 = exp1
        self.exp2 = exp2


class OR:
    def __init__(self, exp1, exp2):
        self.type = 'OR'
        self.exp1 = exp1
        self.exp2 = exp2


class NOT:
    def __init__(self, exp1):
        self.type = 'NOT'
        self.exp1 = exp1


class Variable:
    def __init__(self, name):
        self.type = 'Variable'
        self.name = name
        self.index = int(name[1:])


"(x1 and x2) or (x3 and x4) or (x5 and x6)"
exp = OR(OR(AND(Variable('x1'), Variable('x2')), AND(Variable('x3'), Variable('x4'))),
         AND(Variable('x5'), Variable('x6')))


def get_vertex_list(var_list):
    v_count = 1
    vertex_list = {}
    max_index = -1
    for var in var_list:
        if var.index > max_index:
            max_index = var.index
    for var in var_list:
        v1 = Vertex()
        v2 = Vertex()
        v1.value = 0
        v2.value = 1
        v1.index = max_index + 1
        v2.index = max_index + 1
        v_vertex = Vertex()
        v_vertex.low = v1
        v_vertex.high = v2
        v_vertex.index = var.index
        v_count += 1
        traverse(v_vertex, 1)
        vertex_list[v_vertex.index] = v_vertex

    return vertex_list, max_index


def copy_vertex(v):
    res = Vertex()
    res.low = v.low
    res.high = v.high
    res.index = v.index
    res.value = v.value
    res.id = v.id
    res.mark = v.mark
    return res


# print(exp)
def deal_exp(exp, vertex_list, max_index):
    if exp.type == 'Variable':
        return copy_vertex(vertex_list[exp.index])
    if exp.type == 'AND' or exp.type == 'OR':
        e1_vertex = deal_exp(exp.exp1, vertex_list, max_index)
        e2_vertex = deal_exp(exp.exp2, vertex_list, max_index)
        vv = apply_step(e1_vertex, e2_vertex, exp.type, max_index)
        traverse(vv, 1)
        vvv = reduce(vv, max_index)
        return vvv
    if exp.type == 'NOT':
        e1_vertex = deal_exp(exp.exp1, vertex_list, max_index)
        # traverse(e1_vertex, 1)
        deal_not(e1_vertex)
        red_v = reduce(e1_vertex, max_index)
        return red_v


# n = 2


def deal_not(v):
    bfs = Queue()
    bfs.put(v)
    flag_set = set()
    while not bfs.empty():
        u= bfs.get()
        if u.value == 1 or u.value == 0:
            continue
        if u.low.value == 0 or u.low.value == 1:
            low = copy_vertex(u.low)
            low.value = 1 - low.value
            u.low = low

        if u.high.value == 0 or u.high.value == 1:
            high = copy_vertex(u.high)
            high.value = 1 - high.value
            u.high = high

        flag_set.add(u.id)
        if u.low is not None and (u.low.id not in flag_set):
            bfs.put(u.low)
        if u.high is not None and (u.high.id not in flag_set):
            bfs.put(u.high)


def apply_step(v1, v2, op, max_index):
    T = {}
    str_id = ''
    if v1 is not None:
        str_id += str(v1.id)
    if v2 is not None:
        str_id += str(v2.id)
    u = T.get(str_id, None)
    if u is not None:
        return u
    u = Vertex()
    u.mark = False
    T[str_id] = u
    u.value = evaluate(v1.value, v2.value, op)
    if not (u.value == -1):
        u.index = max_index + 1
        u.low = None
        u.high = None
    else:

        u.index = min(v1.index, v2.index)

        if v1.index == u.index:
            vlow1 = v1.low
            vhigh1 = v1.high
        else:
            vlow1 = v1
            vhigh1 = v1
        if v2.index == u.index:
            vlow2 = v2.low
            vhigh2 = v2.high
        else:
            vlow2 = v2
            vhigh2 = v2
        u.low = apply_step(vlow1, vlow2, op, max_index)
        u.high = apply_step(vhigh1, vhigh2, op, max_index)
    return u


def traverse(v, cid):
    v.mark = True
    if v.low is not None and not v.low.mark:
        cid = traverse(v.low, cid)
    if v.high is not None and not v.high.mark:
        cid = traverse(v.high, cid)
    v.id = cid
    return cid + 1


def reduce(v, max_index):
    vlist = [list() for i in range(max_index + 2)]
    subgraph = {}
    bfs = Queue()
    bfs.put(v)
    flag_set = set()

    while not bfs.empty():
        u = bfs.get()
        flag_set.add(u.id)
        vlist[u.index].append(u)
        if u.low is not None:
            bfs.put(u.low)
        if u.high is not None:
            bfs.put(u.high)
    nextid = 0
    index_list = list(range(max_index + 2))[1:]
    index_list.reverse()
    for i in index_list:
        Q = {}
        q1 = []
        for u in vlist[i]:
            if u.index == max_index + 1:
                Q[str(u.value)] = u
                q1.append((u.value, u))
                # u.id = u.value + 1
            elif u.low.id == u.high.id:
                u.id = u.low.id
            else:
                q1.append((str(u.low.id * (v.id + 1)) + str(u.high.id), u))
                Q[str(u.low.id * (v.id + 1)) + str(u.high.id)] = u
        old_key = '-1'
        s_keys = sorted(Q.keys())
        q1.sort(key=lambda e: e[0])
        for key, u in q1:
            if key == old_key:
                u.id = nextid
            else:
                nextid += 1
                u.id = nextid
                subgraph[str(nextid)] = u
                if u.low is not None:
                    u.low = subgraph.get(str(u.low.id), None)
                if u.high is not None:
                    u.high = subgraph.get(str(u.high.id), None)
                old_key = key

        # for key in s_keys:
        #     u = Q.get(key)
        #     if key == old_key:
        #         u.id = nextid
        #     else:
        #         nextid += 1
        #         u.id = nextid
        #         subgraph[str(nextid)] = u
        #         if u.low is not None:
        #             if u.low.value == 0:
        #                 u.low = subgraph['1']
        #             elif u.low.value == 1:
        #                 u.low = subgraph['2']
        #             else:
        #                 u.low = subgraph.get(str(u.low.id), None)
        #         if u.high is not None:
        #             if u.high.value == 0:
        #                 u.high = subgraph['1']
        #             elif u.high.value == 1:
        #                 u.high = subgraph['2']
        #             else:
        #                 u.high = subgraph.get(str(u.high.id), None)
        #         old_key = key
    return subgraph[str(v.id)]


def evaluate(a, b, op):
    if op == 'AND':
        if a == 0 or b == 0:
            return 0
        elif a == 1 and b == 1:
            return 1
        return -1
    elif op == 'OR':
        if a == 1 or b == 1:
            return 1
        elif a == 0 and b == 0:
            return 0
        return -1


def draw(v):
    f = Digraph('finite_state_machine', filename='fsm.gv')
    bfs = Queue()
    bfs.put(v)
    flag_set = set()
    edge_set = set()

    while not bfs.empty():
        u = bfs.get()
        if u.value == 0 or u.value == 1:
            f.node(str(u.value))
        else:
            f.node('x' + str(u.index) + str(u.id), 'x' + str(u.index))
        flag_set.add(u.id)
        if u.low is not None:
            bfs.put(u.low)
            if u.low.value != -1:
                f.node(str(u.low.value))
                if 'x' + str(u.index) + str(u.id) + str(u.low.value) not in edge_set:
                    f.edge('x' + str(u.index) + str(u.id), str(u.low.value), label='low')
                    edge_set.add('x' + str(u.index) + str(u.id) + str(u.low.value))
            else:
                f.node('x' + str(u.low.index) + str(u.low.id), label='x' + str(u.low.index))
                if 'x' + str(u.index) + str(u.id) + str(u.low.index) + str(u.low.id) not in edge_set:
                    f.edge('x' + str(u.index) + str(u.id), 'x' + str(u.low.index) + str(u.low.id), label='low')
                    edge_set.add('x' + str(u.index) + str(u.id) + str(u.low.index) + str(u.low.id))
        if u.high is not None:
            bfs.put(u.high)
            if u.high.value != -1:
                f.node(str(u.high.value))
                if 'x' + str(u.index) + str(u.id) + str(u.high.value) not in edge_set:
                    f.edge('x' + str(u.index) + str(u.id), str(u.high.value), label='high')
                    edge_set.add('x' + str(u.index) + str(u.id) + str(u.high.value))
            else:
                f.node('x' + str(u.index) + str(u.id), label='x' + str(u.index))
                if 'x' + str(u.index) + str(u.id) + str(u.high.index) + str(u.high.id) not in edge_set:
                    f.edge('x' + str(u.index) + str(u.id), 'x' + str(u.high.index) + str(u.high.id), label='high')
                    edge_set.add('x' + str(u.index) + str(u.id) + str(u.high.index) + str(u.high.id))
    f.view()


# var_list = [Variable('x1'), Variable('x2')]
# n = len(var_list)


def parse_suffix(exp_list):
    v_stack = []
    index_set = set()
    var_list = []
    for item in exp_list:
        # 变量
        if item[0] == 'x' or item[0] == 'X':
            index = str(int(item[1:]))
            if index not in index_set:
                index_set.add(index)
                var_list.append(Variable('x' + index))
            v_stack.append(Variable('x' + index))
        elif item[0] == '¬':
            exp1 = v_stack.pop()
            res_exp = NOT(exp1)
            v_stack.append(res_exp)
        elif item[0] == '+':
            exp1 = v_stack.pop()
            exp2 = v_stack.pop()
            res_exp = OR(exp1, exp2)
            v_stack.append(res_exp)
        elif item[0] == '*':
            exp1 = v_stack.pop()
            exp2 = v_stack.pop()
            res_exp = AND(exp1, exp2)
            v_stack.append(res_exp)
    return v_stack[0], var_list


if __name__ == "__main__":
    # ok1
    # expression = "x1*(¬x2+x3)*x4"
    # ok2
    # expression = "x1*¬x2*x3"
    # ok3
    # expression = "x1*x2+x4"
    # ok4
    # expression = "x1*x2+x3*x4+x5*x6"
    # ok5
    # expression = "x1+x2*x3+x4*x5+x6"
    # ok6
    # expression = "¬x1+(x2*¬(¬x3+x4)*¬x5+x6)"
    # ok7
    expression = "x3+(x2*¬x1)*¬x2"
    # ok8
    # expression = "(x1*x4)+(x2*x5)+(x3*x6)"
    # expression = "¬x1+(x2*¬(¬x3+x4)*(¬x5+x6))"
    # expression = "¬(x1*x3)+(x1*x2)"
    # expression = "x1*(¬x1)"
    exp = boolexp(expression)
    exp.infix2suffix()
    print(exp.suffix_exp)
    final_exp, var_list = parse_suffix(exp.suffix_exp)
    vertex_list, max_index = get_vertex_list(var_list)
    # l=NOT(OR(Variable('x1'), Variable('x2')))
    # final_exp = AND(AND(Variable('x1'), NOT(Variable('x2'))), Variable('x3'))
    res = deal_exp(final_exp, vertex_list, max_index)
    draw(res)
    print('finished!')
