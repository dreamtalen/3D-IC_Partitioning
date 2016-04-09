import random

def ast2graph():
    module_wire_dict = {}
    module_list = []
    wire_list = []
    with open("idct_module.ast") as f:
        for line in f.readlines():
            if line:
                type, name = line.strip().split()
                if type == 'module':
                    this_module = name
                    module_wire_dict[this_module] = []
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
        wire_module_list = [module for module in module_list if wire in module_wire_dict[module]]
        wire_module_dict[wire] = wire_module_list
    # print wire_module_dict

    module_area_dict = {module:random.randint(1,5) for module in module_list}

    # hypergraph completed
    return module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict

def fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor):
    left_module_list = module_list[:len(module_list)/2]
    right_module_list = module_list[len(module_list)/2:]
    # print left_module_list
    # print right_module_list

    #initial partition
    # print FS('inst_mem_ctrl_tran',module_wire_dict,wire_module_dict,left_module_list,right_module_list)
    # print TE('inst_mem_ctrl_tran',module_wire_dict,wire_module_dict,left_module_list,right_module_list)
    module_gain_dict = {module: FS(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list) - TE(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list) for module in module_list}
    # print module_gain_dict
    locked = []
    gain_list = []
    step_list = []

    low_border = factor*sum(module_area_dict.values()) - max(module_area_dict.values())
    high_border = factor*sum(module_area_dict.values()) + max(module_area_dict.values())
    print low_border, high_border, sum(module_area_dict.values())
    print sum([module_area_dict[k] for k in left_module_list])
    print sum([module_area_dict[k] for k in right_module_list])

    while len(locked) < len(module_list):
        module_sorted = sorted(module_gain_dict.keys(), key=lambda k: module_gain_dict[k], reverse=True)
        try:
            module_chosen = [module for module in module_sorted if module not in locked and area_constraint(module, low_border, high_border, left_module_list, module_area_dict)][0]
        except:
            break
        # print 'choose', module_chosen, sum([module_area_dict[k] for k in left_module_list]) - module_area_dict[module_chosen]
        locked.append(module_chosen)
        gain_list.append(module_gain_dict[module_chosen])
        step_list.append(module_chosen)
        # print module_chosen
        critical_nets = module_wire_dict[module_chosen]
        if module_chosen in left_module_list:
            left_module_list.remove(module_chosen)
            right_module_list.append(module_chosen)
        else:
            left_module_list.append(module_chosen)
            right_module_list.remove(module_chosen)
        # move module_chosen
        for net in critical_nets:
            for module in wire_module_dict[net]:
                module_gain_dict[module] = FS(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list) - TE(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list)
        # updated gain
    # print gain_list
    # print step_list
    max_gain, step = 0, 0
    for i in range(len(gain_list)):
        if sum(gain_list[0:i]) > max_gain:
            max_gain = sum(gain_list[:i])
            step = i
    # print max_gain, step
    max_gain_step = step_list[:step]
    max_gain_list = gain_list[:step]
    print max_gain_step
    print max_gain_list
    left_module_list = module_list[:len(module_list)/2]
    right_module_list = module_list[len(module_list)/2:]
    for module in max_gain_step:
        if module in left_module_list:
            left_module_list.remove(module)
            right_module_list.append(module)
        else:
            left_module_list.append(module)
            right_module_list.remove(module)
    print left_module_list
    print right_module_list
    print sum([module_area_dict[k] for k in left_module_list])
    print sum([module_area_dict[k] for k in right_module_list])

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
        return len([module for module in net_module_list if module in left_module_list]) == 1
    else:
        return len([module for module in net_module_list if module in right_module_list]) == 1

def TE(module,module_wire_dict,wire_module_dict,left_module_list,right_module_list):
    all_net = module_wire_dict[module]
    return len([net for net in all_net if TE_net(net, wire_module_dict[net], left_module_list,right_module_list)])

def TE_net(net, net_module_list, left_module_list,right_module_list):
    return len([module for module in net_module_list if module in left_module_list]) == 0 or len([module for module in net_module_list if module in right_module_list]) == 0

if __name__ == '__main__':
    module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict = ast2graph()
    factor = 0.5
    fm_partition(module_wire_dict, wire_module_dict, module_list, wire_list, module_area_dict, factor)