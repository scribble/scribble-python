from ast.nodefactory import NodeFactory as NodeFactory


# Factor out local visitor with reachability checker
class SubprotocolCollector(object):
    nf = NodeFactory()

    def __init__(self, context_):
        super(SubprotocolCollector, self).__init__()
        self._context = context_

    def collect_subprotocols(self, node_, do_recursively):
        self.do_recursively = do_recursively
        self._protos = []
        self.visit(node_)
        return self._protos
    
    # Visits target recursively if specified to do so
    def add_subprotocol(self, proto):
        if proto not in self._protos:
            self._protos.append(proto)
            if self.do_recursively:
                self.visit(self._context.get_projection(proto))

    def visit(self, node_):
        return node_.collect_subprotocols(self)
