import scribble.scrib_constants as constants
import scribble.scrib_util as util

from scribble.ast.importmodule import ImportModule as ImportModule
from scribble.ast.module import Module as Module
from scribble.ast.moduledecl import ModuleDecl as ModuleDecl
from scribble.ast.payloadtypedecl import payloadTypeDecl as payloadTypeDecl
from scribble.ast.roledecl import RoleDecl as RoleDecl
from scribble.ast.roledecllist import RoleDeclList as RoleDeclList
from scribble.ast.parameterdecl import ParameterDecl as ParameterDecl
from scribble.ast.parameterdecllist import ParameterDeclList as ParameterDeclList
from scribble.ast.roleinstantiation import RoleInstantiation as RoleInstantiation
from scribble.ast.roleinstantiationlist import RoleInstantiationList as \
        RoleInstantiationList
from scribble.ast.argument import Argument as Argument
from scribble.ast.argumentlist import ArgumentList as ArgumentList

from scribble.ast.local.localprotocoldecl import LocalProtocolDecl as LocalProtocolDecl
from scribble.ast.local.localprotocoldef import LocalProtocolDef as LocalProtocolDef
from scribble.ast.local.localprotocolblock import LocalProtocolBlock as \
        LocalProtocolBlock
from scribble.ast.local.localinteractionsequence import LocalInteractionSequence as \
        LocalInteractionSequence
from scribble.ast.local.localchoice import LocalChoice as LocalChoice
from scribble.ast.local.localrecursion import LocalRecursion as LocalRecursion
from scribble.ast.local.localcontinue import LocalContinue as LocalContinue
from scribble.ast.local.localparallel import LocalParallel as LocalParallel
from scribble.ast.local.localinterruptible import LocalInterruptible as \
        LocalInterruptible
from scribble.ast.local.localthrow import LocalThrow as LocalThrow 
from scribble.ast.local.localcatch import LocalCatch as LocalCatch
from scribble.ast.local.localdo import LocalDo as LocalDo
from scribble.ast.local.localsend import LocalSend as LocalSend
from scribble.ast.local.localreceive import LocalReceive as LocalReceive


# Make classes for roles, message signatures, parameters, etc? or just Strings
# for names?
class NodeFactory(object):
    def __init__(self):
        super(NodeFactory, self).__init__()

    # signature follows ANTLR grammar
    #def module(self, decl, importmodules, importmembers, payloads, protocols):
    def module(self, decl, imports, payloads, globalps, localps):
        #return module.module(decl, importmodules, importmembers, payloads, protocols)
        return Module(decl, imports, payloads, globalps, localps)

    def parameterdecl(self, kind, name, alias):
        return ParameterDecl(kind, name, alias)

    def parameterdecllist(self, paramdecls):
        return ParameterDeclList(paramdecls)

    def argument(self, kind, isVal, arg, param):
        return Argument(kind, isVal, arg, param)

    def argumentlist(self, args):
        return ArgumentList(args)

    def roledecl(self, name, alias):
        return RoleDecl(name, alias)

    def roledecllist(self, roledecls):
        return RoleDeclList(roledecls)

    def roleinstantiation(self, arg, param):
        return RoleInstantiation(arg, param)

    def roleinstantiationlist(self, roleinstantiations):
        return RoleInstantiationList(roleinstantiations)

    def moduledecl(self, fmn):
        return ModuleDecl(fmn)

    def importmodule(self, fmn, alias):
        return ImportModule(fmn, alias)

    def payloadtypedecl(self, kind, ext_name, source, decl_name):
        return payloadTypeDecl(kind, ext_name, source, decl_name)


    def localprotocoldecl(self, local_role, name, parameterdecllist,
                          roledecllist, body):
        return LocalProtocolDecl(local_role, name, parameterdecllist,
                                 roledecllist, body)

    """def localprotocoldef(self, local_role, block):
        return LocalProtocolDef(local_role, block)"""
    def localprotocoldef(self, roles, params, local_role, block):
        return LocalProtocolDef(roles, params, local_role, block)

    def localprotocolblock(self, local_role, seq):
        return LocalProtocolBlock(local_role, seq)

    def localinteractionsequence(self, local_role, children):
        return LocalInteractionSequence(local_role, children)

    def localsend(self, local_role, dest, message):
        return LocalSend(local_role, dest, message)

    def localreceive(self, local_role, src, message):
        return LocalReceive(local_role, src, message)

    def localchoice(self, local_role, subject, blocks):
        return LocalChoice(local_role, subject, blocks)

    def localrecursion(self, local_role, reclab, block):
        return LocalRecursion(local_role, reclab, block)

    def localcontinue(self, local_role, reclab):
        return LocalContinue(local_role, reclab)

    def localparallel(self, local_role, blocks):
        return LocalParallel(local_role, blocks)

    def localdo(self, local_role, scope, target, args, roles):
        return LocalDo(local_role, scope, target, args, roles)

    def localinterruptible(self, local_role, scope, block, throws, catches):
        return LocalInterruptible(local_role, scope, block, throws, catches)

    def localthrow(self, local_role, dests, messages):
        return LocalThrow(local_role, dests, messages)

    def localcatch(self, local_role, src, messages):
        return LocalCatch(local_role, src, messages)
