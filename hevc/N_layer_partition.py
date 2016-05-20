import random
import copy

def parser_area_report():
    design_area_dict = {}
    with open("area_report.rpt") as f:
        for line in f.readlines():
            line = line.strip().split()
            if len(line) == 6 or len(line) == 7:
                design_area_dict[(line[-1])] = float(line[-6])
    return design_area_dict

def ast2graph_module(top_module_name, prefix=''):
    module_wire_dict = {}
    wire_weight_dict = {}
    module_design_dict = {}
    module_list = []
    wire_list = []
    design_list = []
    this_design = ''
    with open("me_full.ast") as f:
        for line in f.readlines():
            if line:
                content_list = line.strip().split()
                type = content_list[0]
                name = content_list[1]
                if type == 'moduleDef':
                    this_design = name
                if type == 'net' and this_design == top_module_name:
                    this_net = name
                    wire_list.append(name)
                    wire_weight_dict[name] = 1
                if type == 'width' and this_design == top_module_name:
                    if name is not '0' and this_net:
                        wire_weight_dict[this_net] = int(name) + 1
                        this_net = ''
                if type == 'module' and this_design == top_module_name:
                    this_module = top_module_name+'_'+name if not prefix else prefix+'_'+top_module_name+'_'+name
                    module_wire_dict[this_module] = []
                    module_design_dict[this_module] = content_list[2]
                if type == 'port' and this_design == top_module_name and this_module:
                    module_wire_dict[this_module].append(name)
    for key, value in module_wire_dict.items():
        module_wire_dict[key] = list(set(value))
        module_list.append(key)
        design_list.append(module_design_dict[key])

    wire_module_dict = {wire:[] for wire in wire_list}
    for module in module_list:
        for w in module_wire_dict[module]:
            wire_module_dict[w].append(module)
    # for wire in wire_list:
    #     wire_module_dict[wire] = [module for module in module_list if wire in module_wire_dict[module]]


    return module_wire_dict, wire_module_dict, module_list, wire_list, design_list, wire_weight_dict, module_design_dict
def Nlayer_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, wire_weight_dict, N, factor):
    ### initial partition
    initial_partition_module_list = module_list[:]
    initial_partition_list = [[] for i in range(N)]
    total_area = sum(module_area_dict[m] for m in module_list)
    print 'total_area', total_area
    average_area = total_area/N
    low_border = average_area*(1-factor)
    high_border = average_area*(1+factor)
    print low_border, high_border
    # for i in reversed(range(N)):
    #     partition_i = random.sample(initial_partition_module_list, len(initial_partition_module_list)/(i+1))
    #     while not low_border <= sum(module_area_dict[m] for m in partition_i) <= high_border:
    #         partition_i = random.sample(initial_partition_module_list, len(initial_partition_module_list)/(i+1))
    #     initial_partition_list.append(partition_i)
    #     initial_partition_module_list = list(set(initial_partition_module_list) - set(partition_i))
    #     print 'initial_partition', i
    initial_partition_module_list = sorted(module_list, key=lambda k: module_area_dict[k], reverse=True)
    for i in range(N):
        current_area = sum(module_area_dict[m] for m in initial_partition_list[i])
        while current_area < average_area:
            try:
                new_module = initial_partition_module_list.pop(0)
            except:
                break
            if current_area + module_area_dict[new_module] < high_border:
                initial_partition_list[i].append(new_module)
                current_area += module_area_dict[new_module]
            else:
                initial_partition_module_list.insert(0, new_module)
                break
        if i == N -1:
            for m in initial_partition_module_list:
                initial_partition_list[i].append(m)

    layer_area_list = []
    for i in initial_partition_list:
        layer_area_list.append(sum(module_area_dict[m] for m in i))
        print len(i),  sum(module_area_dict[m] for m in i)

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
                print module
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
    print 'initial cut:',initial_cut
    print 'end_cut:', end_cut

    partitioned_module_list = [[] for i in range(N)]
    for module in module_list:
        layer = module_layer_dict[module]
        partitioned_module_list[layer].append(module)

    for i in partitioned_module_list:
        print len(i),  sum(module_area_dict[m] for m in i)

    return end_cut, partitioned_module_list

def wire_cost(wire, wire_weight, wire_module_list, module_layer_dict):
    # print wire_module_dict
    try:
        return wire_weight*(max(module_layer_dict[m] for m in wire_module_list)-min(module_layer_dict[i] for i in wire_module_list))
    except:
        return 0

def N_layer_area_constraint(module, layer_area_list, low_border, high_border, this_layer, opti_layer, module_area):
    if low_border <= layer_area_list[this_layer] - module_area <= high_border and low_border <= layer_area_list[opti_layer] + module_area <= high_border:
        return True
    else:
        return False

if __name__ == '__main__':
    max_split_area = 120000
    max_module_num = 100000
    factor = 0.1
    N = 3
    top_module_name = 'me_top'
    module_wire_dict, wire_module_dict, module_list, wire_list, design_list, wire_weight_dict, module_design_dict = ast2graph_module(top_module_name)
    # print module_list
    print len(list(set(module_list))), len(list(set(design_list)))
    design_area_dict = parser_area_report()
    # print design_area_dict
    unknown_area_design_list = list(set(d for d in design_list if d not in design_area_dict.keys()))
    for unknown_area_design in unknown_area_design_list:
        design_area_dict[unknown_area_design] = 10
    module_area_dict = {module:design_area_dict[module_design_dict[module]] for module in module_list}
    # print module_area_dict
    total_area = sum(module_area_dict[m] for m in module_list)
    print total_area
    area_upper_limit = total_area/N
    area_upper_limit = 500000
    # print area_upper_limit
    unlimited_module_list = [module for module in module_list if module_area_dict[module] > area_upper_limit]
    print unlimited_module_list
    prefix = top_module_name

    # unlimited_module_list = ['me_top_I_tier1']
    while unlimited_module_list:
        print unlimited_module_list
        decompose_module = unlimited_module_list.pop(0)
        new_module_wire_dict, new_wire_module_dict, new_module_list, new_wire_list, new_design_list, new_wire_weight_dict, new_module_design_dict = ast2graph_module(module_design_dict[decompose_module], prefix)

        if len(module_list)+len(new_module_list) > max_module_num:
            continue
        else:
            unknown_area_design_list = list(set(d for d in new_design_list if d not in design_area_dict.keys()))
            for unknown_area_design in unknown_area_design_list:
                design_area_dict[unknown_area_design] = 10
                # print unknown_area_design

            module_list.remove(decompose_module)
            module_list += new_module_list

            module_wire_dict.update(new_module_wire_dict)

            wire_list = list(set(wire_list+new_wire_list))
            for w in new_wire_list:
                if wire_module_dict.get(w):
                    wire_module_dict[w] += new_wire_module_dict[w]
                else:
                    wire_module_dict[w] = new_wire_module_dict[w]
            for v in wire_module_dict.values():
                if decompose_module in v:
                    v.remove(decompose_module)

            wire_weight_dict.update(new_wire_weight_dict)

            design_list = list(set(design_list+new_design_list))

            module_design_dict.update(new_module_design_dict)

            print len(module_list)
            # print len(wire_list)

            for m in new_module_list:
                module_area_dict[m] = design_area_dict[module_design_dict[m]]
                if module_area_dict[m] > area_upper_limit:
                    unlimited_module_list.append(m)
            # prefix += decompose_module
            # print design_area_dict['sr_mem_cluster']

    mincut, min_partitioned_module_list = Nlayer_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, wire_weight_dict, N, factor)

