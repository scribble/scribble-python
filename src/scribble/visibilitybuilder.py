##
# Section 4.1.1 -- Visible modules and module Members

# TODO: member imports
#
# Could fit into Visitor/Traverser pattern, but quite simple so mabe unnecessary


import scrib_constants as constants
import scrib_util as util

from ast.importmodule import (
    get_full_module_name as importmodule_get_full_module_name,
    get_declaration_name as importmodule_get_declaration_name
)

from ast.module import (
    get_moduledecl_child as module_get_moduledecl_child,
    get_importmember_children as module_get_importmember_children,
    get_importmodule_children as module_get_importmodule_children,
    get_payloadtypedecl_children as module_get_payloadtypedecl_children,
    get_globalprotocoldecl_children as \
        module_get_globalprotocoldecl_children,
    get_localprotocoldecl_children as module_get_localprotocoldecl_children
)

from ast.moduledecl import get_full_name as moduledecl_get_full_name

from ast.payloadtypedecl import \
    get_declaration_name as payloadtypedecl_get_declaration_name

from ast.globel.globalprotocoldecl import \
    get_name as globalprotocoldecl_get_name

from ast.local.localprotocoldecl import \
    get_name as localprotocoldecl_get_name


# Precondition: no visibility built in the context object yet, including the
# primary module
def build_visibility(context, module_):
    fullname = moduledecl_get_full_name(module_get_moduledecl_child(module_))
    # Build visibility wrt. primary module_
    context = context.add_visible_module(fullname, module_)
    context = _get_module_members(context, fullname, module_)
    # Section 4.1.1 -- self reference of module_ by simple module_ name
    smn = util.get_simple_module_name_from_full_module_name(fullname)
    if fullname != smn:
        context = context.add_visible_module(smn, module_)
        #context = _get_module_members(context, smn, module_)
            # No: members of primary module_ are not accessible via the simple
            # name of module_

    # add on unqualified names for ``local'' module_ entities (i.e.\ for the
    # primary module_ only)
    context = _get_self_visibility(context, module_)

    # Build visibility wrt. imported modules
    context = _get_imported_modules(context, module_)
    #context = getImportedMembers(context, module_) # TODO
    return context


def _get_imported_modules(context, module_):
    importmodules = module_get_importmodule_children(module_)
    for im in importmodules:
        fn = importmodule_get_full_module_name(im)
        # Distinct names already checked
        dn = importmodule_get_declaration_name(im)
        m = context.get_module(fn)

        # Section 4.1.1 -- imported module_ referred to by declaration name
        
        # FIXME: transitively import modules -- not working for project all (and do well-formedness?)
        if dn not in context.get_visible_modules().keys():
            context = context.add_visible_module(dn, m)
            context = _get_module_members(context, dn, m)
    return context


# Section 4.1.1 -- members accessed via the declaration names of (visible) modules
#
# (For self module_, "declaration name" is assumed to mean the full name, i.e.
# the name declared by the moduledecl)
#
# Same or very similar in memberloader
def _get_module_members(context, dn, module_):
    for ptd in module_get_payloadtypedecl_children(module_):
        n = payloadtypedecl_get_declaration_name(ptd)
        f = dn + '.' + n
        context = context.add_visible_payload(f, ptd)
        #context = context.add_visible_payload(n, ptd)
    for gpd in module_get_globalprotocoldecl_children(module_):
        n = globalprotocoldecl_get_name(gpd)
        f = dn + '.' + n
        context = context.add_visible_global(f, gpd)
        #context = context.add_visible_global(n, gpd)
    for lpd in module_get_localprotocoldecl_children(module_):
        n = localprotocoldecl_get_name(lpd)
        f = dn + '.' + n
        context = context.add_visible_local(f, lpd)
        #context = context.add_visible_local(n, gpd)
    importmembers = module_get_importmember_children(module_)
    for im in importmembers:
        util.report_error("TODO member import: " + im)
        # TODO: members
    return context
#}


# Section 4.1.1 -- members of primary module_ accessed by their simple names
def _get_self_visibility(context, module_):
    for ptd in module_get_payloadtypedecl_children(module_):
        n = payloadtypedecl_get_declaration_name(ptd)
        context = context.add_visible_payload(n, ptd)
    for gpd in module_get_globalprotocoldecl_children(module_):
        n = globalprotocoldecl_get_name(gpd)
        context = context.add_visible_global(n, gpd)
    for lpd in module_get_localprotocoldecl_children(module_):
        n = localprotocoldecl_get_name(lpd)
        context = context.add_visible_local(n, lpd)
    importmembers = module_get_importmember_children(module_)
    for im in importmembers:
        util.report_error("TODO: member import: " + im)
        # FIXME: members
    return context
