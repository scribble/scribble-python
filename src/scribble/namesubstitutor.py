

#TODO: refactor the node routines into the node modules


import copy

import scrib_constants as constants
import scrib_util as util

#from visit.visitor import Visitor as Visitor  # cyclic imports
import visit.visitor as visitor

import ast.globel.globalprotocolblock as globalprotocolblock
import ast.globel.globalinteractionsequence as globalinteractionsequence
import ast.globel.globalmessagetransfer as globalmessagetransfer
import ast.globel.globalchoice as globalchoice
import ast.globel.globalrecursion as globalrecursion
import ast.globel.globalcontinue as globalcontinue
import ast.globel.globalparallel as globalparallel
import ast.globel.globalinterrupt as globalinterrupt
import ast.globel.globalinterruptible as globalinterruptible
#import ast.globaldo as globaldo 
# something weird is going on that doesn't allow this; it's to do with circular
# imports

import ast  # HACK: because (recursive) import ast.globaldo is a problem

import ast.argument as argument
import ast.argumentlist as argumentlist
import ast.messagesignature as messagesignature
import ast.parameter as parameter
import ast.payloadelement as payloadelement
import ast.role as role
import ast.roleinstantiation as roleinstantiation
import ast.roleinstantiationlist as roleinstantiationlist


class NameSubstitutor(visitor.Visitor):
    def __init__(self, rolemap, argmap):
        super(NameSubstitutor, self).__init__()
        #Visitor.Visitor.__init__(self)
        self._rolemap = rolemap
        self._argmap = argmap

    def substituteNames(self, node):
        return self.visit(node)

    def getroleMap(self):
        return self._rolemap

    def getArgMap(self):
        return self._argmap


    def _visit_globalprotocolblock(self, node):
        dup = node.dupNode()
        #mycopy.children = [''] * 1  # HACK???
        seq = globalprotocolblock.get_globalinteractionsequence_child(node)
        substituted = self.visit(seq)
        #dup.setChild(0, newChild)
        dup.addChild(substituted)
        return dup

    def _visit_globalinteractionsequence(self, node):
        dup = node.dupNode()
        #childCount = node.getChildCount()
        ##dup.children = [''] * childCount
        #i = 0
        #while i < childCount :
        for child in globalinteractionsequence.get_children(node):
            #child = node.getChild(i)
            substituted = self.substituteNames(child)
            #dup.setChild(i, newChild)
            #i += 1
            dup.addChild(substituted)
        return dup

    def _visit_globalmessagetransfer(self, node):
        rolemap = self.getroleMap()
        argmap = self.getArgMap()

        dup = node.dupNode()
        #dup.children = [''] * 3

        msgnode = globalmessagetransfer.get_message_child(node)
        srcnode = globalmessagetransfer.get_source_child(node)
        #destnode = globalmessagetransfer.getglobalmessagetransferDestinationChild(node)
        destnodes = globalmessagetransfer.get_destination_children(node)

        tmp = msgnode.dupNode()
        if util.get_node_type(msgnode) != constants.MESSAGE_SIGNATURE_NODE_TYPE:
            msg = parameter.get_parameter_name(msgnode)  # parameter or message signature

            if msg in argmap.keys():  # a param to substitute
                val = argmap[msg]  # message signature or another parameter?
                tmp.token = copy.deepcopy(msgnode.token)  # HACK: does it conflict with any parser meta data? e.g. line number?
                #tmp.token.setText(_argmap[msg].getText())
                util.set_node_type(tmp, util.get_node_type(val))
                for child in val.getChildren():
                    tmp.addChild(copy.deepcopy(child))
        else:
            tmp.addChild(copy.deepcopy(messagesignature.get_operator_child(msgnode)))
            payload = messagesignature.get_payload_child(msgnode)
            tmp2 = payload.dupNode()
            for pe in payload.getChildren():
                tmp3 = pe.dupNode()
                tmp3.addChild(copy.deepcopy(payloadelement.get_annotation_child(pe)))
                child = payloadelement.get_type_child(pe)
                tmp4 = child.dupNode()
                if child.getText() in argmap.keys():
                    val = argmap[child.getText()]
                    tmp4.token = copy.deepcopy(child.token)
                    util.set_node_type(tmp4, util.get_node_type(val))  # parameter name and payload type both correspond to the node type for this node (the text of the node)
                tmp3.addChild(tmp4)
                tmp2.addChild(tmp3)
            tmp.addChild(tmp2)
        dup.addChild(tmp)  # If a parameter but not a substitution object, then the dupNode for tmp is enough

        src = role.get_role_name(srcnode)
        tmp = srcnode.dupNode()  # FIXME: sort out dupNode vs deepclone
        if src in rolemap.keys():  # FIXME: factor out this routine
            val = rolemap[src]
            #token = tmp.getToken()
            #token.setText(_rolemap[src])
            #tmp.setToken(token)

            #tmp.token.setText(_rolemap[src])
            tmp.token = copy.deepcopy(srcnode.token)
            #tmp.token.setText(_rolemap[src])
            util.set_node_type(tmp, val)
        #dup.setChild(1, tmp)
        dup.addChild(tmp)

        for destnode in destnodes:
            dest = role.get_role_name(destnode)
            tmp = destnode.dupNode()
            if dest in rolemap.keys():
                val = rolemap[dest]
                tmp.token = copy.deepcopy(destnode.token)
                #tmp.token.setText(_rolemap[dest])
                util.set_node_type(tmp, val)
            #dup.setChild(2, tmp)
            dup.addChild(tmp)

        return dup

    def _visit_globalchoice(self, node):
        rolemap = self.getroleMap()
        dup = node.dupNode()
        subjnode = globalchoice.get_subject_child(node)
        blocks = globalchoice.get_block_children(node)
        subj = role.get_role_name(subjnode)
        tmp = subjnode.dupNode()
        if subj in rolemap.keys():
            val = rolemap[subj]
            tmp.token = copy.deepcopy(tmp.token)
            #tmp.token.setText(_rolemap[subj])
            util.set_node_type(tmp, val)
        dup.addChild(tmp)
        for child in blocks:
            substituted = self.visit(child)
            dup.addChild(substituted)
        return dup

    def _visit_globalrecursion(self, node):
        dup = node.dupNode()
        #reclab = node.getChild(0).getText()
        labnode = globalrecursion.get_label_child(node)
        block = globalrecursion.get_block_child(node)
        dup.addChild(labnode.dupNode())
        substituted = self.visit(block)
        dup.addChild(substituted)
        return dup

    def _visit_globalcontinue(self, node):
        return node

    def _visit_globalparallel(self, node):
        dup = node.dupNode()
        blocks = globalparallel.get_block_children(node)
        for child in blocks:
            substituted = self.visit(child)
            dup.addChild(substituted)
        return dup

    def _visit_globalinterruptible(self, node):
        dup = node.dupNode()
        scopenode = globalinterruptible.get_scope_child(node)
        dup.addChild(scopenode.dupNode())
        block = globalinterruptible.get_block_child(node)
        substituted = self.visit(block)
        dup.addChild(substituted)
        interrupts = globalinterruptible.get_interrupt_children(node)
        for interrupt in interrupts:
            substituted = self.visit(interrupt)
            dup.addChild(substituted)
        return dup

    def _visit_globalinterrupt(self, node):  # FIXME: not actually permitted by the syntax yet, but for later
        rolemap = self.getroleMap()
        argmap = self.getArgMap()

        dup = node.dupNode()

        #util.report_error('[NameSubstitutor] TODO: ' + node)  # FIXME

        rolenode = globalinterrupt.get_role_child(node)
        msgnodes = globalinterrupt.get_message_children(node)

        dest = role.get_role_name(rolenode)  # FIXME: factor out with globalmessagetransfer
        tmp = rolenode.dupNode()
        if dest in rolemap.keys():
            val = rolemap[dest]
            tmp.token = copy.deepcopy(rolenode.token)
            util.set_node_type(tmp, val)
        dup.addChild(tmp)

        for mn in msgnodes:
            tmp = mn.dupNode()  # FIXME: factor out with globalmessagetransfer
            if util.get_node_type(mn) != constants.MESSAGE_SIGNATURE_NODE_TYPE:
                msg = parameter.get_parameter_name(mn)  # parameter or message signature
                if msg in argmap.keys():  # a param to substitute
                    val = argmap[msg]  # message signature or another parameter?
                    tmp.token = copy.deepcopy(mn.token)  # HACK: does it conflict with any parser meta data? e.g. line number?
                    #tmp.token.setText(_argmap[msg].getText())
                    util.set_node_type(tmp, util.get_node_type(val))
                    for mn in val.getChildren():
                        tmp.addChild(copy.deepcopy(mn))
            else:
                for mn in mn.getChildren():
                    tmp.addChild(copy.deepcopy(mn))
            #tmp.addChild(tmp)  # If a parameter but not a substitution object, then the dupNode for tmp is enough
            dup.addChild(tmp)

        return dup

    def _visit_globaldo(self, node):
        rolemap = self.getroleMap()
        argmap = self.getArgMap()

        dup = node.dupNode()

        scopenode = ast.globel.globaldo.get_scope_child(node)
        dup.addChild(scopenode.dupNode())

        #protocolnode = ast.globel.globaldo.getglobaldoProtocolChild(node)
        protocolnodes = ast.globel.globaldo.get_target_name_children(node)
        argnodes = argumentlist.get_argument_children(ast.globel.globaldo.get_argumentlist_child(node))
        roleinstantiations = roleinstantiationlist.get_roleinstantiation_children(ast.globel.globaldo.get_roleinstantiationlist_child(node))  # list of ROLEINSTANTIATION
        #packagenodes = ast.globel.globaldo.getglobaldoPackageChildren(node)

        #dup.addChild(protocolnode.dupNode())

        #dup.addChild(copy.deepcopy(node.getChild(1)))  # FIXME: handle argnodes "properly"?
        tmp = ast.globel.globaldo.get_argumentlist_child(node).dupNode()
        for arg in argnodes:  # each arg
            """argtype = util.get_node_type(arg)  # FIXME: make parameters (recursion labels, etc.) proper syntactic categories with node types
            if argtype != constants.MESSAGE_SIGNATURE_NODE_TYPE:
                tmp2 = copy.deepcopy(_argmap[argtype])  # argtype is the parameter name
            else:
                tmp2 = copy.deepcopy(arg)  # need to get MESSAGESIGNATURE's children
            tmp.addChild(tmp2)"""
            tmp2 = arg.dupNode()  # roughly duplicated from roleinstantiationlist procedure below, FIXME: factor out
            tmp3 = argument.get_arg_child(arg).dupNode()
            #tmp3 = copy.deepcopy(argument.get_arg_child(arg))  # FIXME: should be uniform with MessageTransfer msgnode
            ours = util.get_node_type(tmp3)
            if ours != constants.MESSAGE_SIGNATURE_NODE_TYPE:
                if ours in argmap.keys():
                    val = argmap[ours]  # ours is a parameter name
                    tmp3.token = copy.deepcopy(tmp3.token)
                    #tmp3.token.setText(_argmap[ours])
                    util.set_node_type(tmp3, util.get_node_type(val))
                    """tmp3.addChild(messagesignature.get_operator_child(val))
                    tmp3.addChild(messagesignature.get_payload_child(val))"""
                    for child in val.getChildren():
                        tmp3.addChild(copy.deepcopy(child))
            else:  # FIXME: factor out with MessageTransfer msgnode case
                """for child in argument.get_arg_child(arg).getChildren():
                    tmp3.addChild(copy.deepcopy(child))"""
                msgnode = argument.get_arg_child(arg)
                tmp3.addChild(copy.deepcopy(messagesignature.get_operator_child(msgnode)))
                payload = messagesignature.get_payload_child(msgnode)
                tmp4 = payload.dupNode()
                for pe in payload.getChildren():
                    tmp5 = pe.dupNode()
                    tmp5.addChild(copy.deepcopy(payloadelement.get_annotation_child(pe)))
                    child = payloadelement.get_type_child(pe)
                    tmp6 = child.dupNode()
                    if child.getText() in argmap.keys():
                        val = argmap[child.getText()]
                        tmp6.token = copy.deepcopy(child.token)
                        util.set_node_type(tmp6, util.get_node_type(val))  # parameter name and payload type both correspond to the node type for this node (the text of the node)
                    tmp5.addChild(tmp6)
                    tmp4.addChild(tmp5)
                tmp3.addChild(tmp4)
            tmp2.addChild(tmp3)
            if argument.get_parameter_child(arg) != None:
                tmp2.addChild(argument.get_parameter_child(arg).dupNode())
            tmp.addChild(tmp2)

        dup.addChild(tmp)

        tmp = ast.globel.globaldo.get_roleinstantiationlist_child(node).dupNode()  # HACroleinstantiations node
        for ri in roleinstantiations:
            tmp2 = ri.dupNode()  # each roleinstantiation node
            tmp3 = roleinstantiation.get_arg_child(ri).dupNode()  # each ours role node
            ours = util.get_node_type(tmp3)
            if ours != constants.MESSAGE_SIGNATURE_NODE_TYPE:  # FIXME: don't understand this line, but seems to break Import11 test when commented
                if ours in rolemap.keys():
                    val = rolemap[ours]  # ours is a parameter name
                    tmp3.token = copy.deepcopy(tmp3.token)
                    #tmp3.token.setText(_rolemap[ours])
                    util.set_node_type(tmp3, val)
            tmp2.addChild(tmp3)
            param = roleinstantiation.get_parameter_child(ri)
            if param != None:
                tmp2.addChild(param.dupNode())
            tmp.addChild(tmp2)

        dup.addChild(tmp)

        """for child in packagenodes:
            dup.addChild(child.dupNode())  # dupNode enough?"""
        for child in protocolnodes:
            dup.addChild(child.dupNode())  # dupNode enough?

        return dup
