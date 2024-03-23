from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations.assignment import Assignment
from slither.slithir.operations.unpack import Unpack
from slither.slithir.operations.binary import Binary, BinaryType
from slither.slithir.variables.constant import Constant
from slither.core.solidity_types.mapping_type import MappingType
from slither.core.solidity_types.array_type import ArrayType
from slither.slithir.operations.index import Index
from slither.slithir.operations.member import Member
from slither.core.cfg.node import Node, NodeType
from slither.slithir.variables.state_variable import StateVariable
from slither.core.variables.local_variable import LocalVariable
from slither.slithir.variables.local_variable import LocalIRVariable
from slither.slithir.variables.state_variable import StateIRVariable
from slither.slithir.variables.temporary_ssa import TemporaryVariableSSA
from slither.slithir.variables.reference_ssa import ReferenceVariableSSA
from slither.slithir.variables.temporary import TemporaryVariable
from slither.slithir.variables.reference import ReferenceVariable
from typing import List, Optional

from .cfg import *
from .loop import *
from .utils import *
import os,re

 
def detectSameTypeVars(vars):
    fields = {}
    for v in vars:
        if v.is_constant:
            continue
        if "int" not in str(v.type):
            continue 
        if v.type not in fields:
            fields[v.type] = []
        fields[v.type].append(v)

    types = list(fields.keys())
    for i in range(len(types)):
        for j in range(i+1, len(types)):
            if isSubType(types[j], types[i]):
                fields[types[i]].extend(fields[types[j]])
            elif isSubType(types[i], types[j]):
                fields[types[j]].extend(fields[types[i]])

    resList = []
    for t in fields:
        vlist = fields[t]
        if len(vlist) >= 2:
            resList.append(vlist)
    return resList

def isSubType(type1, type2):
    if isinstance(type1, MappingType):
        if type1.type_to == type2:
            return True
        elif isinstance(type1.type_to, MappingType) or isinstance(type1.type_to, ArrayType):
            return isSubType(type1.type_to, type2)
    elif isinstance(type1, ArrayType):
        if type1.type == type2:
            return True
        elif isinstance(type1.type, MappingType) or isinstance(type1.type, ArrayType):
            return isSubType(type1.type, type2)
    return False

def checkContractFieldsInitVal(contructors, sameTypelist):
    svars = {}
    for l in sameTypelist:
        for v in l:
            try:
                svars[v] = int(str(v.expression)) if v.initialized else 0
            except:
                print("special initialization", v.expression)
    
    vals = {}
    for const in contructors:
        for node in const.nodes:
            for ir in node.irs_ssa:
                leftVar = None
                rightVar = None
                if isinstance(ir, Assignment):
                    leftVar = ir.lvalue.non_ssa_version
                    rightVar = ir.rvalue
                elif isinstance(ir, Binary):
                    leftVar = ir.lvalue.non_ssa_version
                    rightVar = [ir.variable_left, ir.type, ir.variable_right]
                if leftVar and rightVar:
                    rightVal = getVal(rightVar, vals, svars)
                    if leftVar in svars:
                        if rightVal:
                            svars[leftVar] = rightVal
                        else:
                            del svars[leftVar]
                    if rightVal:
                        vals[leftVar] = rightVal
                    else:
                        vals.pop(leftVar, "no key")

    return getOrderedVars(sameTypelist, svars)

def getOrderedVars(sameTypelist, var_vals):
    largeVars = {}
    smallVars = {}
    for l in sameTypelist:
        l_len = len(l)
        for i in range(l_len-1):
            for j in range(i+1, l_len):
                if l[i] in var_vals and l[j] in var_vals:
                    if var_vals[l[i]] >= var_vals[l[j]]:
                        if l[i] not in smallVars:
                            smallVars[l[i]] = []
                        smallVars[l[i]].append(l[j])
                        if l[j] not in largeVars:
                            largeVars[l[j]] = []
                        largeVars[l[j]].append(l[i])
                    else:
                        if l[j] not in smallVars:
                            smallVars[l[j]] = []
                        smallVars[l[j]].append(l[i])
                        if l[i] not in largeVars:
                            largeVars[l[i]] = []
                        largeVars[l[i]].append(l[j])

    return smallVars, largeVars

def getVal(rightVar, vals, svars):
    if isinstance(rightVar, list):
        a = rightVar[0]
        b = rightVar[2]
        if hasNonSSAVersion(a):
            a = a.non_ssa_version
        if hasNonSSAVersion(b):
            b = b.non_ssa_version
        aVal = getVal(a, vals, svars)
        bVal = getVal(b, vals, svars)
        
        if aVal is not None and bVal is not None:
            if rightVar[1] == BinaryType.ADDITION:
                return aVal + bVal
            elif rightVar[1] == BinaryType.SUBTRACTION:
                return aVal - bVal
            elif rightVar[1] == BinaryType.MULTIPLICATION:
                return aVal * bVal
            elif rightVar[1] == BinaryType.DIVISION:
                return aVal / bVal
    else:
        if isinstance(rightVar, Constant):
            return rightVar.value
        if hasNonSSAVersion(rightVar):
            rightVar = rightVar.non_ssa_version
        if rightVar in vals:
            return vals[rightVar]
        elif rightVar in svars:
            vals[rightVar] = svars[rightVar]
            return svars[rightVar]

def hasNonSSAVersion(v):
    if isinstance(v, LocalIRVariable) or isinstance(v, StateIRVariable) or isinstance(v, TemporaryVariableSSA) or isinstance(v, ReferenceVariableSSA):
       return True
    return False

def detectUnchecked(c):
    sameTypeFields = detectSameTypeVars(c.state_variables)
    smallVars, largeVars = {},{}
    if len(sameTypeFields) > 0:
       smallVars, largeVars = checkContractFieldsInitVal(c.constructors, sameTypeFields)
    if not smallVars:
        bugs = {}
        for f in c.functions_declared:
            if not f.is_implemented:
                continue
            bugs[f] = []
            if not f.is_constructor:
                dominators = computeDominators(f)
                refDict = getRefDict(f)
                bugs[f].extend(checkLocalVar(f, dominators, refDict))
            bugs[f].extend(checkPlus(f))
            bugs[f] = filterFP(bugs[f], f.source_mapping)
        return bugs
    
    candidates = {}
    removeVars = []
    for f in c.functions_declared:
        if f.is_constructor or not f.is_implemented:
            continue
        refDict = getRefDict(f)
        var_add = {}
        var_sub = {}
        candidates[f] = []
        for node in f.nodes:
            for ir in node.irs_ssa:
                if isinstance(ir, Binary):
                    if ir.type == BinaryType.ADDITION:
                        left = getRefVar(ir.variable_left, refDict)
                        right = getRefVar(ir.variable_right, refDict)
                        if isinstance(left, tuple):
                            left = left[0]
                        if isinstance(right, tuple):
                            right = right[0]
                        if isinstance(left, StateVariable):
                            if left not in var_add:
                                var_add[left] = (right,ir)
                            else:
                                removeVars.append(left)
                        if isinstance(right, StateVariable):
                            if right not in var_add:
                                var_add[right] = (left,ir)
                            else:
                                removeVars.append(right)
                    elif ir.type == BinaryType.SUBTRACTION:
                        left = getRefVar(ir.variable_left, refDict)
                        right = getRefVar(ir.variable_right, refDict)
                        if isinstance(left, tuple):
                            left = left[0]
                        if isinstance(right, tuple):
                            right = right[0]
                        if isinstance(left, StateVariable):
                            if left not in var_sub:
                                var_sub[left] = (right,ir)
                            else:
                                removeVars.append(left)
                        if isinstance(right, StateVariable):
                            if right not in var_sub:
                                var_sub[right] = (left,ir)
                            else:
                                removeVars.append(right)
        for key in var_add:
            if key in var_sub:
                if var_add[key][0] == var_sub[key][0]:
                    candidates[f].append((key, var_add[key][1], key, var_sub[key][1]))
                    continue
                else:
                    removeVars.append(key) 

    for item in removeVars:
        if item in largeVars:
            del largeVars[item]
        if item in smallVars:
            del smallVars[item]

    for l in largeVars:
        arr = largeVars[l]
        new_arr = []
        for item in arr:
            if item not in removeVars:
                new_arr.append(item)    
        largeVars[l] = new_arr 

    for s in smallVars:
        arr = smallVars[s]
        new_arr = []
        for item in arr:
            if item not in removeVars:
                new_arr.append(item)    
        smallVars[s] = new_arr 
    
    bugs = {}
    for f in c.functions_declared:
        if not f.is_implemented:
            continue
        bugs[f] = []
        if not f.is_constructor:
            dominators = computeDominators(f)
            refDict = getRefDict(f)
            for can in candidates[f]:
                if can[1] in dominators[can[3]] and not stateVarValueChanged(can[0], can[1], can[2], can[3], f, refDict):
                        bugs[f].append((can[0], can[1], can[2], can[3]))
                elif can[3] in dominators[can[1]] and not stateVarValueChanged(can[2], can[3], can[0], can[1], f, refDict):
                        bugs[f].append((can[2], can[3], can[0], can[1]))
            tmp = checkStateVarInFunc(f, smallVars, largeVars, dominators, refDict)
            for t in tmp:
                if not stateVarValueChanged(t[0], t[2], t[1], t[3], f, refDict):
                    bugs[f].append(t)
            bugs[f].extend(checkLocalVar(f, dominators, refDict))
        bugs[f].extend(checkPlus(f))
        bugs[f] = filterFP(bugs[f], f.source_mapping)
    return bugs

def stateVarValueChanged(a, ira, b, irb, f, refDict):
    for node in f.nodes:
        for ir in node.irs_ssa:
            if isinstance(ir, Assignment):
                lvalue = getRefVar(ir.lvalue, refDict)
                if isinstance(lvalue, tuple):
                    lvalue = lvalue[0]
                if lvalue == a and ir.rvalue != ira.lvalue:
                    return True
                if lvalue == b and ir.rvalue != irb.lvalue:
                    return True
    return False

def checkStateVarInFunc(f, smallVars, largeVars, dominators, refDict):
    candidates = []
    additions = []
    substractions = []
    alias = {}
    for node in f.nodes:
        for ir in node.irs_ssa:
            if isinstance(ir, Assignment):
                rvalue = getRefVar(ir.rvalue, refDict)
                if isinstance(ir.lvalue, LocalVariable) and (isinstance(rvalue, StateVariable) or (isinstance(rvalue, tuple) and isinstance(rvalue[0], StateVariable))):
                    alias[ir.lvalue] = rvalue
            elif isinstance(ir, Binary):
                if ir.type == BinaryType.ADDITION:
                    left = ir.variable_left
                    right = ir.variable_right
                    if left in alias:
                        left = alias[left]
                    if right in alias:
                        right = alias[right]
                    left = getRefVar(left, refDict)
                    right = getRefVar(right, refDict)
                    if isinstance(left, tuple):
                        left = left[0]
                    if isinstance(right, tuple):
                        right = right[0]
                    if isinstance(left, StateVariable) or isinstance(right, StateVariable):
                        additions.append(ir)
                elif ir.type == BinaryType.SUBTRACTION:
                    left = ir.variable_left
                    right = ir.variable_right
                    if left in alias:
                        left = alias[left]
                    if right in alias:
                        right = alias[right]
                    left = getRefVar(left, refDict)
                    right = getRefVar(right, refDict)
                    if isinstance(left, tuple):
                        left = left[0]
                    if isinstance(right, tuple):
                        right = right[0]
                    if isinstance(left, StateVariable) or isinstance(right, StateVariable):
                        substractions.append(ir)

    replace_dict_add = {}
    for i in range(len(additions)-1):
        ira = additions[i]
        for j in range(i+1,len(additions)):
            irb = additions[j]
            is_can = isCandidate(ira, irb, largeVars, dominators, refDict, alias)
            if isinstance(is_can, tuple):
                (ira,irb,a,b) = is_can
                if isinstance(a, tuple):
                    a_first = a[0]
                else:
                    a_first = a
                if isinstance(b, tuple):
                    b_first = b[0]
                else:
                    b_first = b
                if irb.node.scope.is_checked:
                    candidates.append((a,ira,b,irb))
                if b_first not in replace_dict_add:
                    replace_dict_add[b_first] = []
                replace_dict_add[b_first].append(a_first)

    replace_dict_sub = {}
    for i in range(len(substractions)-1):
        ira = substractions[i]
        for j in range(i+1,len(substractions)):
            irb = substractions[j]
            is_can = isCandidate(ira, irb, smallVars, dominators, refDict, alias)
            if isinstance(is_can, tuple):
                (ira,irb,a,b) = is_can
                if isinstance(a, tuple):
                    a_first = a[0]
                else:
                    a_first = a
                if isinstance(b, tuple):
                    b_first = b[0]
                else:
                    b_first = b
                if irb.node.scope.is_checked:
                    candidates.append((a,ira,b,irb))
                if b_first not in replace_dict_sub:
                    replace_dict_sub[b_first] = []
                replace_dict_sub[b_first].append(a_first)

    removeInDict(replace_dict_add, replace_dict_sub, largeVars, smallVars)
    return candidates   

def checkLocalVar(f, dominators, refDict):
    additions = []
    substractions = []
    vals = {}
    for node in f.nodes:
        if node.type == NodeType.VARIABLE:
            var = node.variable_declaration
            if "int" in str(var.type):
                vals[var] = 0
        for ir in node.irs_ssa:
            if isinstance(ir, Unpack):
                lvalue = getRefVar(ir.lvalue, refDict)
                if isinstance(lvalue, tuple):
                    lvalue = lvalue[0]
                if lvalue in vals:
                    del vals[lvalue]
            elif isinstance(ir, Assignment):
                lvar = getRefVar(ir.lvalue, refDict)
                vals[lvar] = ir.rvalue
            elif isinstance(ir, Binary):
                if ir.type == BinaryType.ADDITION:
                    left = getRefVar(ir.variable_left, refDict)
                    right = getRefVar(ir.variable_right, refDict)
                    if isinstance(left, tuple):
                        left = left[0]
                    if isinstance(right, tuple):
                        right = right[0]
                    if not isinstance(left, LocalVariable) and not isinstance(right, LocalVariable):
                        continue                   
                    if left in vals:
                        additions.append((ir,left,vals[left],ir.variable_right))
                    if right in vals:
                        additions.append((ir,right,vals[right],ir.variable_left))
                elif ir.type == BinaryType.SUBTRACTION:
                    left = getRefVar(ir.variable_left, refDict)
                    right = getRefVar(ir.variable_right, refDict)
                    if isinstance(left, tuple):
                        left = left[0]
                    if isinstance(right, tuple):
                        right = right[0]
                    if not isinstance(left, LocalVariable) and not isinstance(right, LocalVariable):
                        continue
                    if left in vals:
                        substractions.append((ir,left,vals[left],ir.variable_right))
                    if right in vals:
                        substractions.append((ir,right,vals[right],ir.variable_left))

    bugs = []
    for i in range(len(additions)-1):
        (ir1,left1,left1_val,right1) = additions[i]
        for j in range(i+1,len(additions)): 
            (ir2,left2,left2_val,right2) = additions[j]
            if left1 == left2:
                continue
            if ir2 in dominators[ir1]:
                (ir1,left1,left1_val,right1) = additions[j]
                (ir2,left2,left2_val,right2) = additions[i]
            if ir1 in dominators[ir2] and ir2.node.scope.is_checked:
                if isinstance(left1_val, Constant):
                    left1_val = left1_val.value
                if isinstance(left2_val, Constant):
                    left2_val = left2_val.value  
                if isinstance(right1, Constant):
                    right1 = right1.value  
                if isinstance(right2, Constant):
                    right2 = right2.value    
                if left1_val == left2_val or (isinstance(left1_val, int) and isinstance(left2_val, int) and left1_val >= left2_val):
                    if right1 == right2 or (isinstance(right1, int) and isinstance(right2, int) and right1 >= right2):
                        bugs.append((left1, ir1, left2, ir2))
    
    for i in range(len(substractions)-1):
        (ir1,left1,left1_val,right1) = substractions[i]
        for j in range(i+1,len(substractions)): 
            (ir2,left2,left2_val,right2) = substractions[j]
            if left1 == left2:
                continue
            if ir2 in dominators[ir1]:
                (ir1,left1,left1_val,right1) = substractions[j]
                (ir2,left2,left2_val,right2) = substractions[i]
            if ir1 in dominators[ir2] and ir2.node.scope.is_checked:
                if isinstance(left1_val, Constant):
                    left1_val = left1_val.value
                if isinstance(left2_val, Constant):
                    left2_val = left2_val.value  
                if isinstance(right1, Constant):
                    right1 = right1.value  
                if isinstance(right2, Constant):
                    right2 = right2.value    
                if left1_val == left2_val or (isinstance(left1_val, int) and isinstance(left2_val, int) and left1_val <= left2_val):
                    if right1 == right2 or (isinstance(right1, int) and isinstance(right2, int) and right1 <= right2):
                        bugs.append((left1, ir1, left2, ir2))  
    return bugs          

def removeInDict(replace_dict_add, replace_dict_sub, largeVars, smallVars):
    for a in replace_dict_add:
        if a in largeVars:
            largeVars[a] = replace_dict_add[a]
        for key in smallVars:
            arr = smallVars[key]
            if a in arr:
                if key not in replace_dict_add[a]:
                    arr.remove(a)
                    smallVars[key] = arr
    
    for s in replace_dict_sub:
        if s in smallVars:
            smallVars[s] = replace_dict_sub[s]
        for key in largeVars:
            arr = largeVars[key]
            if s in arr:
                if key not in replace_dict_sub[s]:
                    arr.remove(s)
                    largeVars[key] = arr

def isCandidate(ira, irb, largeVars, dominators, refDict, alias):
    if irb in dominators[ira]:
        (ira, irb) = (irb, ira)
    if ira in dominators[irb]:
        b = irb.variable_left
        if b in alias:
            b = alias[b]
        b = getRefVar(b, refDict)
        b_added = irb.variable_right
        if b_added in alias:
            b_added = alias[b_added]
        b_added = getRefVar(b_added, refDict)
        b_first = b
        b_added_first = b_added
        if isinstance(b, tuple):
            b_first = b[0]
        if isinstance(b_added, tuple):
            b_added_first = b_added[0]
        if b_first not in largeVars:
            if b_added_first not in largeVars:
                return False
            (b, b_added) = (b_added, b)
            (b_first, b_added_first) = (b_added_first, b_first)
        
        a = ira.variable_left
        if a in alias:
            a = alias[a]
        a = getRefVar(a, refDict)
        a_added = ira.variable_right
        if a_added in alias:
            a_added = alias[a_added]
        a_added = getRefVar(a_added, refDict)
        a_first = a
        a_added_first = a_added
        if isinstance(a, tuple):
            a_first = a[0]
        if isinstance(a_added, tuple):
            a_added_first = a_added[0]
        if a_first not in largeVars[b_first]:
            if a_added_first not in largeVars[b_first]:
                return False
            (a, a_added) = (a_added, a)
            (a_first, a_added_first) = (a_added_first, a_first)
        if a_added == b_added:
            return (ira, irb, a, b)
        else:
            if isinstance(a_added, Constant) and isinstance(b_added, Constant) and a_added.value>=b_added.value:
                return (ira, irb, a, b)
    return False

def filterFP(bugs, source_mapping):
    if len(bugs) < 1:
        return bugs

    filename = source_mapping.filename.absolute
    f = open(filename, encoding="utf8")
    content = f.readlines()
    lines = source_mapping.lines
    uncheckedLines = []
    braces = []
    
    for l in lines:
        c = content[l-1]
        if isComment(c):
            continue
        if re.match("unchecked(\s*){", str.strip(c)):
            uncheckedLines.append([l, None])
        else:
            if re.match("}.*", str.strip(c)):
                if braces and uncheckedLines:
                    if not uncheckedLines[-1][1] and uncheckedLines[-1][0] > braces[-1]:
                        uncheckedLines[-1][1] = l
                    else:
                        braces.pop()
                elif braces:
                    braces.pop()
                elif uncheckedLines:
                    uncheckedLines[-1][1] = l
            if re.match(".*{", str.strip(c)):
                braces.append(l)
    
    if len(uncheckedLines) < 1:
        return bugs

    res = []
    for b in bugs:
        if isinstance(b[-1], Node):
            l = b[-1].source_mapping.lines[0]
        else:
            l = b[-1].node.source_mapping.lines[0]
        fp = False
        for u in uncheckedLines:
            if u[0] <= l and u[1] >= l:
                fp = True
                break
        if not fp:
            res.append(b)

    return res

def checkPlus(f):
    bugs = []
    loops = []
    backedges = findBackedges(f.entry_point)
    for b in backedges:
        body = getLoopBody(b)
        loops.append(body)

    for l in loops:
        ifNode = l[0]
        loopVar = None
        if ifNode.type != NodeType.IFLOOP:
            ifNode = l[-1]
        for ir in ifNode._irs_ssa:
            if isinstance(ir, Binary):
                loopVar = ir.variable_left.non_ssa_version
                break
        if not loopVar:
            continue
        if "_asm_" in loopVar.name:
            continue
            
        for node in l:
            for ir in node.irs_ssa:
                if isinstance(ir, Binary) and not BinaryType.return_bool(ir.type):
                    leftvar = ir.variable_left
                    rightvar = ir.variable_right
                    if hasNonSSAVersion(leftvar):
                        leftvar = leftvar.non_ssa_version
                    if hasNonSSAVersion(rightvar):
                        rightvar = rightvar.non_ssa_version
                    if leftvar == loopVar and isinstance(rightvar, Constant):
                        bugs.append((loopVar, ir))
                    elif rightvar == loopVar and isinstance(leftvar, Constant):
                        bugs.append((loopVar, ir))

    return bugs


class Unchecked(AbstractDetector):  # pylint: disable=too-few-public-methods
    """
    Documentation
    """

    ARGUMENT = "unchecked"  # slither will launch the detector with slither.py --mydetector
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detecting unchecked"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"

    def _detect(self):

        if self.compilation_unit.compiler_version.version < "0.8.0":
            return []

        results = []
        for c in self.compilation_unit.contracts_derived:
            if "@" in c.source_mapping.filename.absolute:
                continue
            if c.is_interface:
                continue
            
            bugs = detectUnchecked(c)
            for f in bugs:
                if len(bugs[f]) > 0:
                    info = [ str(f.name) + '() @ ' + str(f.source_mapping) + '\n' ]

                    i = 0
                    while i < len(bugs[f]):
                        info.append("[BUG:] ")
                        info.append(str(i))
                        info.append(": ") 
                        if len(bugs[f][i]) > 3:
                            if isinstance(bugs[f][i][0], tuple):
                                info.append(bugs[f][i][0][0].name)
                            else:
                                info.append(bugs[f][i][0].name)
                            info.append("\t")
                            info.append(str(bugs[f][i][1].node.source_mapping))
                            info.append("\t")
                            if isinstance(bugs[f][i][2], tuple):
                                info.append(bugs[f][i][2][0].name)
                            else:
                                info.append(bugs[f][i][2].name)
                            info.append("\t")
                            info.append(str(bugs[f][i][3].node.source_mapping)+"*")
                        else:
                            if isinstance(bugs[f][i][0], tuple):
                                info.append(bugs[f][i][0][0].name)
                            else:
                                info.append(bugs[f][i][0].name)
                            info.append("\t")
                            info.append(str(bugs[f][i][1].node.source_mapping))
                        info.append("\n")
                        i += 1
                    info.append("\n")
                    
                    res = self.generate_result(info)
                    results.append(res)


        return results

