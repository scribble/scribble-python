import scrib_util as util

import ast.payload as payload


EMPTY_MESSAGE_OP = 'EMPTY_MESSAGE_OP'


OPERATOR_CHILD = 0
PAYLOAD_CHILD = 1


def traverse(traverser, node_):
    traversed = []
    op = get_operator_child(node_)
    payload = get_payload_child(node_)
    traversed.append(traverser.traverse_untyped_leaf(op))
    traversed.append(traverser.traverse(payload))
    new = util.antlr_dupnode_and_replace_children(node_, traversed)
    return new
    

# An auxiliary function, not directly called by the Visitor pattern
# Updates checker, void return (as for main WellformednessChecker visitor -- node_ is not modified)
def check_wellformedness(checker, node_):
    payload_ = get_payload_child(node_)
    #context = payloadList.checkpayloadListWellformedness(context, payloads)
    payload.check_wellformedness(checker, payload_)


def get_operator(node_):
#def getOperator(node_):
    return get_operator_child(node_).getText()


def get_operator_child(node_):
    return node_.getChild(OPERATOR_CHILD)

def get_payload_child(node_):
#def getpayloadChild(node_):
    return node_.getChild(PAYLOAD_CHILD)


def pretty_print(node_):
    text = ''
    op = get_operator(node_)
    if op != EMPTY_MESSAGE_OP:
        text = text + op
    text = text + '('
    payloads = get_payload_child(node_)
    if payloads != None:
        text = text + payload.pretty_print(payloads)
    text = text + ')'
    return text
