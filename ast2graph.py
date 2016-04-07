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

    print module_list
    wire_list = list(set(wire_list))
    print wire_list

    wire_module_dict = {}
    for wire in wire_list:
        wire_module_list = [module for module in module_list if wire in module_wire_dict[module]]
        wire_module_dict[wire] = wire_module_list
    # print wire_module_dict

    # hypergraph completed

    left_module_list = module_list[:len(module_list)/2]
    right_module_list = module_list[len(module_list)/2:]

    #initial partition



if __name__ == '__main__':
    ast2graph()