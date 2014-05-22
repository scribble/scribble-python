import scrib_constants as constants
import scrib_util as util

from ast.globel.globalprotocolblock import \
    pretty_print as globalprotocolblock_pretty_print


LABEL_INDEX = 0
BLOCK_INDEX = 1


def traverse_recursion(traverser, node_, label, body):
    traversed = [traverser.traverse_untyped_leaf(label)]
    traversed.append(traverser.traverse(body))
    rebuilt = util.antlr_dupnode_and_replace_children(node_, traversed)
    return rebuilt

def traverse(traverser, node_):
    return traverse_recursion(traverser, node_,
                             get_label_child(node_),
                             get_block_child(node_))


def context_visitor_enter(cv, node_):
    context_ = cv.get_context()
    pushed = context_.push_globalrecursion(node_)
    cv.set_context(pushed)


def context_visitor_visit(cv, node_):
    lab = get_label_child(node_)
    block = get_block_child(node_)
    visited = []
    visited.append(lab)
    visited.append(cv.visit(block))
    return util.antlr_dupnode_and_replace_children(node_, visited)


def context_visitor_leave(cv, node_):
    clone = cv.get_context().clone()
    #reclab = get_label(node_)
    reclab = clone.get_current_scope() + '.' + get_label(node_)
        # FIXME: factor out with above and Context.push_globalrecursion
    clone = clone.remove_recursion_label(reclab)
    if clone.is_continue_label_seen(reclab):
        clone = clone.remove_continue_label(reclab);
    clone = clone.set_rec_exitable(True)
    cv.set_context(clone.pop_globalrecursion(node_))


def check_wellformedness_enter(checker, node_):
    context_ = checker.get_context()
    # Section 4.6.7 -- global recursion must specify a recursion label that is
    # not bound
    #reclab = get_label(node_)
    reclab = context_.get_current_scope() + '.' + get_label(node_)
    if reclab in context_.peek_recursion_labels().keys():
        util.report_error("Bad recursion label: " + reclab)


def check_wellformedness_visit(checker, node_):
    return context_visitor_visit(checker, node_)


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    reclab = get_label(node_)
    block = get_block_child(node_)
    roles = projector.rc.collect_roles(block)
        # replace by a better check (role involved) on the projection
    if projector.role in roles:
        return projector.nf.localrecursion(#projector.rolemap[projector.role],
                                           projector.role,
                                           reclab,
                                           projector.visit(block))
    else:
        return None


def get_label(node_):
    return get_label_child(node_).getText()


def pretty_print(node_):
    text = ""
    text = text + constants.REC_KW + ' ' + get_label(node_)
        # FIXME: factor out
    block = get_block_child(node_)
    text = text + '\n' + globalprotocolblock_pretty_print(block)
    return text


def get_label_child(node_):
    return node_.getChild(LABEL_INDEX)

def get_block_child(node_):
    return node_.getChild(BLOCK_INDEX)
