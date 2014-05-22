import scrib_constants as constants
import scrib_collections as collections
import scrib_util as util

from visit.abstractcontext import AbstractContext as AbstractContext

from ast.globel.globalprotocoldecl import (
    get_parameter_names as globalprotocoldecl_get_parameters,
    get_role_name as globalprotocoldecl_get_roles
)

from ast.globel.globalprotocoldef import (
    get_full_name as globalprotocoldef_get_full_name,
    ROOT_SCOPE as globalprotocoldef_ROOT_SCOPE,
    get_declared_parameters as globalprotocoldef_get_parameters,
    get_declared_roles as globalprotocoldef_get_roles
)

from ast.globel.globalchoice import (
    get_subject as globalchoice_get_subject,
    DUMMY_ENABLING_OP as globalchoice_DUMMY_ENABLING_OP
)

from ast.globel.globaldo import (
    get_scope as globaldo_get_scope,
    get_target_full_name as globaldo_get_target_full_name,
    EMPTY_SCOPE_NAME as globaldo_EMPTY_SCOPE_NAME,
    get_argument_roles as globaldo_get_role_args,
    get_argument_args as globaldo_get_argument_args
)

from ast.globel.globalinterruptible import \
    get_scope as globalinterruptible_get_scope

from ast.globel.globalrecursion import \
    get_label as globalrecursion_get_label


# Could distinct "static" from "dynamic" info
#
# To be used "immutably" (via defensive copy setters)
class Context(AbstractContext):
    def __init__(self,
            import_path,  # string
            payload_path,  # string

            sources={},  # string |-> string
            modules={},  # string |-> CommonTree
            members={},  # string |-> CommonTree

            visible_modules={},  # string |-> CommonTree
            visible_payloads={},  # string |-> CommonTree   
            visible_globals={},  # string |-> CommonTree
            visible_locals={},  # string |-> CommonTree

            parent=None,  # AbstractContext
            ast=None,  # CommonTree

            module=None,  # string
            parameters=None,  # string |-> string
            roles=None,  # set of string
            scope=None,  # list of string
            scopes=None,  # list of set
            annotations=None,  # set of string
            enabled_roles=None,  # string |-> set of string
            operators=None,  # (string, string) |-> set of string
            rec_labs=None,  # list of (string |-> boolean)
            cont_labs=None,  # set of string
            rec_exitable=False,  # bool
            cont_exitable=False,  # bool
            do_stack=None,  # list of (string |-> boolean)
            do_exitable=False,  # bool
        
            rec_unfoldings={},  # string |-> CommonTree
            proto_unfoldings={},  # string |-> CommonTree
            projections={}):  # string |-> LocalProtocolDecl
    # {
        super(Context, self).__init__(parent, ast)

        self.import_path = import_path  # string
        self.payload_path = payload_path  # string

        # module dependencies built by moduleLoader
        # Map from fqmn to module source file path
        self._sources = sources
        # Map from fqmn to module AST (scribble.ast.module)
        self._modules = modules
        # Map from full member name to member AST (module AST accessible via
        # parent). Used in projection
        self._members = members

        # Section 4.1.1 -- Visibility built by VisibilityBuilder
        #
        # Map from "visible name" to module AST
        self._visible_modules = visible_modules
        # Map from "visible name" to member AST
        self._visible_payloads = visible_payloads
        self._visible_globals = visible_globals
        self._visible_locals = visible_locals

        # "Current" full module name (primary module)
        self.module = module  # string

        # Section 4.6.1 -- Bound role and parameter Names
        #
        # Map from in-scope parameter names to kind
        self._parameters = parameters # {}  
        # In-scope (bound) roles
        self._roles = roles  # set([])

        # Section 4.6.2 -- Scope names
        #
        # Current-scope stack (tracks the specific scope we are currently in) 
        # FIXME: not currently specified in the langref
        self._scope = scope
        # Stack of sets of scopes encountered (stack is pushed/popped on
        # entering/existing a nested _scope); simply requiring all scopes at
        # each "scope level" to be unique for now 
        #
        # A scope identifies a node in
        # the FSM hierarchy (a tree where each node is an FSM)
        self._scopes = scopes  # [set]

        # Section 4.6.2 -- Annotation names
        self._annotations = annotations  # set([])

        # Section 4.6.6 -- "enabling" roles for "action" (e.g. transfer sender
        # position, choice-at position, etc.) in choice well-formedness
        #
        # Map from role name to set of received "initial _operators" that may
        # enable it  # Name is a bit confusing (sounds like a set of roles),
        # just "enabled" may actually be better
        self._enabled_roles = enabled_roles  # {}

        # Section 4.6.8 -- "potential" operators for parallel well-formedness
        #
        # Map from (src, dest) role name pairs to set of _operators that src may
        # (potentially) send to dest
        self._operators = operators  # {}

        # Section 4.6.7 -- Bound recursion labels (map key set)

        # Section 4.6.7 -- Continue inside parallel for a recursion outside the
        # parallel (map values: True/False)
        #
        # List of maps from label to boolean
        # Value set to false when inside a parallel, i.e. label is technically
        # bound but cannot recurse to it
        self._rec_labs = rec_labs  # [{}]

        # Used to check bad sequencing within a rec (cf. rec/cont_exitable, for
        # sequencing after a rec)
        #
        # Set of "continue'd" labels; empty set means _exitable is true
        self._cont_labs = cont_labs  # set

        # True means an exit exists (for rec/continue)
        self._rec_exitable = rec_exitable  # bool
        self._cont_exitable = cont_exitable  # bool

        # List of maps from member name to set of role and argument tuples
        #
        # based on _rec_labs. each frame holds the protocols in the do-chain
        # (stored as a "set", chain order not needed); the stack itself is for
        # pushing/popping frames for parallels (for checking recursion due to a
        # do inside a parallel) -- FIXME: not currently specified in the langref
        # yet
        self._do_stack = do_stack  # [{}]

        # True means an exit exists (for do)
        self._do_exitable = do_exitable  # bool
        
        self._rec_unfoldings = rec_unfoldings
        self._proto_unfoldings = proto_unfoldings
        self._projections = projections
    # }


    def clone(self):
    # {
        # "Static" info compiled on top-level initialisation (creation, module
        # loading, visibility building) and not modified later
        sources = collections.clone_collection(self._sources)
        modules = collections.clone_collection(self._modules)
        members = collections.clone_collection(self._members)
        visiblemodules = collections.clone_collection(self._visible_modules)
        visiblepayloads = collections.clone_collection(self._visible_payloads)
        visibleglobals = collections.clone_collection(self._visible_globals)
        visibleLocals = collections.clone_collection(self._visible_locals)
        
        # "Dynamic" info that is modified as the AST is traversed
        parent = self.parent
        ast = self.ast
        module = self.module
        parameters = collections.clone_collection(self._parameters)
        roles = collections.clone_collection(self._roles)
        scope = collections.clone_collection(self._scope)
        scopes = collections.clone_collection(self._scopes)
        annotations = collections.clone_collection(self._annotations)
        enabledroles = collections.clone_collection(self._enabled_roles)
        operators = collections.clone_collection(self._operators)
        reclabs = collections.clone_collection(self._rec_labs)
        contlabs = collections.clone_collection(self._cont_labs)
        rec_exitable = self._rec_exitable
        cont_exitable = self._cont_exitable
        dostack = collections.clone_collection(self._do_stack)
        do_exitable = self._do_exitable
        
        rec_unfoldings = self._rec_unfoldings
        proto_unfoldings = self._proto_unfoldings
        projections = self._projections

        clone = Context(self.import_path, self.payload_path,
                        sources, modules, members, visiblemodules,
                        visiblepayloads, visibleglobals, visibleLocals,
                        parent, ast, module,
                        parameters, roles, scope, scopes, annotations,
                        enabledroles, operators, reclabs, contlabs,
                        rec_exitable, cont_exitable, dostack, do_exitable,
                        rec_unfoldings, proto_unfoldings, projections)
        return clone
    # }


    #########################################
    # Public lookup functions

    def is_role_declared(self, role):
        return role in self.get_roles()

    def is_role_enabled(self, role):
        return role in self._enabled_roles.keys()

    def is_operator_seen(self, src, dest, op):
        return (src, dest) in self._operators.keys() and \
            op in self._operators[(src, dest)]

    def is_recursion_label_declared(self, lab):
        labs = self.peek_recursion_labels()
        return lab in labs.keys() and labs[lab]

    def is_continue_label_seen(self, lab):
        return lab in self._cont_labs

    def has_exit(self):
        return self._rec_exitable and self._cont_exitable and \
            self._do_exitable and \
            (len(set(self.peek_recursion_labels().keys()) & \
                 self._cont_labs) == 0)

    # Maybe rename to something like getCurrentRecursionLabels
    def peek_recursion_labels(self):
        return self._rec_labs[len(self._rec_labs)-1]

    def get_current_scope(self):
        tmp = ''
        if self._scope:
            tmp = self._scope[0]
        for s in self._scope[1:]:
            tmp = '.' + s
        return tmp

    def get_current_scopes(self):
        return self._scopes[len(self._scopes)-1]

    # The "chain" is unordered
    def peek_do_chain(self):
        return self._do_stack[len(self._do_stack)-1]
    
    def has_projection(self, fullname):
        return fullname in self._projections.keys()
    

    #######################################################
    # Public getters (more basic than the lookup functions)
 
    # Getter used for this attribute because the method name is more meaningful
    def get_current_module(self):
        return self.module

    def get_source(self, fqmn):
        return self._sources[fqmn]

    def get_modules(self):
        return self._modules

    def get_module(self, fmn):
        return self._modules[fmn]

    def get_members(self):
        return self._members

    def get_member(self, fqmn):
        return self._members[fqmn]

    def get_visible_modules(self):
        return self._visible_modules

    def get_visible_payloads(self):
        return self._visible_payloads

    def get_visible_globals(self):
        return self._visible_globals

    def get_visible_global(self, n):
        return self._visible_globals[n]

    def get_visible_locals(self):
        return self._visible_locals

    def get_visible_local(self, n):
        return self._visible_locals[n]

    def get_parameters(self):
        return self._parameters

    def get_parameter(self, param):
        return self._parameters[param]

    def get_roles(self):
        return self._roles

    def get_annotationss(self):
        return self._annotations

    def get_enabled_roles(self):
        return self._enabled_roles

    def get_operators(self):
        return self._operators

    def get_continue_labels(self):
        return self._cont_labs

    def get_rec_exitable(self):
        return self._rec_exitable;

    def get_cont_exitable(self):
        return self._cont_exitable;

    def get_do_exitable(self):
        return self._do_exitable;
    
    def get_rec_unfolding(self, lab):
        return self._rec_unfoldings[lab]

    def get_proto_unfolding(self, fullname):
        return self._proto_unfoldings[fullname]

    def get_projection(self, fullname):
        return self._projections[fullname]

    def get_projections(self):
        return self._projections


    ###################################################
    # Defensive copy setters (for Context immutability)

    def set_current_module(self, module_):
        clone = self.clone()
        clone.module = module_
        return clone
    

    def add_source(self, fqmn, filepath):
        clone = self.clone()
        if fqmn not in clone._sources.keys():
            clone._sources[fqmn] = filepath
        else:
            # raise Exception("Shouldn't get in here: ", fqmn, filepath)
            pass
        return clone

    def add_module(self, fmn, module_):
        if fmn not in self._modules.keys():
            clone = self.clone()
            clone._modules[fmn] = module_
            return clone
        else:
            raise Exception("Shouldn't get in here: ", fmn, file)
            # return self

    # Update Context after an AST is modified by some pass
    def replace_module(self, fmn, module_):
        if fmn in self._modules.keys():
            clone = self.clone()
            clone._modules[fmn] = module_
            return clone
        else:
            raise Exception("Shouldn't get in here: ", fqmn, file)
            # return self

    # HACK: local name mangling for local context visiting
    def rename_visible_global(self, old, new):
        if old in self._visible_globals.keys():
            clone = self.clone()
            tmp = clone._visible_globals[old] 
            del(clone._visible_globals[old])
            clone._visible_globals[new] = tmp
            return clone
        else:
            raise RuntimeError("Shouldn't get in here: ", old, new)
            
    # member name parameter
    def add_member(self, fqmn, member):
        clone = self.clone()
        clone._members[fqmn] = member
        return clone
            

    def add_visible_module(self, n, module_):
        if n not in self._visible_modules.keys():
            clone = self.clone()
            clone._visible_modules[n] = module_
            return clone
        else:
            # raise Exception("Shouldn't get in here: ", fqmn, file)
            return self

    def add_visible_payload(self, n, member):
        if n not in self._visible_payloads.keys():
            clone = self.clone()
            clone._visible_payloads[n] = member
            return clone
        else:
            # raise Exception("Shouldn't get in here: ", fqmn, file)
            return self

    def add_visible_global(self, n, member):
        if n not in self._visible_globals.keys():
            clone = self.clone()
            clone._visible_globals[n] = member
            return clone
        else:
            # raise Exception("Shouldn't get in here: ", fqmn, file)
            return self

    def add_visible_local(self, n, member):
        if n not in self._visible_locals.keys():
            clone = self.clone()
            clone._visible_locals[n] = member
            return clone
        else:
            # raise Exception("Shouldn't get in here: ", fqmn, file)
            return self

    # Should have duplicate check, like add_role?
    def add_parameter(self, param, kind):
        clone = self.clone()
        clone._parameters[param] = kind
        return clone

    def add_role(self, role):
        if role in self._roles:
            util.report_error("Duplicate role: " + role)
        clone = self.clone()
        clone._roles.add(role)
        return clone

    # add_scope used to track distinct scopes in the current level (cf.
    # push/_pop_scope), called on entering a scope declaring node (do,
    # interruptible)
    def add_scope(self, scope):
        if scope not in self.get_current_scopes():
            clone = self.clone()
            scopes = clone.get_current_scopes()
            scopes.add(scope)
            return clone
        else:
            raise Exception("Shouldn't get in here: ", scope)

    def add_annotation(self, annot):
        clone = self.clone()
        clone._annotations.add(annot)
        return clone

    # addEnabledrole
    def enable_role(self, role_, op):
        """if op == None:
            raise Exception("Shouldn't get in here: ", role_, op)"""
        clone = self.clone()
        roles = clone._enabled_roles.keys()
        if role_ not in roles:  # or clone.enabledroles[role_] is None:
            clone._enabled_roles[role_] = set([op])
        else:
            # After a choice, the static enabling ops can be a set (run-time one
            # will belong to the set)
            clone._enabled_roles[role_].add(op)
        return clone

    def add_operator(self, src, dest, op):
        clone = self.clone()
        if (src, dest) not in clone._operators.keys():
            clone._operators[(src, dest)] = set([])
        clone._operators[(src, dest)].add(op)
        return clone

    def add_recursion_label(self, lab):
        # labs = self.recLabs[len(self.recLabs) - 1]
        if lab not in self.peek_recursion_labels().keys():
            clone = self.clone()
            labs = clone.peek_recursion_labels()
            labs[lab] = True
            # clone.recLabs = labs
                # Not needed, side effecting mutable labs in-place
            return clone
        else:
            raise Exception("Shouldn't get in here: ", lab)

    def remove_recursion_label(self, lab):
        clone = self.clone()
        recLabs = clone.peek_recursion_labels()
        del(recLabs[lab])
        return clone

    def add_continue_label(self, lab):
        clone = self.clone()
        clone._cont_labs.add(lab)
        return clone

    def remove_continue_label(self, lab):
        clone = self.clone()
        clone._cont_labs.remove(lab)
        return clone

    def set_rec_exitable(self, exitable):
        clone = self.clone()
        clone._rec_exitable = exitable
        return clone

    def set_cont_exitable(self, exitable):
        clone = self.clone()
        clone._cont_exitable = exitable
        return clone

    def set_do_exitable(self, exitable):
        clone = self.clone()
        clone._do_exitable = exitable
        return clone

    def add_rec_unfolding(self, lab, node_):
        clone = self.clone()
        clone._rec_unfoldings[lab] = node_
        return clone

    def add_proto_unfolding(self, fullname, node_):
        clone = self.clone()
        clone._proto_unfoldings[fullname] = node_
        return clone

    def add_projection(self, fullname, lpd):
        clone = self.clone()
        clone._projections[fullname] = lpd
        return clone


    ###########################################################################
    # Internal setters (no defensive copy -- should be used only within Context
    # on a clone)
    #
    # push/_pop_scope used to track current scope, called on entering/exiting
    # nested scopes (do target, interruptible body)
    # These are "private" (only used inside Context -- don't clone here)
    def _push_scope(self, scope):
        # root hack not really needed if a proper "makeScopedName" is used
        if scope != globalprotocoldef_ROOT_SCOPE:
            self._scope.append(scope)

    def _pop_scope(self, scope):
        if scope == globalprotocoldef_ROOT_SCOPE:
            if self._scope:
                raise Exception("Shouldn't get in here: " + str(self.scope))
        else:
            if self._scope[len(self._scope)-1] != scope:
                raise Exception("Shouldn't get in here: " + scope)
            self._scope.pop()

    def _push_scope_level(self):
        self._scopes.append(set([]))

    def _pop_scope_level(self):
        self._scopes.pop()


    ###########################################################################
    #The following node-specific push methods are for manipulating the Context
    #of a ContextVisitor for visiting the various Scribble (compound)
    #constructs. They should be used as push/pop pairs (although some rely on a
    #generic pop -- this should be fixed to always have an explicit push/pop for
    #each compound construct). They are called by the Visitor via the target
    #construct to here, because they manipulate the "private" fields of the
    #Context.
    #
    #These methods perform the logic needed to maintain a consistent Context
    #for all ContextVisitors, not just WellformednessChecker, although the
    #basis for these procedures lies in the well-formedness definitions.
    #Consequently, some of these routines depend on well-formedness to make
    #sense, and so the WellformednessChecker pass should be run before any
    #other ContextVisitor pass.
    ###########################################################################

    # Most information is reset for each protocol declaration. When visiting
    # do-targets however, the visitor should go to the block body of the target
    # directly, not start from the protocol declaration (so these fields won't
    # be reset)
    def push_globalprotocoldecl(self, gpd):
        context_ = self.push(gpd) 
        # "Initialisers"
        context_._parameters = {}
        context_._roles = set([])
        # The following may be more suitable in globalprotocoldef
        context_._scope = []
        context_._scopes = [set([])]
        context_._annotations = set([])
        # Conservative set for choice, but precise set for parallel 
        # is the domain the same as the bound roles?
        context_._enabled_roles = {}  # choice
        context_._operators = {}  # parallel 
            # OK to clear the set here, but makes more sense in a "body context_"
        context_._rec_labs = [{}]  # recursion
        context_._cont_labs = set([])
        context_._rec_exitable = True  # for checking rec continuations
        context_._cont_exitable = True  # for checking cont continuations
        context_._do_stack = [{}]  # based on recLabs
        context_._do_exitable = True  # for checking recursive-do continuations
        return context_
    
    def pop_globalprotocoldecl(self, gpd):
        return self.pop()
        

    # Bootstrap case for doStack, i.e. initial do-chain member; subsequent
    # doStack items are added on do (do-target block visited directly, skipping
    # the containing decl/def)
    def push_globalprotocoldef(self, node_):
        # Just a clone, unlike the others using AbstractContext.push -- just
        # doing some lightweight recording (bootstrapping) for recursive-do
        #
        # so doesn't update the ast
        clone = self.clone()
        """do_frame = clone.peek_do_chain()
        proto = globalprotocoldef_get_full_name(node_)
        # Tracking the "do-chain" (although as a key set -- order doesn't
        # matter) to detect recursive chains
        if proto not in do_frame.keys():
            # True means a (recursive) do to this proto is permitted (set False
            # by push_globalparallel and push_globalinterruptible)
            roles = globalprotocoldef_get_roles(node_)
            params = globalprotocoldef_get_parameters(node_)
            # def is the bootstrap case: the declared roles and params are the
            # "do args"
            clone._add_do_instance(proto, roles, params)
        else:
            raise Exception("Shouldn't get in here: ", proto)"""
        return clone

    def pop_globalprotocoldef(self, node_):
        clone = self.clone()
        """#do_frame = clone.peek_do_chain()
        proto = globalprotocoldef_get_full_name(node_)
        #del(do_frame[proto])
        roles = globalprotocoldef_get_roles(node_)
        params = globalprotocoldef_get_parameters(node_)
        clone._remove_do_instance(proto, roles, params)"""
        return clone
    

    # Precondition: Section 4.6.6 -- at-role of choice is bound
    def push_globalchoice(self, node_):
        clone = self.push(node_)  # Superclass method
        # Section 4.6.6 -- every role except the at-role must occur in a
        # receiver position (it must receive an "initial operator") before
        # occurring in a non-receiver position
        clone._enabled_roles = {}
        subj = globalchoice_get_subject(node_)
        clone = clone.enable_role(subj, globalchoice_DUMMY_ENABLING_OP)
        return clone
    
    def pop_globalchoice(self, node_):
        # Should possibly move some stuff here from globalchoice.context_visitor_leave
        return self.pop()  # Not really a pop; actually replaces old with current with
                           # pointers adjusted


    def push_globalrecursion(self, node_):
        clone = self.push(node_)
        # Section 4.6.7 -- bound recursion labels for well-formedness
        # FIXME: factor out with globalrecursion.check_wellformedness_enter
        reclab = self.get_current_scope() + '.' + globalrecursion_get_label(node_) 
        clone = clone.add_recursion_label(reclab)
        return clone

    def pop_globalrecursion(self, node_):
        return self.pop()


    def push_globalparallel(self, node_):
        clone = self.push(node_)
        # Visit children of this parallel with cleared record to collect all
        # required information, parent Context information should be added back
        # by the checker later
        clone._operators = {}
        # Section 4.6.7 -- continue inside parallel well-formedness
        # Pushing a "fully disabled" recursion frame onto the stack, so on
        # continues for outer labels will be allowed
        _append_disabled_frame(clone._rec_labs, False)
        # Equivalent to above recLabs treatment, adapted for recursive-do?
        # FIXME: not currently specified in the langref
        _append_disabled_frame(clone._do_stack, set([]))
        return clone

    def pop_globalparallel(self, node_):
        clone = self.pop()
        clone._rec_labs.pop()
        clone._do_stack.pop()
        return clone


    def push_globalinterruptible(self, node_):
        clone = self.push(node_)
        scope = globalinterruptible_get_scope(node_)
        # Some scope details not specified explicitly enough in langref yet
        clone._push_scope(scope)
        clone._push_scope_level()
        _append_disabled_frame(clone._do_stack, set([]))
        return clone

    def pop_globalinterruptible(self, node_):
        clone = self.pop()
        scope = globalinterruptible_get_scope(node_)
        clone._pop_scope(scope)
        clone._pop_scope_level()
        clone._do_stack.pop()
        return clone


    # Used to visit the do-target (not the do statement itself)
    def push_globaldo(self, node_):
        # Just a clone, unlike the others using AbstractContext.push -- will
        # visit the target AST but finding the AST itself does not need to push
        # the Context (the do statement itself is not structural, i.e. affecting
        # node_ and context parents)
        clone = self.clone()
        scope = globaldo_get_scope(node_)
        proto = globaldo_get_target_full_name(self, node_)
        if scope != globaldo_EMPTY_SCOPE_NAME:
            clone._push_scope(scope)  # Current scope
            clone._push_scope_level()  # Scopes encountered at this "scope level"
            
        # Also need to treat recLabs? for unscoped do? to avoid false shadowing
            
        do_frame = clone.peek_do_chain()
        # Tracking the "do-chain" (although as a key set -- order doesn't
        # matter) to detect recursive chains
        #gpd = clone.get_member(proto)
        #roles = globalprotocoldecl_get_roles(gpd)
        #params = globalprotocoldecl_get_parameters(gpd)
        roles = globaldo_get_role_args(node_)
        params = globaldo_get_argument_args(node_)
        #if proto not in do_frame.keys():
        if not clone.do_instance_in_chain(proto, roles, params):
            # True means a (recursive) do to this proto is permitted (set False
            # by push_globalparallel and push_globalinterruptible)
            clone._add_do_instance(proto, roles, params)
        else:
            # Checked in globaldo: shouldn't be visiting a recursive do-target
            raise Exception("Shouldn't get in here: ", proto)
        return clone

    def pop_globaldo(self, node_):
        clone = self.clone()
        scope = globaldo_get_scope(node_)
        proto = globaldo_get_target_full_name(self, node_)
        if scope != globaldo_EMPTY_SCOPE_NAME:
            clone._pop_scope(scope)
            clone._pop_scope_level()
        #do_frame = clone.peek_do_chain()
        #del(do_frame[proto])
        gpd = self.get_member(proto)
        #roles = globalprotocoldecl_get_roles(gpd)
        #params = globalprotocoldecl_get_parameters(gpd)
        roles = globaldo_get_role_args(node_)
        params = globaldo_get_argument_args(node_)
        clone._remove_do_instance(proto, roles, params)
        return clone
    
    
    ##
    # Local node versions of the above global routines, should be factored out
    
    def push_localprotocoldef(self, node_):
        clone = self.clone()
        """do_frame = clone.peek_do_chain()
        full_name = node_.get_full_name(self) 
        if full_name not in do_frame.keys():
            #do_frame[full_name] = True
            roles = node_.get_declared_roles()
            params = node_.get_declared_parameters()
            # def is the bootstrap case: the declared roles and params are the
            # "do args"
            clone._add_do_instance(full_name, roles, params)
        else:
            raise Exception("Shouldn't get in here: ", proto)"""
        return clone

    def pop_localprotocoldef(self, node_):
        clone = self.clone()
        """#do_frame = clone.peek_do_chain()
        full_name = node_.get_full_name(self) 
        #del(do_frame[full_name])
        roles = node_.get_declared_roles()
        params = node_.get_declared_parameters()
        clone._remove_do_instance(full_name, roles, params)"""
        return clone


    def push_localchoice(self, node_):
        clone = self.push(node_)
        #clone._enabled_roles = {}
        #subj = globalchoice_get_subject(node_)
        #clone = clone.enable_role(subj, globalchoice_DUMMY_ENABLING_OP)
        return clone
    
    def pop_localchoice(self, node_):
        return self.pop()


    def push_localrecursion(self, node_):
        clone = self.push(node_)
        reclab = self.get_current_scope() + '.' + node_.get_label() 
        clone = clone.add_recursion_label(reclab)
        return clone

    def pop_localrecursion(self, node_):
        return self.pop()


    def push_localparallel(self, node_):
        clone = self.push(node_)
        clone._operators = {}
        _append_disabled_frame(clone._rec_labs, False)
        _append_disabled_frame(clone._do_stack, set([]))
        return clone

    def pop_localparallel(self, node_):
        clone = self.pop()
        clone._rec_labs.pop()
        clone._do_stack.pop()
        return clone
    

    def push_localinterruptible(self, node_):
        clone = self.push(node_)
        scope = node_.get_scope()
        clone._push_scope(scope)
        clone._push_scope_level()
        _append_disabled_frame(clone._do_stack, set([]))
        return clone

    def pop_localinterruptible(self, node_):
        clone = self.pop()
        scope = node_.get_scope()
        clone._pop_scope(scope)
        clone._pop_scope_level()
        clone._do_stack.pop()
        return clone

    def push_localdo(self, node_):
        clone = self.clone()
        scope = node_.get_scope()
        proto = node_.get_target_full_name(self)
        if scope != globaldo_EMPTY_SCOPE_NAME:
            clone._push_scope(scope)  # Current scope
            clone._push_scope_level()  # Scopes encountered at this "scope level"
        #do_frame = clone.peek_do_chain()
        lpd = clone.get_projection(proto)
        #roles = lpd.get_role_names()
        #params = lpd.get_parameter_names()
        roles = node_.get_role_args()
        params = node_.get_param_args()
        #if proto not in do_frame.keys():
        if not clone.do_instance_in_chain(proto, roles, params):
            #do_frame[proto] = True
            ## True means a (recursive) do to this proto is permitted (set False
            ## by push_globalparallel and push_globalinterruptible)
            clone._add_do_instance(proto, roles, params)
        else:
            raise Exception("Shouldn't get in here: ", proto)
        return clone

    def pop_localdo(self, node_):
        clone = self.clone()
        scope = node_.get_scope()
        proto = node_.get_target_full_name(self)
        if scope != globaldo_EMPTY_SCOPE_NAME:
            clone._pop_scope(scope)
            clone._pop_scope_level()
        #do_frame = clone.peek_do_chain()
        #del(do_frame[proto])
        lpd = self.get_projection(proto)
        #roles = lpd.get_role_names()
        #params = lpd.get_parameter_names()
        roles = node_.get_role_args()
        params = node_.get_param_args()
        clone._remove_do_instance(proto, roles, params)
        return clone


    # Add do-instance to the do-chain ("call stack")
    def _add_do_instance(self, proto, roles, params):
        do_frame = self.peek_do_chain()
        if proto not in do_frame.keys():
            do_frame[proto] = set([])
        do_frame[proto].add(_make_do_chain_value(roles, params))

    def _remove_do_instance(self, proto, roles, params):
        do_frame = self.peek_do_chain()
        do_frame[proto].remove(_make_do_chain_value(roles, params))
        if not do_frame[proto]:
            del(do_frame[proto])
    
    def do_instance_in_chain(self, proto, roles, params):
        do_frame = self.peek_do_chain()
        if proto not in do_frame.keys():
            return False
        return _make_do_chain_value(roles, params) in do_frame[proto]


# A helper function for manipulating the rec_labs and do_stack structures
# s is a (list of (dict with boolean range values))
def _append_disabled_frame(s, v):
    tmp = {}
    for k in s[len(s)-1].keys():
        tmp[k] = v
    s.append(tmp)  # Side effecting s

# roles and params are lists
def _make_do_chain_value(roles, params):
    #.. FIXME: choice/par context leave .. also local ..  -- no: do-chain information not persisted to choice/par continuations (because it's not part of the chain)
    return (tuple(roles), tuple(params))
