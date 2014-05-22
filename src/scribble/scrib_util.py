import os
import sys

from antlr3 import (
    ANTLRFileStream as ANTLRFileStream,
    CommonTokenStream as CommonTokenStream,
    RecognitionException as RecognitionException
)

from ScribbleLexer import ScribbleLexer as ScribbleLexer
from ScribbleParser import ScribbleParser as ScribbleParser

import scrib_constants as constants

from visit.commonerrornodechecker import \
    CommonErrorNodeChecker as CommonErrorNodeChecker

from ast.globel.globalprotocoldef import \
    pretty_print as globalprotocoldef_pretty_print
from ast.globel.globalprotocolblock import \
    pretty_print as globalprotocolblock_pretty_print
from ast.globel.globalchoice import \
    pretty_print as globalchoice_pretty_print
from ast.globel.globalcontinue import \
    pretty_print as globalcontinue_pretty_print
from ast.globel.globaldo import \
    pretty_print as globaldo_pretty_print
from ast.globel.globalinterruptible import \
    pretty_print as globalinterruptible_pretty_print
from ast.globel.globalmessagetransfer import \
    pretty_print as globalmessagetransfer_pretty_print
from ast.globel.globalparallel import \
    pretty_print as globalparallel_pretty_print
from ast.globel.globalrecursion import \
    pretty_print as globalrecursion_pretty_print

from ast.local.localsend  import pretty_print as localsend_pretty_print
from ast.local.localreceive  import pretty_print as localreceive_pretty_print
"""from ast.local.localchoice import \
    pretty_print as localchoice_pretty_print
from ast.local.localcontinue import \
    pretty_print as localcontinue_pretty_print
from ast.local.localdo import \
    pretty_print as localdo_pretty_print
from ast.local.localinterruptible import \
    pretty_print as localinterruptible_pretty_print
from ast.local.localmessagetransfer import \
    pretty_print as localmessagetransfer_pretty_print
from ast.local.localparallel import \
    pretty_print as localparallel_pretty_print
from ast.local.localrecursion import \
    pretty_print as localrecursion_pretty_print"""

from visit.unfolder import Unfolder as Unfolder


"""def getCurrentFunctionName():
    return sys._getframe(1).f_code.co_name"""


# AST node "type" functions

def get_node_type(node_):
    return node_.getText()  # gets the token text?

def set_node_type(node_, type_):
    node_.token.setText(type_)

def filter_node_types(nodes, type_):
    res = []
    for node_ in nodes:
        if get_node_type(node_) == type_:
            res.append(node_)
    return res


# Duplicate an ANTLR node (shallow clone -- and may be currently incomplete)
def antlr_dupnode_and_replace_children(node_, children):
    clone = node_.dupNode()
    for child in children:
        clone.addChild(child)
    clone.setParent(node_.getParent())
    # How about text and token fields?
    return clone


##
# Tool feedback

def report_warning(message):
    print message

def report_error(message):
    print message
    sys.exit(0)  # Not a failure


def search_importpath_for_file(importpath, filepath):
    path = None
    found = False
    for ip in importpath:
        path = ip + '/' + filepath
        if os.path.isfile(path):
            try:
                open(path)
                found = True
                return path
            except IOError as e:
                pass
    if not found:
        report_error("File not found: " + filepath)


# Read Scribble file
def load_file_and_parse_module(filepath):
    try:
        char_stream = ANTLRFileStream(filepath)
        lexer = ScribbleLexer(char_stream)
        tokens = CommonTokenStream(lexer)
        parser = ScribbleParser(tokens)
        tree = parser.module().tree
        checker = CommonErrorNodeChecker()
        checker._check_for_errornode(tree)
        return tree
    except IOError as e:
        print e
        sys.exit(1)
    except RecognitionException as e:
        print e
        sys.exit(1)
    # except Exception as e:  # Failed parse doesn't seem to throw any exceptions
        # traceback.print_stack()
    

def write_to_file(filepath, text):
    try:
        if filepath.find('/') != -1 or filepath.find('\\') != -1:
            d = os.path.dirname(filepath)
            if not os.path.exists(d):
                os.makedirs(d)
        
        with open(filepath, 'w') as file:
            file.write(text)
    except Exception as e:
        print "Write to file failed: ", e
        sys.exit(1)


##
# Filepath helpers

def parse_file_extension_from_filepath(filepath):
    return filepath[filepath.rfind('.') + 1:]

def parse_directory_from_filepath(filepath):
    if filepath.find('/') != -1:
        return filepath[:filepath.rfind('/')]
    elif filepath.find('\\') != -1:
        return filepath[:filepath.rfind('\\')]
    else:
        return '.'


##
# Conversion between module names and filepaths 

def convert_full_module_name_to_filepath(fmn):
    return fmn.replace('.', '/') + '.' + constants.SCRIBBLE_FILE_EXTENSION

def parse_simple_module_name_from_filepath(filepath):
    ext = parse_file_extension_from_filepath(filepath)
    if ext != constants.SCRIBBLE_FILE_EXTENSION:
        report_error("Bad file extension: " + ext)

    dirsep = '/'
    if filepath.find('\\') != -1:  # HACK: for Windows paths
        dirsep = '\\'
    module = filepath[filepath.rfind(dirsep) + 1:filepath.rfind('.')]
    return module


##
# module and member name helpers

def get_simple_module_name_from_full_module_name(fullname):
    if fullname.find('.') == -1:
        return fullname
    else:
        return fullname[fullname.rfind('.') + 1:]

def get_full_module_name_from_full_member_name(fullname):
    return fullname[:fullname.rfind('.')]

def get_simple_member_name_from_full_member_name(fullname):
    return fullname[fullname.rfind('.') + 1:]

# converse to globaldo.get_projected_member_name
#
# FIXME: broken for names with underscores
def get_global_module_name_from_projected_member_name(localname):
    tmp = get_full_module_name_from_full_member_name(localname)
    tmp = tmp[:tmp.rfind('_')]
    tmp = tmp[:tmp.rfind('_')]
    return tmp


# Assembles a list of "name nodes" into one dot-separated name (the name "parse"
# is not suitable)
def parse_dot_separated_name_from_node_list(nodes):
    name = nodes[0].getText()
    for n in nodes[1:]:
        name = name + '.' + n.getText()
    return name


# TODO: make a proper PrettyPrint visitor, with support for indenting
def pretty_print(node_):
    ntype = get_node_type(node_)
    if ntype == constants.GLOBAL_PROTOCOL_DEF_NODE_TYPE:
        return globalprotocoldef_pretty_print(node_)
    elif ntype == constants.GLOBAL_PROTOCOL_BLOCK_NODE_TYPE:
        return globalprotocolblock_pretty_print(node_)
    elif ntype == constants.GLOBAL_MESSAGE_TRANSFER_NODE_TYPE:
        return globalmessagetransfer_pretty_print(node_)
    elif ntype == constants.GLOBAL_CHOICE_NODE_TYPE:
        return globalchoice_pretty_print(node_)
    elif ntype == constants.GLOBAL_RECURSION_NODE_TYPE:
        return globalrecursion_pretty_print(node_)
    elif ntype == constants.GLOBAL_CONTINUE_NODE_TYPE:
        return globalcontinue_pretty_print(node_)
    elif ntype == constants.GLOBAL_PARALLEL_NODE_TYPE:
        return globalparallel_pretty_print(node_)
    elif ntype == constants.GLOBAL_DO_NODE_TYPE:
        return globaldo_pretty_print(node_)
    elif ntype == constants.GLOBAL_INTERRUPTIBLE_NODE_TYPE:
        return globalinterruptible_pretty_print(node_)
    elif ntype == constants.LOCAL_SEND_NODE_TYPE:
        return localsend_pretty_print(node_)
    elif ntype == constants.LOCAL_RECEIVE_NODE_TYPE:
        return localreceive_pretty_print(node_)
    elif ntype == constants.LOCAL_CHOICE_NODE_TYPE:
        return localchoice_pretty_print(node_)
    elif ntype == constants.LOCAL_RECURSION_NODE_TYPE:
        return localrecursion_pretty_print(node_)
    elif ntype == constants.LOCAL_CONTINUE_NODE_TYPE:
        return localcontinue_pretty_print(node_)
    elif ntype == constants.LOCAL_PARALLEL_NODE_TYPE:
        return localparallel_pretty_print(node_)
    elif ntype == constants.LOCAL_DO_NODE_TYPE:
        return localdo_pretty_print(node_)
    elif ntype == constants.LOCAL_INTERRUPTIBLE_NODE_TYPE:
        return localinterruptible_pretty_print(node_)
    else:
        raise Exception("TODO: ", ntype)


# Misc

def replace_in_list(l, map):
    ll = []
    for x in l:
        if x in map.keys():
            ll.append(map[x])
        else:
            ll.append(x)
    return ll




def unfold_once(context_, node_):
    unfolder = Unfolder(context_)  # Context will be updated
    return unfolder.once_unfold_all(node_)
