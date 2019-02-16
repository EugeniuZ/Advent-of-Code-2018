class _Node:
    def __init__(self, metadata, children):
        self.metadata = metadata
        self.children = children

    def traverse(self, f_node, f_result):
        if self.children:
            r = f_node(self)
            for c in self.children:
                c = c.traverse(f_node, f_result)
                r = f_result(c, r)
            return r
        else:
            return f_node(self)


def read_input(filename):
    with open(filename) as f:
        encoding = [int(c) for c in f.read().split()]
    tree, _ = _read_tree(encoding)
    return tree


def _read_tree(encoding):
    n_children = encoding[0]
    n_metadata_entries = encoding[1]
    if n_children == 0:
        r = 2 + n_metadata_entries
        return _Node(encoding[2: r], []), encoding[r:]
    else:
        children = []
        encoding = encoding[2:]
        for i in range(n_children):
            node, encoding = _read_tree(encoding)
            children.append(node)
        return _Node(encoding[:n_metadata_entries], children), encoding[n_metadata_entries:]


def solution1(tree):
    return tree.traverse(
        lambda node: sum(node.metadata),
        lambda value, accum: value + accum
    )


def solution2(node):
    if not node.children:
        return sum(node.metadata)
    else:
        s = 0
        nc = len(node.children)
        for metadata in node.metadata:
            i = metadata - 1
            if i < nc:
                s += solution2(node.children[i])
        return s
