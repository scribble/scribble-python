import scrib_constants as constants
import scrib_util as util

from ast.node import Node as Node

from ast.argument import (
    get_arg_child as argument_get_arg_child,
    get_arg as argument_get_arg,
    has_parameter_child as argument_has_parameter_child,
    get_parameter as argument_get_parameter,
    pretty_print as argument_pretty_print
)

from ast.messagesignature import \
    check_wellformedness as messagesignature_check_wellformedness

from ast.parameterdecl import (
    get_kind as parameterdecl_get_kind,
    get_declaration_name as parameterdecl_get_declaration_name,
    get_parameter_name as parameterdecl_get_name
)

from ast.parameterdecllist import \
    get_parameterdecl_children as parameterdecllist_get_parameterdecl_children

from ast.globel.globalprotocoldecl import \
    get_parameterdecllist_child as \
    globalprotocoldecl_get_parameterdecllist_child


EMPTY_ARGUMENT_LIST = 'EMPTY_ARGUMENT_LIST'


class ArgumentList(Node):
    #args = None  # [ argument ]

    def __init__(self, args):
        super(ArgumentList, self).__init__()
        self.args = args



def traverse(traverser, node_):
    traversed = []
    for child in get_argument_children(node_):
        traversed.append(traverser.traverse(child))
    new = util.antlr_dupnode_and_replace_children(node_, traversed)
    return new


# Section 4.6.3 -- well-formed argument list
#
# Like roleinstantiationlist, not in the Visitor pattern directly: argumentlist
# used by both globaldo and GlobalInstantiation (i.e. different parents), more
# convenient to factor out in this way -- also, no traverse
def check_wellformedness(checker, target, node_):
    context_ = checker.get_context()

    tree = context_.get_visible_global(target)
    pdl = globalprotocoldecl_get_parameterdecllist_child(tree)
    paramlist = parameterdecllist_get_parameterdecl_children(pdl)

    # Section 4.6.3 -- lengths of argument list and parameter decl list are the
    # same
    args = get_argument_children(node_)
    if len(args) != len(paramlist):  # This check includes empty lists
        util.report_error("Bad number of arguments, expected: " + \
                          str(len(paramlist)))

    argmap = {}  # params -> args (args are the MESSAGESIGNATURE nodes)
    params = paramlist.__iter__()
    for argpair in args:
    #{
        # FIXME: tidy up usage of argpair and arg
        #arg = argument.get_arg(argpair)
        arg = argument_get_arg_child(argpair)
        targ_pd = params.next()

        # Section 4.6.3 -- for each argument, one of the two cases must hold:
        kind = parameterdecl_get_kind(targ_pd)
        #if kind == constants.SIGKW:  # HACK: KW constant
        # Section 4.6.3 -- case (1): the target parameter is a sig parameter
        if kind == constants.KIND_MESSAGE_SIGNATURE:
            # Should annotations be allowed here?
            if util.get_node_type(arg) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
                # Section 4.6.3 -- the argument should be a well-formed
                # message-signature
                messagesignature_check_wellformedness(checker, arg)
                    # Well-formed message-signature
            else:
              # Section 4.6.3 -- the argument should be a bound sig parameter
                #util.report_error('Expected sig argument: ' + arg)
                param = argument_get_arg(argpair)
                if param not in context_.get_parameters().keys():
                    # The argument isn't a valid parameter
                    util.report_error("Bad argument : " + param)
                #if context_.get_parameter(param) != constants.SIGKW:
                if context_.get_parameter(param) != \
                        constants.KIND_MESSAGE_SIGNATURE:
                    util.report_error("Expected sig parameter: " + param)
            ##argmap[parameter.get_parameter_name(params.next())] = arg
        #elif kind == constants.TYPEKW:
        # Section 4.6.3 -- case (2): the target parameter is a type parameter
        elif kind == constants.KIND_PAYLOAD_TYPE:
            # Section 4.6.3 -- the argument should be a visible payload or a
            # bound type parameter
            val = argument_get_arg(argpair)
            if val not in context_.get_visible_payloads():
                # FIXME: factor out with payload
                #if context_.get_current_module() + '.' + val in context_.get_visible_payloads():
                if val not in context_.get_parameters().keys():
                    util.report_error("Bad argument: " + val)
                ##if not(context_.get_parameter(val) == constants.TYPEKW):
                if context_.get_parameter(val) != constants.KIND_PAYLOAD_TYPE:
                    util.report_error("Expected type parameter: " + val)
        else:
            raise Exception("Shouldn't get in here: " + kind)

        # Section 4.6.3 -- argument parameter must match the declared parameter
        # in the target protocol declaration
        if argument_has_parameter_child(argpair):
            theirs = argument_get_parameter(argpair)
            if theirs != parameterdecl_get_name(targ_pd):
                util.report_error("Bad role parameter: " + theirs)

        argmap[parameterdecl_get_declaration_name(targ_pd)] = arg
    #}
    return argmap


def get_argument_map(context_, target, node_):
    argmap = {}  # params -> args (string name -> MESSAGESIGNATURE node)
    tree = context_.get_visible_global(target)
    pdl = globalprotocoldecl_get_parameterdecllist_child(tree)
    paramlist = parameterdecllist_get_parameterdecl_children(pdl)
    params = paramlist.__iter__()
    args = get_argument_children(node_)
    for argpair in args:
        arg = argument_get_arg_child(argpair)
        targ_pd = params.next()
        argmap[parameterdecl_get_declaration_name(targ_pd)] = arg
    return argmap

def is_empty(node_):
    return util.get_node_type(node_) == EMPTY_ARGUMENT_LIST

def get_argument_args(node_):
    children = get_argument_children(node_)
    args = []
    for child in children:
        args.append(argument_get_arg(child))
    return args


def pretty_print(node_):
    args = get_argument_children(node_)
    text = ""
    if args:
        text = '<' + argument_pretty_print(args[0])
        for a in args[1:]:
            text = text + ', '
            text = text + argument_pretty_print(a)
        text = text + '>'
    return text


def get_argument_children(node):
    return node.getChildren()
