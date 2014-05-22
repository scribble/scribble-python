import scrib_constants as constants
import scrib_util as util

#from visit.rolecollector import RoleCollector  # cyclic imports...

from ast.messagesignature import pretty_print as messagesignature_pretty_print

from ast.parameter import pretty_print as parameter_pretty_print

from ast.globel.globalprotocolblock import \
    pretty_print as globalprotocolblock_pretty_print

from ast.globel.globalinterrupt import (
    check_wellformedness as globalinterrupt_check_wellformedness,
    get_role as globalinterrupt_get_role,
    get_message_children as globalinterrupt_get_message_children,
    pretty_print as globalinterrupt_pretty_print
)


EMPTY_SCOPE_NAME = 'EMPTY_SCOPE_NAME'

SCOPE_NAME_INDEX = 0
INTERRUPTIBLE_BLOCK_INDEX = 1
INTERRUPTS_START_INDEX = 2


def traverse(traverser, node_):
    scope = get_scope_child(node_)
    block = get_block_child(node_)
    interrupts = get_interrupt_children(node_)
    traversed = []
    traversed.append(traverser.traverse_untyped_leaf(scope))
    traversed.append(traverser.traverse(block))
    for interr in interrupts:
        traversed.append(traverser.traverse(interr))
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def context_visitor_enter(cv, node_):
    context = cv.get_context()
    # Pushing scope for the whole interruptible, not just the block (seems OK?
    # -- is needed: interrupts must belong to the scope of the interruptible)
    pushed = context.push_globalinterruptible(node_)
    cv.set_context(pushed)


def context_visitor_visit(cv, node_):
    scope = get_scope_child(node_)
    block = get_block_child(node_)
    interrupts = get_interrupt_children(node_)
    visited = []
    visited.append(scope)
    visited.append(cv.visit(block))  # Section 4.6.9 -- block is well-formed
    visited.extend(interrupts)
    return util.antlr_dupnode_and_replace_children(node_, visited)


def context_visitor_leave(cv, node_):
    context_ = cv.get_context()
    # Section 6.3.5 -- if at least one interrupt, the interruptible has an exit
    if get_interrupt_children(node_):
        context_ = context_.set_rec_exitable(True)
        context_ = context_.set_do_exitable(True)
    cv.set_context(context_.pop_globalinterruptible(node_))


def check_wellformedness_enter(checker, node_):
    pass


# should be at least one interrupt? not currently required by the langref
def check_wellformedness_visit(checker, node_):
    visited = context_visitor_visit(checker, node_)
    interrupts = get_interrupt_children(visited)
    seen = []
    for i in interrupts:
        globalinterrupt_check_wellformedness(checker, i)
        subj = globalinterrupt_get_role(i)
        # Section 4.6.9 -- distinct interrupt roles (bound role checked inside
        # globalinterrupt)
        if subj in seen:
            util.report_error("Bad interrupt role: " + subj)
        seen.append(subj)
    return visited


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    scope = get_scope(node_)
    gblock = get_block_child(node_)
    block = projector.visit(gblock)
    throw = None  # localthrow  # FIXME: need destination roles
    catches = []  # [localcatch]

    #RoleCollector() # Couldn't import conveniently (cyclic)
    involved = projector.rc.collect_roles(gblock)
    for i in get_interrupt_children(node_):
        subj = globalinterrupt_get_role(i)  # String
        involved.add(subj)
    
    throw_messages = []
    for i in get_interrupt_children(node_):
        subj = globalinterrupt_get_role(i)  # String
        roles = list(involved - set([subj]))
        messages = []
        for sig in globalinterrupt_get_message_children(i): 
            # Factor out with interrupt, message transfer, argument, etc.
            if util.get_node_type(sig) == \
                   constants.MESSAGE_SIGNATURE_NODE_TYPE:
                messages.append(messagesignature_pretty_print(sig))
            else:
                messages.append(parameter_pretty_print(sig))
        if projector.role == subj and len(roles) > 0:
            #throws.append(projector.nf.localthrow(dests, messages)) 
            #new_roles = util.replace_in_list(roles, projector.rolemap)
            new_roles = roles
            """throw = projector.nf.localthrow(#projector.rolemap[projector.role],
                                            projector.role,
                                            new_roles,
                                            messages)"""
            throw_messages.extend(messages)
        else:
            catches.append(projector.nf.localcatch(
                               #projector.rolemap[projector.role],
                               projector.role,
                               #projector.rolemap[subj],
                               subj,
                               messages))
    if throw_messages:
        throw = projector.nf.localthrow(projector.role,
                                        new_roles,
                                        throw_messages)
    if (not block.is_empty()) or throw:
        # Section 5.3.5 -- if R is involved in the interruptible (if it is
        # involved in the block or is a thrower)
        return projector.nf.localinterruptible(
                   #projector.rolemap[projector.role], scope, block, throw, catches)
                   projector.role, scope, block, throw, catches)
    else:
        return None


def get_scope(node_):
    return get_scope_child(node_).getText()


def pretty_print(node_):
    text = constants.INTERRUPTIBLE_KW
    text = text + ':' + get_scope(node_)+ '\n'
    text = text + globalprotocolblock_pretty_print(get_block_child(node_)) + '\n'
    text = text + '{\n'
    for i in get_interrupt_children(node_):
        text = text + globalinterrupt_pretty_print(i) + '\n'
    text = text + '}'
    return text


def get_scope_child(node_):
    return node_.getChild(SCOPE_NAME_INDEX)

def get_block_child(node_):
    return node_.getChild(INTERRUPTIBLE_BLOCK_INDEX)

def get_interrupt_children(node_):
    return node_.getChildren()[INTERRUPTS_START_INDEX:]
