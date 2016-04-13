import random
import copy
def ast2graph():
    module_wire_dict = {}
    module_list = []
    wire_list = []
    left_module_list, right_module_list = [], []
    with open("tier2.ast") as f:
        for line in f.readlines():
            if line:
                type, name = line.strip().split()
                if type == 'module':
                    this_module = name
                    module_wire_dict[this_module] = []
                    left_module_list.append(this_module)
                if type == 'port':
                    module_wire_dict[this_module].append(name)
    with open("tier1.ast") as f:
        for line in f.readlines():
            if line:
                type, name = line.strip().split()
                if type == 'module':
                    this_module = name
                    module_wire_dict[this_module] = []
                    right_module_list.append(this_module)
                if type == 'port':
                    module_wire_dict[this_module].append(name)
    for key, value in module_wire_dict.items():
        module_wire_dict[key] = list(set(value))
        module_list.append(key)
        wire_list += value
    # print module_wire_dict

    # print module_list
    wire_list = list(set(wire_list))
    # print wire_list

    wire_module_dict = {}
    for wire in wire_list:
        wire_module_dict[wire] = []
    # for wire in wire_list:
    #     wire_module_list = [module for module in module_list if wire in module_wire_dict[module]]
    #     wire_module_dict[wire] = wire_module_list
    for module in module_list:
        this_wire_list = module_wire_dict[module]
        for wire in this_wire_list:
            wire_module_dict[wire].append(module)

    # print left_module_list
    # print right_module_list
    # print wire_module_dict

    # module_area_dict = {module:random.randint(1,5) for module in module_list}
    module_area_dict = {}
    # print module_list
    with open("area_report_me_chip.rpt") as f:
        line_list = f.readlines()
        for index, line in enumerate(line_list):
            line = line.strip().split()
            try:
                if line:
                    if line[0][25:] in module_list:
                        try:
                            module_area_dict[line[0][25:]] = float(line[1])
                        except:
                            next_line = line_list[index+1]
                            module_area_dict[line[0][25:]] = float(next_line.strip().split()[0])
                    elif line[0][39:] in module_list:
                        try:
                            module_area_dict[line[0][39:]] = float(line[1])
                        except:
                            next_line = line_list[index+1]
                            module_area_dict[line[0][39:]] = float(next_line.strip().split()[0])
            except: pass
    # print module_area_dict
    for module in module_list:
        if module not in module_area_dict.keys():
            if 'U' in module:
                module_area_dict[module] = 3.6
            elif 'abs_outs_reg_reg_' in module:
                module_area_dict[module] = 9.36
            elif '_reg' in module:
                module_area_dict[module] = 9.0
            elif module == 'inst_current_block_memcluster':
                module_area_dict[module] = 101052.1094
            elif 'inst_minisad_tree_buffer_' in module:
                module_area_dict[module] = 2397.6000
            elif 'inst_merge_mem_' in module:
                module_area_dict[module] = 6202.5712
            elif 'inst_output_buffer_' in module:
                module_area_dict[module] = 462.6
            elif 'inst_output_buffer_final' in module:
                module_area_dict[module] = 601.5600
            elif module == 'inst_sad_tree_2':
                module_area_dict[module] = 837.7200
            elif module == 'inst_sad_tree_1':
                module_area_dict[module] = 3617.2800
            else:
                # print module
                module_area_dict[module] = 10
            # module_area_dict[module] = 1500.0

    # print module_area_dict

    # hypergraph completed
    return module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, left_module_list, right_module_list

# @profile
def fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, left_module_list, right_module_list):

    # initial_left = left_module_list[:]
    # initial_right = right_module_list[:]

    locked = []
    gain_list = []
    step_list = []

    total_area = sum([module_area_dict[k] for k in left_module_list]) + sum([module_area_dict[k] for k in right_module_list])

    low_border = factor*total_area - max(module_area_dict.values())
    high_border = factor*total_area + max(module_area_dict.values())
    print low_border, high_border, total_area
    print sum([module_area_dict[k] for k in left_module_list])
    print sum([module_area_dict[k] for k in right_module_list])

    initial_cut = len([net for net in wire_list if not TE_net(net, wire_module_dict[net], left_module_list, right_module_list)])
    print initial_cut
    module_gain_dict = {module: FS(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list) - TE(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list) for module in module_list}

    while True:
        initial_gain_dict = copy.deepcopy(module_gain_dict)

        initial_left = left_module_list[:]
        initial_right = right_module_list[:]
        # module_gain_dict = {module: FS(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list) - TE(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list) for module in module_list}
        # print right_module_list
        while len(locked) < len(module_list):
            module_sorted = sorted(module_gain_dict.keys(), key=lambda k: module_gain_dict[k], reverse=True)
            module_chosen = ''
            for module in module_sorted:
                if module not in locked and area_constraint(module, low_border, high_border, left_module_list, module_area_dict):
                    module_chosen = module
                    break
            if not module_chosen:
                break
            print module_chosen, module_gain_dict[module_chosen]
            # print 'choose', module_chosen, sum([module_area_dict[k] for k in left_module_list]) - module_area_dict[module_chosen]
            locked.append(module_chosen)
            gain_list.append(module_gain_dict[module_chosen])
            step_list.append(module_chosen)
            # print module_chosen
            if module_chosen in left_module_list:
                left_module_list.remove(module_chosen)
                right_module_list.append(module_chosen)
            else:
                left_module_list.append(module_chosen)
                right_module_list.remove(module_chosen)
            # move module_chosen
            critical_nets = module_wire_dict[module_chosen]
            for net in critical_nets:
                for module in wire_module_dict[net]:
                    module_gain_dict[module] = FS(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list) - TE(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list)
            # updated gain
        print gain_list
        print step_list
        max_gain, step = 0, 0
        for i in range(len(gain_list)):
            if sum(gain_list[0:i+1]) > max_gain:
                max_gain = sum(gain_list[:i+1])
                step = i+1
        # print max_gain, step
        max_gain_step = step_list[:step]
        max_gain_list = gain_list[:step]
        print sum(max_gain_list)
        if sum(max_gain_list) <= 0:
            left_module_list = initial_left
            right_module_list = initial_right
            break
        print max_gain_step
        print max_gain_list
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
                    module_gain_dict[module] = FS(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list) - TE(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list)

        locked, gain_list, step_list = [], [], []

    # print left_module_list
    # print right_module_list
    print sum([module_area_dict[k] for k in left_module_list])
    print sum([module_area_dict[k] for k in right_module_list])

    sum_cut = len([net for net in wire_list if not TE_net(net, wire_module_dict[net], left_module_list, right_module_list)])
    print sum_cut
    print "cut number reduced: ", initial_cut - sum_cut

def area_constraint(module, low_border, high_border, left_module_list, module_area_dict):
    if module in left_module_list:
        left_area =  sum([module_area_dict[module] for module in left_module_list]) - module_area_dict[module]
        if low_border <= left_area <= high_border:
            return True
        else: return False
    else:
        left_area =  sum([module_area_dict[module] for module in left_module_list]) + module_area_dict[module]
        if low_border <= left_area <= high_border:
            return True
        else: return False

def FS(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list):
    all_net = module_wire_dict[module]
    return len([net for net in all_net if FS_net(net, wire_module_dict[net], module, left_module_list,right_module_list)])

def FS_net(net, net_module_list, module, left_module_list, right_module_list):
    if module in left_module_list:
        # return len([module for module in net_module_list if module in left_module_list]) == 1
        return len(set(net_module_list).intersection(set(left_module_list))) == 1
    else:
        # return len([module for module in net_module_list if module in right_module_list]) == 1
        return len(set(net_module_list).intersection(set(right_module_list))) == 1


def TE(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list):
    all_net = module_wire_dict[module]
    return len([net for net in all_net if TE_net(net, wire_module_dict[net], left_module_list,right_module_list)])

def TE_net(net, net_module_list, left_module_list,right_module_list):
    # return len([module for module in net_module_list if module in left_module_list]) == 0 or len([module for module in net_module_list if module in right_module_list]) == 0
    return len(set(net_module_list).intersection(set(left_module_list))) == 0 or len(set(net_module_list).intersection(set(right_module_list))) == 0

if __name__ == '__main__':
    module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, left_module_list, right_module_list = ast2graph()
    factor = 0.55
    fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor, left_module_list, right_module_list)