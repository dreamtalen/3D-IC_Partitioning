if __name__ == '__main__':
    graph = {'A':['D', 'F'], 'B':['C', 'E'], 'C':['B'], 'D':['A', 'F'], 'E':['B'], 'F':['A']}
    left = ['A', 'C', 'E']
    right = ['B', 'D', 'F']
    locked = []
    while len(locked) < 6:
        edge = {key:0 for key in left+right}
        for node in left:
            for dot in graph[node]:
                if dot in right:
                     edge[node] += 1
        for node in right:
            for dot in graph[node]:
                if dot in left:
                     edge[node] += 1
        print edge
        edge_changed = {key:0 for key in left+right}
        for node in left:
            for dot in graph[node]:
                if dot in left:
                     edge_changed[node] += 1
        for node in right:
            for dot in graph[node]:
                if dot in right:
                     edge_changed[node] += 1
        print edge_changed
        edge_gain = {node:edge[node]-edge_changed[node] for node in edge}
        print edge_gain
        node_sorted = sorted(edge_gain.keys(), key=lambda k: edge_gain[k], reverse=True)
        print node_sorted
        # node_changed = max(edge_gain.keys(), key=lambda k:edge_gain[k])
        node_changed = [i for i in node_sorted if i not in locked][0]
        print node_changed
        if edge_gain[node_changed] < 0: break
        if node_changed in left:
            left.remove(node_changed)
            right.append(node_changed)
        else:
            right.remove(node_changed)
            left.append(node_changed)
        locked.append(node_changed)
    print left, right, locked