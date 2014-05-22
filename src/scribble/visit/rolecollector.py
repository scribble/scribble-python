from visit.traverser import Traverser as Traverser

from ast.globel.globalmessagetransfer import (
    get_source as globalmessagetransfer_get_source,
    get_destinations as globalmessagetransfer_get_destinations
)
    
from ast.roleinstantiation import get_arg as roleinstantiation_get_arg

from ast.globel.globalchoice import get_subject as globalchoice_get_subject

from ast.globel.globalinterrupt import get_role as globalinterrupt_get_role


# Should only be run on Block nodes or smaller
class RoleCollector(Traverser):
    def __init__(self):
        super(RoleCollector, self).__init__()
        #self.roles = set([])

    # Returns a set
    def collect_roles(self, node_):
        self.roles = set([])
        self.traverse(node_)
        return self.roles

    def visit_untyped_leaf(self, node_):
        return node_


    def _visit_roleinstantiationlist(self, node_):
        return node_

    def _visit_roleinstantiation(self, node_):
        self.roles.add(roleinstantiation_get_arg(node_))
        return node_

    def _visit_argumentlist(self, node_):
        return node_

    def _visit_argument(self, node_):
        return node_

    def _visit_globalprotocolblock(self, node_):
        return node_

    def _visit_globalinteractionsequence(self, node_):
        return node_

    def _visit_globalmessagetransfer(self, node_):
        self.roles.add(globalmessagetransfer_get_source(node_))
        self.roles |= set(globalmessagetransfer_get_destinations(node_))
        return node_

    def _visit_messagesignature(self, node_):
        return node_

    def _visit_payload(self, node_):
        return node_

    def _visit_payloadelement(self, node_):
        return node_

    def _visit_globalchoice(self, node_):
        self.roles.add(globalchoice_get_subject(node_))
        # although if well-formed, subject necessarily appears in the choice
        return node_

    def _visit_globalrecursion(self, node_):
        return node_

    def _visit_globalcontinue(self, node_):
        return node_

    def _visit_globalparallel(self, node_):
        return node_

    def _visit_globalinterruptible(self, node_):
        return node_

    def _visit_globalinterrupt(self, node_):
        self.roles.add(globalinterrupt_get_role(node_))
        return node_

    def _visit_globaldo(self, node_):
        return node_

    """#TODO: local nodes (if needed)

    def _visit_localprotocolblock(self, node_):
        return node_

    def _visit_localinteractionsequence(self, node_):
        return node_

    def _visit_localsend(self, node_):
        return node_

    def _visit_localreceive(self, node_):
        return node_

    def _visit_localchoice(self, node_):
        return node_

    def _visit_localrecursion(self, node_):
        return node_

    def _visit_localcontinue(self, node_):
        return node_

    def _visit_localparallel(self, node_):
        return node_

    def _visit_localinterruptible(self, node_):
        return node_

    def _visit_localthrow(self, node_):
        return node_

    def _visit_localcatch(self, node_):
        return node_

    def _visit_localdo(self, node_):
        return node_"""
