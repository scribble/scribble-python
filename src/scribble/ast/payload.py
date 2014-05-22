import scrib_constants as constants
import scrib_util as util

from ast.payloadelement import (
    get_annotation as payloadelement_get_annotation,
    get_type as payloadelement_get_type,
    EMPTY_ANNOTATION as payloadelement_EMPTY_ANNOTATION,
    pretty_print as payloadelement_pretty_print
)


##
# For message sig payloads


def traverse(traverser, node_):
    traversed = []
    for child in get_payloadelement_children(node_):
        traversed.append(traverser.traverse(child))
    new = util.antlr_dupnode_and_replace_children(node_, traversed)
    return new


# An auxiliary function, not directly called by the Visitor pattern
#
# Updates checker, void return (as for main WellformednessChecker visitor --
# node_ is not modified)
def check_wellformedness(checker, node_):
    context = checker.get_context()

    payloads = get_payloadelement_children(node_)
    for payload in payloads:
        annot = payloadelement_get_annotation(payload)
        payloadtype = payloadelement_get_type(payload)

        # TODO: annotation well-formedness will be further specified in langref
        # when annotations framework is added
        if annot != payloadelement_EMPTY_ANNOTATION:
            # Section 4.6.2 -- distinct annotation names
            if annot in context.get_annotationss():
                util.report_error("Bad annotation: " + annot)
            context = context.add_annotation(annot)

      # Section 4.5 -- Visible payload types
        if payloadtype not in context.get_visible_payloads().keys():
            # "type" parameters
            # Section 4.5 -- Bound (type) parameter
            if payloadtype not in context.get_parameters().keys():
                util.report_error("Bad payload type: " + payloadtype)
            # Section 4.5 -- type parameter
            if context.get_parameter(payloadtype) != \
                    constants.KIND_PAYLOAD_TYPE:
                util.report_error("Bad payload type parameter: " + \
                                  payloadtype)
    checker.set_context(context)


def pretty_print(node_):
    text = ""
    pes = get_payloadelement_children(node_)
    if pes:
        text = payloadelement_pretty_print(pes[0])
        for child in pes[1:]:
            text = text + ', '
            text = text + payloadelement_pretty_print(child)
    return text


def get_payloadelement_children(node_):
    return node_.getChildren()
