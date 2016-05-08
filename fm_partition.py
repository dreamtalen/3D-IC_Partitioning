import random
import copy

def ast2graph():
    module_wire_dict = {}
    wire_weight_dict = {}
    module_list = []
    wire_list = []
    with open("test1.ast") as f:
        for line in f.readlines():
            if line:
                type, name = line.strip().split()
                if type == 'net':
                    this_net = name
                    wire_list.append(name)
                    wire_weight_dict[name] = 1
                if type == 'width':
                    if name is not '0' and this_net:
                        wire_weight_dict[this_net] = int(name) + 1
                        this_net = ''
                if type == 'module':
                    this_module = name
                    module_wire_dict[this_module] = []
                if type == 'port' and this_module:
                    module_wire_dict[this_module].append(name)
    for key, value in module_wire_dict.items():
        module_wire_dict[key] = list(set(value))
        module_list.append(key)
        # wire_list += value
    # print module_wire_dict

    # print module_list
    # wire_list = list(set(wire_list))
    # print wire_list
    # print net_list
    # print len(module_list)
    # print len(wire_list)
    # print wire_weight_dict

    wire_module_dict = {}
    for wire in wire_list:
        wire_module_dict[wire] = [module for module in module_list if wire in module_wire_dict[module]]
    # print wire_module_dict

    # module_area_dict = {module:random.randint(1,5) for module in module_list}
    module_area_dict = {}
    # print module_list
    with open("area_report_hierarchy.rpt") as f:
        for line in f.readlines():
            line = line.strip().split()
            if line:
                if line[0][10:] in module_list:
                    module_area_dict[line[0][10:]] = float(line[1])
    # print module_area_dict
    for module in module_list:
        if module not in module_area_dict.keys():
            # print module
            module_area_dict[module] = 3600

    # print module_area_dict

    # hypergraph completed
    # print sorted(module_area_dict.values(), reverse=True)
    return module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, wire_weight_dict

def three_fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict):
    low_border = 420000
    high_border = 480000
    initial_a = random.sample(module_list, len(module_list)/3)
    while not low_border < sum([module_area_dict[k] for k in initial_a]) < high_border:
        initial_a = random.sample(module_list, len(module_list)/3)
    left_module_list = list(set(module_list)-set(initial_a))
    initial_b = random.sample(left_module_list, len(left_module_list)/2)
    while not low_border < sum([module_area_dict[k] for k in initial_b]) < high_border:
        initial_b = random.sample(left_module_list, len(left_module_list)/2)
    initial_c = list(set(left_module_list)-set(initial_b))
    # print initial_a, sum(module_area_dict[k] for k in initial_a)
    # print initial_b, sum(module_area_dict[k] for k in initial_b)
    # print initial_c, sum(module_area_dict[k] for k in initial_c)
    cut_a = calculate_cut(module_wire_dict, wire_module_dict, wire_weight_dict, wire_list, initial_b, initial_a, initial_c)
    cut_b = calculate_cut(module_wire_dict, wire_module_dict, wire_weight_dict, wire_list, initial_a, initial_b, initial_c)
    cut_c = calculate_cut(module_wire_dict, wire_module_dict, wire_weight_dict, wire_list, initial_a, initial_c, initial_b)
    initial_cut = min(cut_a, cut_b, cut_c)
    print initial_cut
    module_list = initial_a+initial_b
    wire_list = []
    for module in module_list:
        wire_list += module_wire_dict[module]
    wire_list = list(set(wire_list))
    result_a, result_b, cut1 = fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict, initial_a, initial_b, low_border, high_border)
    module_list = result_b+initial_c
    wire_list = []
    for module in module_list:
        wire_list += module_wire_dict[module]
    wire_list = list(set(wire_list))
    result_b, result_c, cut2 = fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict, result_b, initial_c, low_border, high_border)
    result_cut = calculate_cut(module_wire_dict, wire_module_dict, wire_weight_dict, wire_list, result_a, result_b, result_c)
    return result_cut, result_a, result_b, result_c


def calculate_cut(module_wire_dict, wire_module_dict, wire_weight_dict, wire_list, top_module_list, middle_module_list, bottom_module_list):
    top_bottom_wire_list = [net for net in wire_list if not TE_net(net, wire_module_dict[net], top_module_list, bottom_module_list)]
    top_middle_wire_list = [net for net in wire_list if not TE_net(net, wire_module_dict[net], top_module_list, middle_module_list)]
    middle_bottom_wire_list = [net for net in wire_list if not TE_net(net, wire_module_dict[net], middle_module_list, bottom_module_list)]

    double_cost_wire_list = list(set(top_bottom_wire_list) - (set(top_middle_wire_list) | set(middle_bottom_wire_list)))
    one_cost_top_bottom_wire_list = list(set(top_bottom_wire_list) & ( (set(top_middle_wire_list) | set(middle_bottom_wire_list)) - (set(top_middle_wire_list) & set(middle_bottom_wire_list))))
    return sum(2*wire_weight_dict[net] for net in double_cost_wire_list) + sum(wire_weight_dict[net] for net in top_middle_wire_list) + sum(wire_weight_dict[net] for net in middle_bottom_wire_list) + sum(wire_weight_dict[net] for net in one_cost_top_bottom_wire_list)
    # left_module_list = initial_a[:]
    # right_module_list = initial_right[:]


def two_fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict):
    low_border = 630000
    high_border = 700000
    initial_left = random.sample(module_list, len(module_list)/2)
    while not low_border < sum([module_area_dict[k] for k in initial_left]) < high_border:
        initial_left = random.sample(module_list, len(module_list)/2)
    initial_right = [module for module in module_list if module not in initial_left]
    left_module_list, right_module_list, sum_cut = fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict, initial_left, initial_right, low_border, high_border)
    return sum_cut, left_module_list, right_module_list

def four_fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict):
    low_border = 630000
    high_border = 700000
    initial_left = random.sample(module_list, len(module_list)/2)
    while not low_border < sum([module_area_dict[k] for k in initial_left]) < high_border:
        initial_left = random.sample(module_list, len(module_list)/2)
    initial_right = [module for module in module_list if module not in initial_left]
    left_module_list, right_module_list, cut_middle = fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict, initial_left, initial_right, low_border, high_border)

    low_border = 315000
    high_border = 350000
    initial_top_left = random.sample(left_module_list, len(left_module_list)/2)
    while not low_border < sum([module_area_dict[k] for k in initial_top_left]) < high_border:
        initial_top_left = random.sample(left_module_list, len(left_module_list)/2)
    initial_top_right = [module for module in left_module_list if module not in initial_top_left]
    top_left_list, top_right_list, cut_top = fm_partition(module_wire_dict, wire_module_dict, left_module_list, wire_list, module_area_dict, factor, wire_weight_dict, initial_top_left, initial_top_right, low_border, high_border)

    initial_bottom_left = random.sample(right_module_list, len(right_module_list)/2)
    while not low_border < sum([module_area_dict[k] for k in initial_bottom_left]) < high_border:
        initial_bottom_left = random.sample(right_module_list, len(right_module_list)/2)
    initial_bottom_right = [module for module in right_module_list if module not in initial_bottom_left]
    bottom_left_list, bottom_right_list, cut_bottom = fm_partition(module_wire_dict, wire_module_dict, right_module_list, wire_list, module_area_dict, factor, wire_weight_dict, initial_bottom_left, initial_bottom_right, low_border, high_border)

    sum_cut = cut_middle + cut_top + cut_bottom
    return sum_cut, top_left_list, top_right_list, bottom_left_list, bottom_right_list

def fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict, initial_left, initial_right, low_border, high_border):
    left_module_list = initial_left[:]
    right_module_list = initial_right[:]
    locked = []
    gain_list = []
    step_list = []

    total_area = sum([module_area_dict[k] for k in left_module_list]) + sum([module_area_dict[k] for k in right_module_list])
    # low_border = factor*total_area - max(module_area_dict.values())
    # high_border = factor*total_area + max(module_area_dict.values())

    # print low_border, high_border, total_area
    # print sum([module_area_dict[k] for k in left_module_list])
    # print sum([module_area_dict[k] for k in right_module_list])

    initial_cut = sum([wire_weight_dict[net] for net in wire_list if not TE_net(net, wire_module_dict[net], left_module_list, right_module_list)])
    # print initial_cut
    # return initial_cut

    module_gain_dict = {module: FS(module, module_wire_dict, wire_module_dict, left_module_list, right_module_list,wire_weight_dict)
                                - TE(module, module_wire_dict, wire_module_dict, left_module_list, right_module_list,wire_weight_dict)
                        for module in module_list}


    while True:
        initial_gain_dict = copy.deepcopy(module_gain_dict)
        initial_left = left_module_list[:]
        initial_right = right_module_list[:]
        # print right_module_list
        while len(locked) < len(module_list):
            module_sorted = sorted(module_list, key=lambda k: module_gain_dict[k], reverse=True)
            module_chosen = ''
            for module in module_sorted:
                if module not in locked and area_constraint(module, low_border, high_border, left_module_list, module_area_dict):
                    module_chosen = module
                    break
            if not module_chosen:
                break
            # print 'choose', module_chosen, sum([module_area_dict[k] for k in left_module_list]) - module_area_dict[module_chosen]
            locked.append(module_chosen)
            gain_list.append(module_gain_dict[module_chosen])
            step_list.append(module_chosen)
            # print module_chosen
            if module_chosen in left_module_list:
                left_module_list.remove(module_chosen)
                right_module_list.append(module_chosen)
            else:
                right_module_list.remove(module_chosen)
                left_module_list.append(module_chosen)
            # move module_chosen
            critical_nets = module_wire_dict[module_chosen]
            for net in critical_nets:
                for module in wire_module_dict[net]:
                    module_gain_dict[module] = FS(module, module_wire_dict, wire_module_dict, left_module_list,
                                                  right_module_list, wire_weight_dict) - TE(module, module_wire_dict,
                                                                              wire_module_dict, left_module_list,
                                                                              right_module_list,wire_weight_dict)
            # print module_chosen, module_gain_dict[module_chosen]
            # updated gain
        # print gain_list
        # print step_list
        max_gain, step = 0, 0
        for i in range(len(gain_list)):
            if sum(gain_list[0:i+1]) > max_gain:
                max_gain = sum(gain_list[:i+1])
                step = i+1
        # print 'step',step
        # print max_gain, step
        max_gain_step = step_list[:step]
        max_gain_list = gain_list[:step]
        # print sum(max_gain_list)
        if sum(max_gain_list) <= 0:
            left_module_list = initial_left
            right_module_list = initial_right
            break
        # print max_gain_step
        # print max_gain_list
        left_module_list = initial_left
        right_module_list = initial_right
        module_gain_dict = initial_gain_dict
        for module in max_gain_step:
            if module in left_module_list:
                left_module_list.remove(module)
                right_module_list.append(module)
            else:
                left_module_list.append(module)
                right_module_list.remove(module)
            critical_nets = module_wire_dict[module]
            for net in critical_nets:
                for module in wire_module_dict[net]:
                    module_gain_dict[module] = FS(module, module_wire_dict, wire_module_dict, left_module_list,right_module_list,wire_weight_dict)\
                                               - TE(module, module_wire_dict,wire_module_dict, left_module_list,right_module_list,wire_weight_dict)

        locked, gain_list, step_list = [], [], []

    # print left_module_list
    # print right_module_list
    # print sum([module_area_dict[k] for k in left_module_list])
    # print sum([module_area_dict[k] for k in right_module_list])

    sum_cut = sum([wire_weight_dict[net] for net in wire_list if not TE_net(net, wire_module_dict[net], left_module_list, right_module_list)])
    # print sum_cut
    print "cut number reduced: ", initial_cut - sum_cut

    return left_module_list, right_module_list, sum_cut

def area_constraint(module, low_border, high_border, left_module_list, module_area_dict):
    if module in left_module_list:
        left_area =  sum([module_area_dict[k] for k in left_module_list]) - module_area_dict[module]
        if low_border <= left_area <= high_border:
            return True
        else: return False
    else:
        left_area =  sum([module_area_dict[k] for k in left_module_list]) + module_area_dict[module]
        if low_border <= left_area <= high_border:
            return True
        else: return False

def FS(module, module_wire_dict, wire_module_dict, left_module_list, right_module_list, wire_weight_dict):
    all_net = module_wire_dict[module]
    return sum([wire_weight_dict[net] for net in all_net if FS_net(net, wire_module_dict[net], module, left_module_list,right_module_list)])

def FS_net(net, net_module_list, module, left_module_list, right_module_list):
    if module in left_module_list:
        # return len([module for module in net_module_list if module in left_module_list]) == 1
        return len(set(net_module_list).intersection(set(left_module_list))) == 1
        #set.intersection equals set & set
    else:
        # return len([module for module in net_module_list if module in right_module_list]) == 1
        return len(set(net_module_list).intersection(set(right_module_list))) == 1


def TE(module, module_wire_dict, wire_module_dict, left_module_list, right_module_list, wire_weight_dict):
    all_net = module_wire_dict[module]
    return sum([wire_weight_dict[net] for net in all_net if TE_net(net, wire_module_dict[net], left_module_list,right_module_list)])

def TE_net(net, net_module_list, left_module_list,right_module_list):
    # return len([module for module in net_module_list if module in left_module_list]) == 0 or len([module for module in net_module_list if module in right_module_list]) == 0
    return len(set(net_module_list).intersection(set(left_module_list))) == 0 or len(set(net_module_list).intersection(set(right_module_list))) == 0

def Nlayer_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, wire_weight_dict, N, factor):
    ### initial partition
    initial_partition_module_list = module_list[:]
    initial_partition_list = []
    total_area = sum(module_area_dict[m] for m in module_list)
    average_area = total_area/N
    low_border = average_area*(1-factor)
    high_border = average_area*(1+factor)
    print low_border, high_border
    for i in reversed(range(N)):
        partition_i = random.sample(initial_partition_module_list, len(initial_partition_module_list)/(i+1))
        while not low_border <= sum(module_area_dict[m] for m in partition_i) <= high_border:
            partition_i = random.sample(initial_partition_module_list, len(initial_partition_module_list)/(i+1))
        initial_partition_list.append(partition_i)
        initial_partition_module_list = list(set(initial_partition_module_list) - set(partition_i))
    layer_area_list = []
    for i in initial_partition_list:
        layer_area_list.append(sum(module_area_dict[m] for m in i))
        print len(i),  sum(module_area_dict[m] for m in i), i

    ### calculate initial gain
    layer_module_list = initial_partition_list[:]
    module_layer_dict = {}
    for module in module_list:
        for layer in layer_module_list:
            if module in layer:
                module_layer_dict[module] = layer_module_list.index(layer)
    initial_module_layer_dict = copy.deepcopy(module_layer_dict)
    initial_cut =sum(wire_cost(wire, wire_weight_dict[wire], wire_module_dict[wire], module_layer_dict) for wire in wire_list)
    module_cost_dict = {}
    for module in module_list:
        module_cost_dict[module] = []
        for layer in range(N):
            module_layer_dict[module] = layer
            module_cost_dict[module].append(sum(wire_cost(wire, wire_weight_dict[wire], wire_module_dict[wire], module_layer_dict) for wire in module_wire_dict[module]))
        module_layer_dict[module] = initial_module_layer_dict[module]
    # print module_cost_dict
    module_gain_dict = {module:module_cost_dict[module][initial_module_layer_dict[module]]-min(module_cost_dict[module]) for module in module_list}
    # print module_gain_dict
    # print module_layer_dict
    ### fm_partition
    locked_list = [module for module in module_list if module_gain_dict[module] == 0]
    end_iter = 0
    while not end_iter:
        module_sorted = sorted(module_list, key=lambda k: module_gain_dict[k], reverse=True)
        for module in module_sorted:
            opti_layer = module_cost_dict[module].index(min(module_cost_dict[module]))
            if module not in locked_list and N_layer_area_constraint(module, layer_area_list, low_border, high_border, module_layer_dict[module], opti_layer, module_area_dict[module]) and module_gain_dict[module] > 0:
                # print module
                layer_area_list[module_layer_dict[module]] -= module_area_dict[module]
                module_layer_dict[module] = opti_layer
                layer_area_list[opti_layer] += module_area_dict[module]
                locked_list.append(module)
                connected_module_list = []
                for net in module_wire_dict[module]:
                    for connected_module in wire_module_dict[net]:
                        connected_module_list.append(connected_module)
                connected_module_list = list(set(connected_module_list))
                for connected_module in connected_module_list:
                    now_layer = module_layer_dict[connected_module]
                    module_cost_dict[connected_module] = []
                    for layer in range(N):
                        module_layer_dict[connected_module] = layer
                        module_cost_dict[connected_module].append(sum(wire_cost(wire, wire_weight_dict[wire], wire_module_dict[wire], module_layer_dict) for wire in module_wire_dict[connected_module]))
                    module_layer_dict[connected_module] = now_layer
                    module_gain_dict[connected_module] = module_cost_dict[connected_module][now_layer] - min(module_cost_dict[connected_module])
                break
            end_iter = 1
    end_cut = sum(wire_cost(wire, wire_weight_dict[wire], wire_module_dict[wire], module_layer_dict) for wire in wire_list)
    print initial_cut, end_cut

    partitioned_module_list = [[] for i in range(N)]
    for module in module_list:
        layer = module_layer_dict[module]
        partitioned_module_list[layer].append(module)

    for i in partitioned_module_list:
        print len(i),  sum(module_area_dict[m] for m in i), i

def wire_cost(wire, wire_weight, wire_module_list, module_layer_dict):
    return wire_weight*(max(module_layer_dict[m] for m in wire_module_list)-min(module_layer_dict[i] for i in wire_module_list))

def N_layer_area_constraint(module, layer_area_list, low_border, high_border, this_layer, opti_layer, module_area):
    if low_border <= layer_area_list[this_layer] - module_area <= high_border and low_border <= layer_area_list[opti_layer] + module_area <= high_border:
        return True
    else:
        return False

if __name__ == '__main__':
    module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, wire_weight_dict= ast2graph()
    factor = 0.1
    N = 3
    Nlayer_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, wire_weight_dict, N, factor)
    # two_fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict)

    # sum_cut, result_a, result_b, result_c = three_fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict)
    # min_cut, best_top, best_middle, best_bottom = sum_cut, result_a, result_b, result_c
    # for i in range(200):
    #     sum_cut, result_a, result_b, result_c = three_fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict)
    #     if sum_cut < min_cut:
    #         min_cut, best_top, best_middle, best_bottom = sum_cut, result_a, result_b, result_c
    # print "best cut ", min_cut
    # print sum(module_area_dict[k] for k in best_top), sum(module_area_dict[k] for k in best_middle), sum(module_area_dict[k] for k in best_bottom)

    # sum_cut, result_a, result_b, result_c, result_d = four_fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict)
    # min_cut, best_a, best_b, best_c, best_d = sum_cut, result_a, result_b, result_c, result_d
    # for i in range(100):
    #     sum_cut, result_a, result_b, result_c, result_d = four_fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, wire_weight_dict)
    #     if sum_cut < min_cut:
    #         min_cut, best_a, best_b, best_c, best_d = sum_cut, result_a, result_b, result_c, result_d
    # print "best cut ", min_cut
    # print sum(module_area_dict[k] for k in best_a), sum(module_area_dict[k] for k in best_b), sum(module_area_dict[k] for k in best_c), sum(module_area_dict[k] for k in best_d)