import sys

import scrib_constants as constants
import scrib_util as util

from moduleloader import load_modules as load_modules
from memberloader import load_members as load_members
from visibilitybuilder import build_visibility as build_visibility

from visit.context import Context as Context
from visit.projector import Projector as Projector
from visit.scopeinserter import ScopeInserter as ScopeInserter
from visit.unfolder import Unfolder as Unfolder
from visit.wellformednesschecker import \
    WellformednessChecker as WellformednessChecker
from visit.reachabilitychecker import ReachabilityChecker as ReachabilityChecker
from visit.subprotocolcollector import \
    SubprotocolCollector as SubprotocolCollector

from ast.module import (
    pretty_print as module_pretty_print,
    get_full_name as module_get_full_name,
    project as module_project,
    get_globalprotocoldecl_children as module_get_globalprotocoldecl_children
)

from ast.globel.globalprotocoldecl import (
    get_role_name as globalprotocoldecl_get_role_names,
    get_full_name as globalprotocoldecl_get_full_name,
    get_roledecllist_child as globalprotocoldecl_get_roledecllist_child
)

from ast.roledecllist import (
    get_roledecl_children as roledecllist_get_roledecl_children,
    get_rolemap as roledecllist_get_rolemap
)
    
from ast.roledecl import (
    get_role_name as roledecl_get_role_name,
    get_alias_name as roledecl_get_alias_name,
    get_declaration_name as roledecl_get_declaration_name
)

from ast.globel.globaldo import \
    get_projected_member_name as globaldo_get_projected_member_name


# Command line argument map keys
_SOURCE = '_SOURCE'
_IMPORT_PATH = '_IMPORT_PATH'
_PAYLOAD_TYPE_PATH = '_PAYLOAD_TYPE_PATH'
_PROJECT_PROTOCOL = 'PROJECT_PROTOCOL'
_PROJECT_ROLE = '_PROJECT_ROLE'
_PROJECT_DIR = '_PROJECT_DIR'


def main(argv, otherArg=None):
    args = _parse_command_line_args(sys.argv)
    if not args[_SOURCE]:
        util.report_error("No input file specified.")

    filepath = args[_SOURCE][0]  # The full module name as a string
                                 # FIXME: hardcoded to 0-index only
    importpath = args[_IMPORT_PATH]
    
    ext = util.parse_file_extension_from_filepath(filepath)
    if ext != constants.SCRIBBLE_FILE_EXTENSION:
        util.report_error("Bad file extension: " + ext)
    module_ = util.load_file_and_parse_module(filepath)
        # Returns an antlr3.tree.CommonTree with the module as the root

    # Section 4.2 -- module dependencies. Load all the modules that the target
    # module_ may depend on Initial Context is outside of the AST (no
    # parent/node) -- these fields are initialised on entering the AST from the
    # root module node
    context_ = Context(args[_IMPORT_PATH], args[_PAYLOAD_TYPE_PATH])
    context_ = load_modules(context_, filepath, module_)
    # TODO: import members not supported yet

    # Next passes can do transformations on the raw AST
    
    # Insert implicit scopes in each protocol of each module_
    context_ = _insert_scopes(context_)

    # Raw transformations finished; next record individual members (for
    # convenience -- currently only used by projection; ContextVisitor passes
    # use visibility)
    context_ = load_members(context_, filepath, module_)
    
    # Context built up to now is the base context. Subsequent ContextVisitor
    # passes each start from the base Context and build/manipulate the
    # pass-specific Context as appropriate
    
    # Section 4.2 -- well-formedness of primary module. Separately build the
    # visibility context_ for each dependency (it can be different for each) and
    # check the well-formedness conditions that must hold for each dependency

    # checks well-formedness conditions on each in-context_ module (these are
    # the loaded modules, which are the dependencies of the primary module)
    _check_wellformedness(context_)

    #context_ = _once_unfold_all(context_)
    #_check_wellformedness(context_)

    # Here the Context has only modules and members loaded, no
    # visibility built (Context was not retained from well-formedness checking).
    # The returned context_ holds all the projections
    context_ = _project_all(context_)

    # Check reachability at the local protocol level
    _check_reachability(context_)

    proto = args[_PROJECT_PROTOCOL]
    if proto is not None:
        localrole = args[_PROJECT_ROLE]
        dir = args[_PROJECT_DIR]
        #context_ = _project(context_, proto, localrole, dir)
        _output_projections_to_modules(context_, proto, localrole, dir)


# "Compiler" passes: scope insertion; well-formedness checking; projection

def _insert_scopes(context_):
    for fullname, module in context_.get_modules().items():
        si = ScopeInserter()
        new = si.insert_scopes(module)
        context_ = context_.replace_module(fullname, new)
    return context_


def _check_wellformedness(context_):
    for _, module_ in context_.get_modules().items():
        clone = context_.clone()
        # Gets fully qualified names of all visible entities
        clone = build_visibility(clone, module_)
        
        # Takes the prepared Context (modules loaded and visibility built etc.)
        # for a target module_ and checks the well-formedness conditions that
        # must hold for each member of the dependency set (Section 4.2) on this
        # target
        checker = WellformednessChecker(clone)
        checker.check_wellformedness(module_)
        #print "Checked module well-formedness:\n", module_pretty_print(module_)


"""def _once_unfold_all(context_):
    for _, module_ in context_.get_modules().items():
        clone = context_.set_current_module(module_get_full_name(module_))
        clone = build_visibility(clone, module_)
        for (proto, gpd) in clone.get_visible_globals().items():
            #full_global_name = globalprotocoldecl_get_full_name(gpd)
            #rdl = globalprotocoldecl_get_roledecllist_child(gpd)
            
            #print "b: ", proto 
            
            unfolder = Unfolder(clone)  # Context will be updated
            clone = unfolder.get_context()  # Get updated Context
            
            # FIXME: don't update Context like that, return something separate and update Context here 
            # FIXME: don't do unfold all -- unfold each protocol (global or local) when needed
            
            unfolder.once_unfold_all(gpd)
            
            #print "c: ", util.pretty_print(unfolder.get_context().get_rec_unfolding("X"))
    return context_"""


def _project_all(context_):
    for _, module_ in context_.get_modules().items():
        clone = context_.set_current_module(module_get_full_name(module_))
        clone = build_visibility(clone, module_)
        
        # FIXME: aliased member imports (visibility not working)
        #for (proto, gpd) in clone.get_visible_globals().items():
        for gpd in module_get_globalprotocoldecl_children(module_):  # OK to check only module's protos? cf. above
            proto = globalprotocoldecl_get_full_name(gpd)
            full_global_name = globalprotocoldecl_get_full_name(gpd)
            rdl = globalprotocoldecl_get_roledecllist_child(gpd)
            #rolemap = roledecllist_get_rolemap(rdl) 
            #for role_ in globalprotocoldecl_get_role_names(gpd):
            for rd in roledecllist_get_roledecl_children(rdl):
                dname = roledecl_get_declaration_name(rd)
                role_ = roledecl_get_role_name(rd)
                full_local_name = globaldo_get_projected_member_name(
                                      full_global_name, role_)
                                      #full_global_name, rolemap[role_])
                if context_.has_projection(full_local_name):
                    break
                projector = Projector()
                lpd = projector.project_globalprotocoldecl(clone, gpd, dname)#, rolemap)
                #full_name = lpd.get_full_name(clone)
                context_ = context_.add_projection(full_local_name, lpd)
                
                #print "Projected", full_global_name, "for", role_ + ":\n", \
                #      lpd.pretty_print()
    return context_


def _check_reachability(context_):
    for proto, lpd in context_.get_projections().items(): 
        local_module_name = util.get_full_module_name_from_full_member_name(
                                proto)
        clone = context_.set_current_module(local_module_name)
        rc = ReachabilityChecker(clone)
        tmp = rc.check_reachability(lpd)


def _output_projections_to_modules(context_, target_globalname, localrole, dir):
    members = context_.get_members()
    if target_globalname not in members.keys():
        util.report_error("[Projection] Unknown protocol: " + \
                          target_globalname) #+ ", " + str(members))
    
    gpd = context_.get_member(target_globalname)
    if util.get_node_type(gpd) != constants.GLOBAL_PROTOCOL_DECL_NODE_TYPE:
        util.report_error("[Projection] Not a global protocol declaration: " +
                          target_globalname)
    if localrole not in globalprotocoldecl_get_role_names(gpd):
        util.report_error("[Projection] Projection role not declared: " + localrole)

    target_localname = globaldo_get_projected_member_name(target_globalname,
                                                          localrole)
    todo = [target_localname]
    lpd = context_.get_projection(target_localname)
    subprotos = SubprotocolCollector(context_).collect_subprotocols(lpd, True)
    todo.extend(subprotos)
        # Includes target_globalname (even if not used recursively)
    
    # Write each subprotocol to a separately projected module
    for subproto in todo:
        globalmodulename = \
            util.get_global_module_name_from_projected_member_name(subproto)
            # FIXME: not working if member/role names contain underscores; but
            # good to run subprotocol collection on local protocol. best way may
            # be to record a mapping between projected names and the global/role
            # names they come from
        globalmodule = context_.get_module(globalmodulename)
        projector = Projector()
        lm = projector.project_module(context_, globalmodule, subproto, todo)
            # subproto is the full local name
        lm = lm.addlocalprotocoldecl(context_.get_projection(subproto))

        fmn = lm.get_full_name()
        filepath = None
        if dir is None:
            # FIXME: factor out with e.g. globaldo and importmodule projection
            filename = util.get_simple_module_name_from_full_module_name(fmn) \
                       + '.' + constants.SCRIBBLE_FILE_EXTENSION
            sp = context_.get_source(globalmodulename)
            filepath = util.parse_directory_from_filepath(sp) + '/' + filename
                # FIXME: double slashes being introduced somewhere
        else:
            filepath = dir + '/' + \
                           util.convert_full_module_name_to_filepath(fmn) 
        _write_module(lm, filepath)
                       
        """print '[DEBUG] Projection of ' + target_globalname + ' for ' + \
                    localrole + ':\n', lpd.pretty_print()"""


def _write_module(m, filepath):
    util.write_to_file(filepath, m.pretty_print())


def _parse_command_line_args(argv):  # Could use argparse (or ANTLR)
    args = { _SOURCE: [], _IMPORT_PATH: [], _PAYLOAD_TYPE_PATH: [],
             _PROJECT_PROTOCOL: None, _PROJECT_DIR: None }
    if len(argv) > 1:
        iter = argv[1:].__iter__()
        for arg in iter:
            if arg == '-ip' or arg == '-importpath':  # Factor out constants
                path = iter.next().split(';')
                args[_IMPORT_PATH].extend(path)
            elif arg == '-pp' or arg == '-payloadpath':
                path = iter.next().split(';')
                args[_PAYLOAD_TYPE_PATH].extend(path)
            elif arg == '-project':
                args[_PROJECT_PROTOCOL] = iter.next()
                args[_PROJECT_ROLE] = iter.next()
            elif arg == '-o':
                args[_PROJECT_DIR] = iter.next()
            else:
                if arg.startswith('-'):
                    util.report_error("Bad argument flag: " + arg)
                if len(args[_SOURCE]) > 0:
                    util.report_error("Specify a single module: " + arg)
                args[_SOURCE].append(arg)
    if '.' not in args[_IMPORT_PATH]:  # factor out current directory
        args[_IMPORT_PATH].append('.')
    return args


##########################################################################
# Call main
if __name__ == '__main__':
    main(sys.argv)
###########################################################################
