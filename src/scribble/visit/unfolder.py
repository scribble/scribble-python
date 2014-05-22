import copy

import scrib_constants as constants
import scrib_util as util

from namesubstitutor import NameSubstitutor as NameSubstitutor
from visibilitybuilder import build_visibility as build_visibility

# from visit.traverser_variant import Traverser as Traverser
from visit.traverser import Traverser as Traverser

from ast.module import get_full_name as module_get_full_name

from ast.globel.globalprotocoldecl import \
    get_child as globalprotocoldecl_get_child

from ast.globel.globalprotocoldef import \
    get_block_child as globalprotocoldef_get_block_child

from ast.globel.globalcontinue import (
    get_label as globalcontinue_get_label,
)

from ast.globel.globalrecursion import (
    get_label as globalrecursion_get_label,
    get_block_child as globalrecursion_get_block_child
 )

from ast.globel.globaldo import (
    get_target_full_name as globaldo_get_target,
    get_argument_args as globaldo_get_args,
    get_argument_roles as globaldo_get_roles,
    get_argumentlist_child as globaldo_get_argumentlist,
    get_roleinstantiationlist_child as globaldo_get_roleinstantiationlist
)

from ast.globel.globalprotocolblock import \
    get_globalinteractionsequence_child as globalblock_get_interactionsequence

from ast.globel.globalinteractionsequence import \
    get_children as globalinteractionsequence_get_children

from ast.roleinstantiationlist import \
    get_role_map as roleinstantiationlist_get_map

from ast.argumentlist import \
    get_argument_map as argumentlist_get_map

from ast.globel.globalinteractionsequence import \
    traverse as globalinteractionsequence_traverse


class Unfolder(Traverser):
    
    # Context gets updated, should be retrieved later
    def __init__(self, context_):
        super(Unfolder, self).__init__()
        self._context = context_
        self._seen_rec_labs = set([])  # set of string (label names)
        self._seen_protos = set([])  # set of (string, [string], [string])   
                                        # (protocol name, roles, args)
        
        
    def once_unfold_all(self, node_):
        unfolded = self.traverse(node_)
        
        print "z: ", util.pretty_print(node_)
        print "a: ", util.pretty_print(unfolded)
        
        #print "a: ", util.pretty_print(globalprotocoldecl_get_child(unfolded))
        
        return unfolded

    def visit_untyped_leaf(self, node_):
        return node_
    
    
    """def _update_context(self, context_):
        self._context = context_"""
        
    def get_context(self):
        return self._context


    """def _visit_module(self, node_):
        return node_

    def _visit_moduledecl(self, node_):
        return node_

    def _visit_importmodule(self, node_):
        return node_

    def _visit_payloadtypedecl(self, node_):
        return node_"""

    def _visit_globalprotocoldecl(self, node_):
        collector = RecursionBlockCollector()
        self._rec_blocks = collector.collect_recursion_blocks(node_)
        return node_

    def _visit_roledecllist(self, node_):
        return node_

    def _visit_parameterdecllist(self, node_):
        return node_

    def _visit_globalprotocoldef(self, node_):
        return node_

    def _visit_roleinstantiationlist(self, node_):
        return node_

    def _visit_roleinstantiation(self, node_):
        return node_

    def _visit_argumentlist(self, node_):
        return node_

    def _visit_argument(self, node_):
        return node_

    def _visit_globalprotocolblock(self, node_):
        return node_

    def _visit_globalinteractionsequence(self, node_):
        return node_

    def _visit_globalmessagetransfer(self, node_):
        return node_

    def _visit_messagesignature(self, node_):
        return node_

    def _visit_payload(self, node_):
        return node_

    def _visit_payloadelement(self, node_):
        return node_

    def _visit_globalchoice(self, node_):
        return node_

    def _visit_globalrecursion(self, node_):
        return node_

    def _visit_globalcontinue(self, node_):
        return node_

    def _visit_globalparallel(self, node_):
        return node_

    def _visit_globalinterruptible(self, node_):
        return node_

    def _visit_globalinterrupt(self, node_):
        return node_

    def _visit_globaldo(self, node_):
        return node_

    def _visit_localprotocoldecl(self, node_):
        return node_

    
    """def _traverse_module(self, node_):
        #return module_traverse(self, node_)
        super(Unfolder, self)._traverse_module()

    def _traverse_moduledecl(self, node_):
        #return moduledecl_traverse(self, node_)
        super(Unfolder, self)._traverse_moduledecl()

    def _traverse_importmodule(self, node_):
        #return importmodule_traverse(self, node_)
        super(Unfolder, self)._traverse_moduledecl()

    def _traverse_payloadtypedecl(self, node_):
        return payloadtypedecl_traverse(self, node_)

    def _traverse_globalprotocoldecl(self, node_):
        return globalprotocoldecl_traverse(self, node_)

    def _traverse_roledecllist(self, node_):
        return roledecllist_traverse(self, node_)

    def _traverse_parameterdecllist(self, node_):
        return parameterdecllist_traverse(self, node_)

    def _traverse_globalprotocoldef(self, node_):
        return globalprotocoldef_traverse(self, node_)

    def _traverse_roleinstantiationlist(self, node_):
        return roleinstantiationlist_traverse(self, node_)

    def _traverse_roleinstantiation(self, node_):
        return roleinstantiation_traverse(self, node_)

    def _traverse_argumentlist(self, node_):
        return argumentlist_traverse(self, node_)

    def _traverse_argument(self, node_):
        return argument_traverse(self, node_)

    def _traverse_globalprotocolblock(self, node_):
        return globalprotocolblock_traverse(self, node_)

    def _traverse_globalinteractionsequence(self, node_):
        return globalinteractionsequence_traverse(self, node_)

    def _traverse_globalmessagetransfer(self, node_):
        return globalmessagetransfer_traverse(self, node_)

    def _traverse_messagesignature(self, node_):
        return messagesignature_traverse(self, node_)

    def _traverse_payload(self, node_):
        return payload_traverse(self, node_)

    def _traverse_payloadelement(self, node_):
        return payloadelement_traverse(self, node_)

    def _traverse_globalchoice(self, node_):
        return globalchoice_traverse(self, node_)

    def _traverse_globalrecursion(self, node_):
        return globalrecursion_traverse(self, node_)"""

    def _traverse_globalcontinue(self, node_):
        node_ = super(Unfolder, self)._traverse_globalcontinue(node_)
        lab = globalcontinue_get_label(node_)
        if lab not in self._seen_rec_labs:
            self._seen_rec_labs.add(lab)
            tmp = copy.deepcopy(self._rec_blocks[lab])  # FIXME: copy
            node_ = self.traverse(tmp)
            self._seen_rec_labs.remove(lab)
        return node_

    """def _traverse_globalparallel(self, node_):
        return globalparallel_traverse(self, node_)

    def _traverse_globalinterruptible(self, node_):
        return globalinterruptible_traverse(self, node_)

    def _traverse_globalinterrupt(self, node_):
        return globalinterrupt_traverse(self, node_)"""

    def _make_seen_protos_key(self, target, roles, args):
        return (target, tuple(roles), tuple(args))

    def _traverse_globaldo(self, node_):
        node_ = super(Unfolder, self)._traverse_globaldo(node_)
        target = globaldo_get_target(self._context, node_)
        roles = globaldo_get_roles(node_)
        args = globaldo_get_args(node_)
        key = self._make_seen_protos_key(target, roles, args)
        if key not in self._seen_protos:
            self._seen_protos.add(key)
            
            # .. FIXME: do substitution .. duplicate from globaldo
            
            ris = globaldo_get_roleinstantiationlist(node_)
            args = globaldo_get_argumentlist(node_)
            
            rolemap = roleinstantiationlist_get_map(self._context, target, ris)
            argmap = argumentlist_get_map(self._context, target, args)
            
            gpd = self._context.get_visible_global(target)
            """module_ = gpd.getParent()
            modulefullname = module_get_full_name(module_)
            clone = self._context.clone()
            clone = build_visibility(clone, module_)
            clone = clone.set_current_module(modulefullname)"""
            
            body = copy.deepcopy(globalprotocoldecl_get_child(gpd))
            block = globalprotocoldef_get_block_child(body)
                    # FIXME: copy
            substitutor = NameSubstitutor(rolemap, argmap)
            substituted = substitutor.substituteNames(block)

            node_ = self.traverse(globalblock_get_interactionsequence(substituted))
            #node_ = self.traverse(block)
            self._seen_protos.remove(key)
        return node_

    def _traverse_globalinteractionsequence(self, node_):
        traversed = []
        for child in globalinteractionsequence_get_children(node_):
            next = self.traverse(child)
            if util.get_node_type(next) == \
                    constants.GLOBAL_INTERACTION_SEQUENCE_NODE_TYPE:
                # No need to do recursively
                for c in globalinteractionsequence_get_children(next):
                   traversed.append(c)
            else:
                traversed.append(next)
        return util.antlr_dupnode_and_replace_children(node_, traversed)


    # FIXME: extend to locals
    def _traverse_localprotocoldecl(self, node_):
        return node_
    

class RecursionBlockCollector(Traverser):
    def __init__(self):
        super(RecursionBlockCollector, self).__init__()
        self._rec_blocks = {}  # Map: String |-> CommonTree  (lab |-> node)
    
    def collect_recursion_blocks(self, node_):
        self.traverse(node_)
        return self._rec_blocks

    def visit_untyped_leaf(self, node_):
        return node_

    def _visit_globalprotocoldecl(self, node_):
        return node_

    def _visit_roledecllist(self, node_):
        return node_

    def _visit_parameterdecllist(self, node_):
        return node_

    def _visit_globalprotocoldef(self, node_):
        return node_

    def _visit_roleinstantiationlist(self, node_):
        return node_

    def _visit_roleinstantiation(self, node_):
        return node_

    def _visit_argumentlist(self, node_):
        return node_

    def _visit_argument(self, node_):
        return node_

    def _visit_globalprotocolblock(self, node_):
        return node_

    def _visit_globalinteractionsequence(self, node_):
        return node_

    def _visit_globalmessagetransfer(self, node_):
        return node_

    def _visit_messagesignature(self, node_):
        return node_

    def _visit_payload(self, node_):
        return node_

    def _visit_payloadelement(self, node_):
        return node_

    def _visit_globalchoice(self, node_):
        return node_

    def _visit_globalrecursion(self, node_):
        lab = globalrecursion_get_label(node_)
        block = globalrecursion_get_block_child(node_)
        self._rec_blocks[lab] = block
        return node_

    def _visit_globalcontinue(self, node_):
        return node_

    def _visit_globalparallel(self, node_):
        return node_

    def _visit_globalinterruptible(self, node_):
        return node_

    def _visit_globalinterrupt(self, node_):
        return node_

    def _visit_globaldo(self, node_):
        return node_

    def _visit_localprotocoldecl(self, node_):
        return node_
