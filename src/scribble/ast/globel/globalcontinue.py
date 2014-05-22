import scrib_constants as constants
import scrib_util as util


LABEL_INDEX = 0


def traverse_continue(traverser, node_, label):
    traversed = [traverser.traverse_untyped_leaf(label)]
    new = util.antlr_dupnode_and_replace_children(node_, traversed)
    return new

def traverse(traverser, node_):
    return traverse_continue(traverser, node_, get_label_child(node_))


def context_visitor_enter(cv, node_):
    context_ = cv.get_context()
    #contlab = get_label(node_)
    contlab = context_.get_current_scope() + '.' + get_label(node_)
        # FIXME: factor out with globalrecursion and Context
    clone = context_.add_continue_label(contlab) 
        # Takes care of bad sequence within rec block
    clone = clone.set_rec_exitable(False)
        # Takes care of bad sequence after (rec) block
    cv.set_context(clone)
    

def context_visitor_visit(cv, node_):
    return node_


def context_visitor_leave(cv, node_):
    """contexts = []
    context_ = cv.get_context()
    parent = context_.parent
    choice = None
    while util.get_node_type(parent.ast) != constants.GLOBAL_PROTOCOL_DECL_NODE_TYPE:
        print "a: ", parent.ast
        if choice is not None:
            contexts.append(parent)
        if util.get_node_type(parent.ast) == constants.GLOBAL_CHOICE_NODE_TYPE:
            if choice is None:
                choice = parent
        parent = parent.parent
    enabled = {}
    if choice is not None and len(context_.get_enabled_roles().keys()) == 1:
        print "c: ", choice, contexts
        i = len(contexts) - 1
        while i > 0:
            ... problem is roledecllist enbales all roles with dummy value; need the explicit messages ..."""
    pass


def check_wellformedness_enter(checker, node_):
    context = checker.get_context()
    #contlab = get_label(node_)
    contlab = context.get_current_scope() + '.' + get_label(node_)  
        # FIXME: factor out with globalrecursion and Context
    if not context.is_recursion_label_declared(contlab):
        util.report_error("Bad continue label: " + contlab)


# check for non-contractive recursions? for MPST (due to role configurations),
# there is a notion of partial contractive: can choose to be (non-)projectable
# or project in a special way -- should check on the projections
def check_wellformedness_visit(checker, node_):
    return context_visitor_visit(checker, node_)


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    reclab = get_label(node_)
    #return projector.nf.localcontinue(projector.rolemap[projector.role], reclab)
    return projector.nf.localcontinue(projector.role, reclab)


def get_label(node_):
    return get_label_child(node_).getText()


def pretty_print(node_):
    return constants.CONTINUE_KW + ' ' + get_label(node_) + ';'
        # FIXME: factor out


def get_label_child(node_):
    return node_.getChild(LABEL_INDEX)
