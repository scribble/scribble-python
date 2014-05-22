import scrib_util as scrib_util

from ast.node import Node as Node

from ast.parameterdecl import (
    get_kind as parameterdecl_get_kind,
    get_declaration_name as parameterdecl_get_declaration_name,
    pretty_print as parameterdecl_pretty_print,
    get_parameter_name as parameterdecl_get_parameter_name
)


EMPTY_PARAMETER_DECL_LIST = 'EMPTY_PARAMETER_DECL_LIST'


class ParameterDeclList(Node):
    #paramdecls = None  # [ parameterdecl ]

    def __init__(self, paramdecls):
        super(ParameterDeclList, self).__init__()
        self.paramdecls = paramdecls
        
    def get_parameter_names(self):
        params = []
        for pd in self.paramdecls:
            params.append(pd.name)
        return params

    def pretty_print(self):
        text = '<'
        first = True
        for pd in self.paramdecls:
            if not(first):
                text = text + ', '
            text = text + pd.pretty_print()
            first = False
        text = text + '>'
        return text


def traverse(traverser, node_):
    return node_


def context_visitor_enter(cv, node_):
    context_ = cv.get_context()
    for pd in get_parameterdecl_children(node_):
        kind = parameterdecl_get_kind(pd)
        param = parameterdecl_get_declaration_name(pd)
        context_ = context_.add_parameter(param, kind)  # Section 4.6.1
    cv.set_context(context_)  # No push/enter
    
    
def context_visitor_visit(cv, node_):
    return node_
    
def context_visitor_leave(cv, node_):
    #cv.leave(node_)  # No push/enter, so no pop/leave
    pass
    
    
def check_wellformedness_enter(checker, node_):
    context_ = checker.get_context()
    parameters = []
    for pd in get_parameterdecl_children(node_):
        kind = parameterdecl_get_kind(pd)
        param = parameterdecl_get_declaration_name(pd)
        # Section 4.6 -- Global protocol header: distinct param declaration
        # names
        if param in parameters or \
                param in context_.get_visible_payloads().keys():
            scrib_util.report_error("Bad param declaration name: " + \
                                    param)
        parameters.append(param)


def check_wellformedness_visit(checker, node_):
    return node_


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    pds = []
    for pd in get_parameterdecl_children(node_):
        pds.append(projector.visit(pd))
    return projector.nf.parameterdecllist(pds)


def get_parameter_names(node_):
    # Not aliases (for projection and role instantiation)
    params = []
    for pd in get_parameterdecl_children(node_):
        params.append(parameterdecl_get_parameter_name(pd))
    return params


# TODO: factor out with above object method
def pretty_print(node_):
    pds = get_parameterdecl_children(node_)
    text = '<' + parameterdecl_pretty_print(pds[0])
    for pd in pds[1:]:
        text = text + ', '
        text = text + parameterdecl_pretty_print(pd)
    text = text + '>'
    return text


def get_parameterdecl_children(node_):
    return node_.getChildren()
