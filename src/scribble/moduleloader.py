# For loading all potential module dependencies of a module

import scrib_constants as constants
import scrib_util as util

from visit.context import Context as Context

from ast.importmodule import \
    get_full_module_name as importmodule_get_full_module_name

from ast.module import (
    get_moduledecl_child as module_get_moduledecl_child,
    get_importmember_children as module_get_importmember_children,
    get_importmodule_children as module_get_importmodule_children,
    get_payloadtypedecl_children as module_get_payloadtypedecl_children,
    get_globalprotocoldecl_children as module_get_globalprotocoldecl_children,
    get_localprotocoldecl_children as module_get_localprotocoldecl_children
)

from ast.moduledecl import (
    check_filename as moduledecl_check_file_name,
    get_full_name as moduledecl_get_full_name
)

from ast.payloadtypedecl import \
    get_declaration_name as payloadtypedecl_get_declaration_name

from ast.globel.globalprotocoldecl import \
    get_name as globalprotocoldecl_get_name

from ast.local.localprotocoldecl import \
    get_name as localprotocoldecl_get_name


# Section 4.2 -- dependencies of the primary module
def load_modules(context_, filepath, module_):
    return _add_module_and_get_dependencies(context_, filepath, module_)


def _add_module_and_get_dependencies(context_, filepath, current):
    # Section 4.2 -- Simple moduledecl name and filename of module
    #
    # Move to well-formedness? (Currently also checked for well-formed
    # moduledecl, but commenting this line here causes some problems for
    # mutually recursive imports -- should debug this)
    moduledecl_ = module_get_moduledecl_child(current)
    moduledecl_check_file_name(filepath, moduledecl_)
    fmn = moduledecl_get_full_name(moduledecl_)

    context_ = context_.add_source(fmn, filepath)
    # Make a combined add_source and add_module method for Context? (And move the
    # above name check into there)
    context_ = context_.add_module(fmn, current)
    #context_ = _add_all_members(context_, fmn, current)
        # Done later by memberloader

    importmodules = module_get_importmodule_children(current)
    for i in importmodules:
        fmn = importmodule_get_full_module_name(i)
        # sources and modules keys should match
        if fmn not in context_.get_modules().keys():
            tmp = util.convert_full_module_name_to_filepath(fmn)
            filepath = util.search_importpath_for_file(context_.import_path,
                                                       tmp)
            module_ = util.load_file_and_parse_module(filepath)
            #  # We found a parseable Scribble module at that file path -- but
            #  module decl not checked yet (checked by well-formedness, along
            #  with other well-formedness conditions) We found a parseable
            #  Scribble module at that file path -- but module decl not checked
            #  yet (checked by well-formedness, along with other well-formedness
            #  conditions)
            context_ = _add_module_and_get_dependencies(context_,
                                                        filepath,
                                                        module_)
    """importmembers = module.module_get_importmember_children(current)  # TODO: member imports"""

    return context_


"""# Same structure as visibilitybuilder.get_moduleMembers
def _add_all_members(context_, fmn, module_):
    for ptd in module_get_payloadtypedecl_children(module_):
        n = payloadtypedecl_get_declaration_name(ptd)
        f = fmn + '.' + n
        context_ = context_.add_member(f, ptd)
    for gpd in module_get_globalprotocoldecl_children(module_):
        n = globalprotocoldecl_get_name(gpd)
        f = fmn + '.' + n
        context_ = context_.add_member(f, gpd)
    for lpd in module_get_localprotocoldecl_children(module_):
        n = localprotocoldecl_get_name(lpd)
        f = fmn + '.' + n
        context_ = context_.add_member(f, lpd)
    importmembers = module_get_importmember_children(module_)
    for im in importmembers:
        # TODO: members
        util.report_error("TODO member import: " + im)
    return context_"""
