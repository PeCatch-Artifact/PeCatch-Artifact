from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.core.cfg.node import Node, NodeType
from slither.core.solidity_types.user_defined_type import UserDefinedType
from slither.core.declarations.structure import Structure
from slither.slithir.operations.assignment import Assignment
from slither.slithir.variables.variable import Variable
from slither.slithir.variables.state_variable import StateVariable
from slither.slithir.variables.local_variable import LocalVariable
from slither.core.solidity_types.mapping_type import MappingType

from .loop import *
from .utils import *
import re

def detectVarDef(f):
    # print(f,"**********************")
    loops = []
    backedges = findBackedges(f.entry_point)
    for b in backedges:
        body = getLoopBody(b)
        loops.append(body)
    bugs = []
    blocks = getAllBlocks(f.source_mapping)
    stack = []
    for p in f.parameters:
        stack.insert(0,p)
        if p.location == "calldata":         
            stack.insert(0,"calldata length")
    block_var_decl = {}
    for lo in loops:
        stack_tmp = []
        stack_tmp.extend(stack)
        header = lo[0]
        if findPath(f.entry_point, header, {}, stack_tmp, blocks, block_var_decl) == False:
            print(header)
        (sline,eline) = getLoopLines(lo)
        index = 0
        new_num = 0
        for ir in header.irs:
            vars = ir.used
            for v in vars:
                if v in stack_tmp:
                    index = max(index, stack_tmp.index(v)+new_num)
                elif isinstance(v, LocalVariable):
                    new_num+=1
        # print(header, index, new_num,sline,eline)
        # print(*stack_tmp, sep = ", ")
        for node in lo[1:]:
            if changeStack(node, stack_tmp, blocks, block_var_decl) == False:
                print(node, "changeStack")
                return bugs
            # print(node)
            # print(*stack, sep = ", ")            
            # cline = node.source_mapping.lines[0]
            # isInBraces = False
            # for b in blocks:
            #     start_line = b[0]
            #     end_line = b[1]
            #     if cline >= start_line and cline <= end_line:
            #         isInBraces = True
            #         break
                # if cline > end_line:
                #     if start_line in block_var_decl:
                #         for v in block_var_decl[start_line]:
                #             if v in stack_var:
                #                 stack_var.remove(v)
                #         del block_var_decl[start_line]
                # elif cline >= start_line and cline <= end_line:
                #     if node.variable_declaration:
                #         if start_line not in block_var_decl:
                #             block_var_decl[start_line] = []
                #         block_var_decl[start_line].append(node.variable_declaration)
            # vars = node.variables_read + node.variables_written
            # for v in vars:
            #     if v in stack_var:
            #         stack_var.remove(v)
            #         stack_var.insert(0,v)
            #     elif len(stack_var) >= 16:
            #         break
            #     else:
            #         stack_var.append(v)
            # for v in node.variables_read:
            #     print(v,"**")
            # for v in node.variables_written:
            #     print(v,"&&")
            if node.type == NodeType.VARIABLE:
                if index > 14:
                    # print(node,"&&&&&&&&&&&&&")
                    return bugs
                if node.variable_declaration not in stack_tmp:
                    stack_tmp.insert(0, node.variable_declaration)
                if "_asm_" in node.variable_declaration.name:
                    continue
                isInBraces = False
                cline = node.source_mapping.lines[0]
                c_scol = node.source_mapping.starting_column
                c_ecol = node.source_mapping.ending_column
                for b in blocks:
                    if b[0] != b[2] and b[0] > sline and b[2] < eline and ((cline > b[0] and cline < b[2]) or (cline == b[0] and c_scol > b[1]) or (cline == b[2] and c_ecol < b[3])):
                        # print(b[0], b[2])
                        isInBraces = True
                        break
                # print(node, cline,"&&&", sline, eline, isInBraces)
                if isInBraces:
                    continue
                if isinstance(node.variable_declaration.type, UserDefinedType):
                    if isinstance(node.variable_declaration.type.type, Structure) and node.variable_declaration.location == "memory":
                        hasAssign = False
                        for ir in node.irs_ssa:
                            if isinstance(ir, Assignment):
                                hasAssign = True
                        if hasAssign:
                            continue
                index+=1
                if (node.variable_declaration.name, node) not in bugs:
                    if isinstance(node.variable_declaration.type, MappingType) and node.variable_declaration.location == "storage":
                        continue
                    bugs.append((node.variable_declaration.name, node)) 
    return bugs

def getLoopLines(loop):
    sline = loop[0].source_mapping.lines[0]
    eline = sline

    for node in loop[1:]:
        sline = min(sline, node.source_mapping.lines[0])
        eline = max(eline, node.source_mapping.lines[0])
    return (sline,eline)

def getAllBlocks(source_mapping):
    filename = source_mapping.filename.absolute
    f = open(filename, encoding="utf8")
    content = f.readlines()
    lines = source_mapping.lines
    braces = []
    unchecked = []
    blocks = []

    for l in lines:
        c = content[l-1]
        if isComment(c):
            continue
        if "{" in c:
            uncheck_index = -1
            if re.match(".*unchecked(\s*){.*", str.strip(c)):
                unchecked.append(l)
                uncheck_index = c.index("unchecked")
                for i in range(0, uncheck_index):
                    if '{' == c[i]:
                        braces.append((l,i))
                    elif '}' == c[i]:
                        handleRightBrace(braces, unchecked, l, i, blocks)
                for i in range(uncheck_index+9):
                    if '{' == c[i]:
                        uncheck_index = i
                        break
                for i in range(uncheck_index+1):
                    if '{' == c[i]:
                        braces.append((l,i))
                    elif '}' == c[i]:
                        handleRightBrace(braces, unchecked, l, i, blocks)
            else:
                for i in range(len(c)):
                    if '{' == c[i]:
                        braces.append((l,i))
                    elif '}' == c[i]:
                        handleRightBrace(braces, unchecked, l, i, blocks)
            # print(l,c)
        elif "}" in c:
            for i in range(len(c)):
                if '}' == c[i]:
                    handleRightBrace(braces, unchecked, l, i, blocks)
    return blocks

def handleRightBrace(braces, unchecked, l, index, blocks):
    if unchecked and braces:
        if unchecked[-1] > braces[-1][0]:
            unchecked.pop()
        else:
            s = braces.pop()
            blocks.append((s[0], s[1], l, index))
    elif unchecked:
        unchecked.pop()
    else:
        s = braces.pop()
        blocks.append((s[0], s[1], l, index))

def findPath(node, des, visited, stack, blocks, block_var_decl):
    visited[node] = True
    if node == des:
        return stack
    if changeStack(node, stack, blocks, block_var_decl) == False:
        return False
    for suc in node.sons:
        if suc not in visited or not visited[suc]:
            res = findPath(suc, des, visited, stack, blocks, block_var_decl)
            if res:
                return res
    visited[node] = False

def changeStack(node, stack, blocks, block_var_decl):
    cline = node.source_mapping.lines[0]
    c_scol = node.source_mapping.starting_column
    c_ecol = node.source_mapping.ending_column
    for b in blocks:
        start_line = b[0]
        start_col = b[1]
        end_line = b[2]
        end_col = b[3]
        # print(node, cline, c_scol, c_ecol, start_line, start_col, end_line, end_col)
        if cline > end_line or (cline == end_line and c_scol > end_col):
            if (start_line,start_col) in block_var_decl:
                for v in block_var_decl[(start_line,start_col)]:
                    if v in stack:
                        stack.remove(v)
                del block_var_decl[(start_line,start_col)]
        elif (cline > start_line and cline < end_line) or (cline == start_line and c_scol > start_col) or (cline == end_line and c_ecol < end_col):
            if node.variable_declaration:
                if (start_line,start_col) not in block_var_decl:
                    block_var_decl[(start_line,start_col)] = []
                block_var_decl[(start_line,start_col)].append(node.variable_declaration)
    vars = node.variables_read + node.variables_written
    for v in vars:
        if not v:
            continue
        if isinstance(v, StateVariable):
            continue
        if isinstance(v, Variable) and (v.is_constant or isinstance(v, Constant)):
            continue
        if v in stack:
            index = stack.index(v)
            if index > 15:
                # print(v)
                # print(*stack, sep = ", ")
                return False
            # stack.remove(v)
            # stack.insert(0,v)
        # else:
        #     stack.insert(0,v)
    if node.variable_declaration and node.variable_declaration not in stack:
        stack.insert(0,node.variable_declaration) 
    return stack

class AllocInLoop(AbstractDetector):  
    """
    Documentation
    """

    ARGUMENT = "alloc-in-loop" 
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detects allocation inside loop"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"

    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            if "@" in c.source_mapping.filename.absolute:
                continue
            if c.is_interface:
                continue
            for f in c.functions_and_modifiers:
                if not f.is_implemented:
                    continue
                bugs = detectVarDef(f)
                if len(bugs) > 0:
                    info = [ str(f.name) + '() @ ' + str(f.source_mapping) + '\n' ]

                    i = 0
                    while i < len(bugs):
                        info.append("[BUG:] ")
                        info.append(str(i))
                        info.append(": ") 
                        info.append(bugs[i][0])
                        info.append("\t")
                        info.append(str(bugs[i][1].source_mapping))
                        info.append("\n")
                        i += 1
                    info.append("\n")
                    
                    res = self.generate_result(info)
                    results.append(res)

        return results