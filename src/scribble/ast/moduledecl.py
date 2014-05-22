import scrib_constants as constants
import scrib_util as util

from ast.node import Node as Node


MODULE_NAME_SEPARATOR = '.'


class ModuleDecl(Node):
    #fmn = None  # string

    #def __init__(self, decl, importmodules, importmembers, payloads, globalps, localps):
    def __init__(self, fmn):
        super(ModuleDecl, self).__init__()
        self.fmn = fmn
        
    def get_full_name(self):
        return self.fmn

    def pretty_print(self):
        return constants.MODULE_KW + ' ' + self.fmn + ';'


def traverse(traverser, node_):
    return node_


def check_wellformedness_enter(checker, node_):
    # Check source file is in the package at compile-time? (Java doesn't) ---
    # currently only check source file location for deployment purposes
    fmn = get_full_name(node_)
        # loadMembers has checked package name is correct?
    context_ = checker.get_context().push(node_)
    context_ = context_.set_current_module(fmn)
    checker.set_context(context_)

    # If we get here, it means the tool front end (Main.py) managed to find a
    # parseable Scribble module for a given file path (either a command line
    # argument or derived from an import module/member) -- but the module
    # declaration of that module has not been checked yet against the filepath
    #
    # Here we check the simple module name against the filename, as a standalone
    # condition on the module itself, but not the full module name against the
    # current directory location -- leave this as a deployment principle for
    # run-time (despite the fact that the same module path scheme is used for
    # compile-time loading -- in principle, doesn't have to be though)
    #
    # Section 4.2 -- Simple moduledecl name and filename of module
    filepath = context_.get_source(fmn)
        # Full path relative to "working directory"
    check_filename(filepath, node_)


def check_wellformedness_visit(checker, node):
    return node

def check_wellformedness_leave(checker, node):
    pass


# Not a "full projection": prepares the projected module container for the
# projected protocol(s)
def project(projector, node_):
    gfmn = get_full_name(node_)
    lfmn = gfmn + '_' + projector.get_protocol() + '_' + projector.role
        # FIXME: factor out name mangling
    new = projector.nf.moduledecl(lfmn)
    return new


# Not currently checking the main module is in the right directory according to
# the full name (but dependencies will be searched in the specified directories)
# -- sort of Java-style
def check_filename(filepath, moduledecl_):
    smn_from_filepath = util.parse_simple_module_name_from_filepath(filepath)
    fmn_from_moduledecl = get_full_name(moduledecl_)
    smn_from_moduledecl = util.get_simple_module_name_from_full_module_name(fmn_from_moduledecl)

    if smn_from_filepath != smn_from_moduledecl:
        util.report_error("Bad module declaration/file name: declaration=" + \
                          smn_from_moduledecl + ", path=" + filepath)


def pretty_print(node_):
    return constants.MODULE_KW + ' ' + get_full_name(node_) + ';'


# returns the full name
def get_full_name(node_):
    return util.parse_dot_separated_name_from_node_list(node_.getChildren())
