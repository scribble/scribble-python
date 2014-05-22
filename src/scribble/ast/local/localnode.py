from ast.node import Node as Node

class LocalNode(Node):  # Factor out with global?
    def __init__(self, local_role):
        super(LocalNode, self).__init__()
        self.local_role = local_role

    def pretty_print(self):
        raise NotImplementedError()

    def context_visitor_enter(self, cv):
        # Not recording ops, unlike global contexts
        pass
    
    def context_visitor_visit(self, cv):
        return self
    
    def context_visitor_leave(self, cv):
        pass
    
    # ReachabilityChecker follows WellformednessChecker pass
    def check_reachability_enter(self, checker):
        self.context_visitor_enter(checker)
    
    def check_reachability_visit(self, checker):
        return self.context_visitor_visit(checker)
    
    def check_reachability_leave(self, checker):
        self.context_visitor_leave(checker)
    
    def visit(self, visitor):
        return self
        
    def collect_subprotocols(self, collector):
        return self.visit(collector)
