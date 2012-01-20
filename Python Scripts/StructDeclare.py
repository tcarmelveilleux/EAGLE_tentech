# -*- coding: cp1252 -*-
# StructDeclare
# by Tennessee Carmel-Veilleux (<tcv - at - ro.boto.ca>)
# $Id$
#
    
from docutils import core, io
import sys
import getopt
import csv
import os.path
import time

VERSION = "1.0"

headerString = ""
codeString = ""
publishString = ""
excelString = ""
instanceAddressList = []

TARGET = "ARM"
TARGET_ALIGNMENTS = {"i386" : 4, "ARM" : 4}
TYPE_SIZES = { "CHAR" : 1, "UINT32_T" : 4, "INT32_T" : 4, "FLOAT" : 4, "INT": 4,"U32": 4, "S32" : 4, "UNSIGNED INT": 4 }
GLOBAL_ID = 0
VERBOSE = False

def EmitHeader(s):
    global headerString
    headerString += s
    
def EmitCode(s):
    global codeString
    codeString += s

def EmitPublish(s):
    global publishString
    publishString += s

def EmitExcel(s):
    global excelString
    excelString += s
 
def PublishRepresentation(startAddress, variable, what, idx):
    if "publish" in what:
        EmitPublish("%7s" % ("0x%04X" % startAddress))
    if "excel" in what:
        EmitExcel("%d" % startAddress)
    
    newAddress = startAddress

    typeName = variable["type"]
    name = variable["name"]
    comment = variable["comment"]
    multiplicity = variable["multiplicity"]
    # Get value from list if available
    if idx < len(variable["values"]):
        value = variable["values"][idx]
    else:
        value = "0"
    
    dataSize = TYPE_SIZES[typeName.upper()]
           
    # Génération du code pour la variable
    if multiplicity == 1:
        if "header" in what:
            EmitHeader("    %s %s; " % (typeName, name))
            if comment: EmitHeader("// %s" % comment)
        if "publish" in what:
            EmitPublish("  %23s  %8s  %10s    %s" % (name, typeName, value, comment))
        if "excel" in what:
            EmitExcel("\t%s\t%s\t%s\t%s" % (name, typeName, value, comment))
        newAddress += dataSize
    else:
        if "header" in what:
            EmitHeader("    %s %s[%d]; " % (typeName, name, multiplicity))
            if comment: EmitHeader("// %s" % comment)
        if "publish" in what:
            EmitPublish("  %23s  %8s  %10s    %s" % (name + ("[%d]" % (multiplicity)), typeName, value, comment))
        if "excel" in what:
            EmitExcel("\t%s\t%s\t%s\t%s" % (name + ("[%d]" % (multiplicity)), typeName, value, comment))
        newAddress += (dataSize * multiplicity)
    # Calcul du padding
    tempAddress, padding = GetPostPadding(newAddress)
    
    if padding <> 0:
        if "header" in what:
            EmitHeader(" char Pad_%d[%d]; " % (newAddress, padding))
        if "publish" in what:
            EmitPublish("\n%7s  %23s  " % (("0x%04X" % newAddress), "*%d bytes of padding*" % padding))
        if "excel" in what:
            EmitExcel("\n%d\t%s\t " % (newAddress, "*%d bytes of padding*" % padding))
    
    newAddress = tempAddress
    
    if "header" in what:
        EmitHeader("\n")
    if "publish" in what:        
        EmitPublish("\n")
    if "excel" in what:
        EmitExcel("\n")
    
    return (newAddress, dataSize, padding)

def GetPostPadding(startAddress):
    """
    Étape intermédiaire pour GetRepresentation. Calcule le postPadding
    pour l'alignement.
    
    retourne (newStartAddress, postPadding)
    """
    newAddress = startAddress

    alignment = TARGET_ALIGNMENTS[TARGET]

    if (startAddress < alignment):
        postPadding = alignment - startAddress
    else:
        if (startAddress % alignment) == 0:
            postPadding = 0
        else:
            postPadding = alignment - (startAddress % alignment)
    
    #print "postPadding = %d, startAddress = %d" % (postPadding, startAddress)
    if postPadding <> 0:
        newAddress = startAddress + postPadding
        
    return (newAddress, postPadding)
            
def ReadVarFile(filename):
    """
    Lit le fichier Filename et retourne un tuple de tuple:
    ( (NOM_DE_STRUCTURE, LISTE DE VARIABLES) , ... )
    """
    f = open(filename, "r")
    
    rows = csv.reader(f, delimiter = '\t')
    
    readingState = "waiting for name"
    structures = []
    
    for row in rows:
        items = [item for item in row if item <> '']
        
        if len(items) <> 0:
            if readingState == "waiting for name":
                structName = row[0]
                variables = []
                variable = {}
                readingState = "waiting for instances"
            elif readingState == "waiting for instances":
                instances = row[0].replace(' ','').split(',')
                readingState = "waiting for header"
            elif readingState == "waiting for header":
                # Pass through header line
                readingState = "reading struct"
            elif readingState == "reading struct":
                try:
                    print row
                    variable["name"] = row[0]
                    variable["type"] = row[1]
                    variable["multiplicity"] = int(row[2])
                    if len(row) > 3:
                        variable["values"] = row[3].replace(' ','').split(',')
                        if not variable["values"]: variable["values"] = ""
                    else:
                        variable["values"] = ""
                        
                        #if len(value) <> len(instances):
                        #    print "Number of values <> number of instances: %s" % row[3]
                        #    return (None,)
                    if len(row) > 4:
                        variable["comment"] = row[4]
                    else:
                        variable["comment"] = ""
                    
                    if variable["type"].upper() not in TYPE_SIZES.keys():
                        raise ValueError
                    
                    variables.append(variable.copy())
                except ValueError:
                    print >> sys.stderr, "Bad tokens : %s" % (str(row))
                    return (None,)
        else:
            if readingState == "reading struct":
                structures.append((structName, instances, variables))
                readingState = "waiting for name"
    
    if readingState == "reading struct":
        structures.append((structName, instances, variables))
        readingState = "waiting for name"
    
    return tuple(structures)


def AddTableEntry(structName, instance, variables, idx):
    address = GLOBAL_ID << 8
    newVariables = []
    
    title = "%d: Structure of %s (type %s)" % (GLOBAL_ID, instance, structName)
    
    EmitExcel(title + "\n")
    EmitExcel("Address\tName\tType\tValue\tComment\n")
    
    EmitPublish("\n" + title + "\n")
    EmitPublish('-' * len(title) + "\n")
    EmitPublish("""
=======  =======================  ========  ==========  ====================================
Address           Name              TYPE      VALUE                  Comment
=======  =======================  ========  ==========  ====================================
""" )

    for variable in variables:
        newAddress, dataSize, padding = PublishRepresentation(address, variable, ("publish","excel"), idx)
        variable["address"] = "0x%04X" % address
        newVariables.append(variable.copy())        
        if (padding <> 0):
            newVariable = {}
            newVariable["address"] = "0x%04X" % (address + dataSize)
            newVariable["name"] = "Pad_%d[%d]" % (newAddress, padding)
            newVariable["values"] = ""
            newVariable["type"] = "char"
            newVariable["multiplicity"] = padding
            
            newVariables.append(newVariable.copy())     
        address = newAddress
    
    EmitExcel("\n\n")
    EmitPublish("=======  =======================  ========  ==========  ====================================\n\n")
    
    return newVariables
    
def AddStructureDefinition(structName, variables):
    address = 0
    EmitHeader("struct st_%s {\n" % structName)

    for variable in variables:
        newAddress, dataSize, padding = PublishRepresentation(address, variable, ("header",), 0)
        address = newAddress
    
    EmitHeader("};\n\n")
    
def AddCode(structName, instance, variables, idx):
    # Emit extern declaration
    EmitHeader("extern struct st_%s %s;\n" % (structName, instance))
    
    # Emit actual instanciation
    EmitCode("struct st_%s %s = {\n" % (structName, instance))
    i = 0
    
    global instanceAddressList
    
    for variable in variables:
        # Get value from list if available
        if idx < len(variable["values"]):
            value = variable["values"][idx]
            if value == "":
                value = "0"
        else:
            value = "0"
            
        # Insert dummy array for both padding and init 
        if variable["multiplicity"] <> 1:
            EmitCode("{")
            for k in range(variable["multiplicity"]):
                if k <> 0:
                    EmitCode(",")
                EmitCode("0")
            EmitCode("}")
        else:    
            EmitCode(value)
        
        # Insert commas
        if i < len(variables) - 1:
            EmitCode(",")
            
        EmitCode(" // %s %s.%s: Global Address = %s\n" % (variable["type"], instance, variable["name"], variable["address"]))
        
        # Create float/not float truth value
        if variable["type"].upper() <> "FLOAT":
            variableType = 0
        else:
            variableType = 1
            
        instanceAddressList.append((variable["address"],"%s.%s" % (instance, variable["name"]), variable["type"], "%d" % variableType))
        
        i += 1
        
    EmitCode("};\n\n")
    
def AddLabels(structName, instance, variables):
    # Emit extern declaration
    EmitHeader("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitHeader("extern char *g_%sLabelTable[%d];\n" % (instance, len(variables)))
    EmitHeader("#endif\n")
    
    # Emit actual instanciation
    EmitCode("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitCode("char *g_%sLabelTable[%d] = {\n" % (instance, len(variables)))
    i = 0
    for variable in variables:
        EmitCode('"%s"' % variable["name"])
        
        # Insert commas
        if i < len(variables) - 1:
            EmitCode(",")
            
        EmitCode(" // %s %s.%s: Global Address = %s\n" % (variable["type"], instance, variable["name"], variable["address"]))
        i += 1
        
    EmitCode("};\n")
    EmitCode("#endif\n\n")
    
def AddInstances(structName, instances, variables):
    idx = 0
    global GLOBAL_ID, VERBOSE
    
    for instance in instances:
        if VERBOSE:
            print "    * Adding variable instance: '%s'" % instance
            
        newVariables = AddTableEntry(structName, instance, variables, idx)
        AddCode(structName, instance, newVariables, idx)
        AddLabels(structName, instance, newVariables)
        idx += 1
        GLOBAL_ID += 1
        
    EmitHeader("\n")
        
def AddInstanceTable(instanceList):
    global instanceAddressList
    
    EmitPublish("""
List of instances
-----------------

======  ============================ 
  ID               Name
======  ============================
""")
    EmitHeader("#define N_INSTANCES %d\n" % len(instanceList))
    EmitHeader("#define N_TOTAL_VARIABLES %d\n\n" % len(instanceAddressList))
    
    #-------- Emit complete type list
    EmitHeader("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitHeader("extern int gVariableTypes[%d];\n" % len(instanceAddressList))
    EmitHeader("#endif\n")
    
    EmitCode("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitCode("// List of types for every system address (non-zero = float):\n")
    EmitCode("int gVariableTypes[%d] = {\n" % (len(instanceAddressList)))
    
    ID = 0
    for address, name, typeName, variableType in instanceAddressList:
        EmitCode("%s" % variableType)
        
        if ID <> len(instanceAddressList) - 1:
            EmitCode(", ")
        
        EmitCode(" // %s: %s\n" % (address, name))
        ID += 1
    EmitCode("\n};\n")   
    EmitCode("#endif\n\n")
    
    #-------- Emit instance list
    EmitHeader("extern void *gInstanceTable[%d];\n" % len(instanceList))
    EmitExcel("List of structs\nID\tName\n")
    
    EmitCode("// List of instances:\n")
    EmitCode("void *gInstanceTable[%d] = {\n" % (len(instanceList)))

    ID = 0
    for instanceName in instanceList:
        if ID <> 0:
            EmitCode(",\n")
        
        EmitCode("(void *)(&%s)" % instanceName)
        EmitPublish("%6d  %28s\n" % (ID, instanceName))
        EmitExcel("%d\t%s\n" % (ID, instanceName))
        ID += 1
        
    EmitCode("\n};\n\n")
    EmitPublish("======  ============================\n\n")
    
    #-------- Emit struct label list
    EmitHeader("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitHeader("extern char *gInstanceLabelTable[%d];\n" % len(instanceList))
    EmitHeader("#endif\n")
    
    EmitCode("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitCode("// Instance labels:\n")
    EmitCode("char *gInstanceLabelTable[%d] = {\n" % (len(instanceList)))
    
    ID = 0
    for instanceName in instanceList:
        if ID <> 0:
            EmitCode(",\n")
        
        EmitCode('"%s"' % instanceName)
        ID += 1
        
    EmitCode("\n};\n")
    EmitCode("#endif\n\n")
    
    #-------- Emit label table list
    EmitHeader("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitHeader("extern char **gInstanceLabelTableList[%d];\n" % len(instanceList))
    EmitHeader("#endif\n")
    
    EmitCode("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitCode("// Instance member labels:\n")
    EmitCode("char **gInstanceLabelTableList[%d] = {\n" % (len(instanceList)))
    
    ID = 0
    for instanceName in instanceList:
        if ID <> 0:
            EmitCode(",\n")
        
        EmitCode('(char **)(&g_%sLabelTable)' % instanceName)
        ID += 1
        
    EmitCode("\n};\n");
    EmitCode("#endif\n\n")
    
    #-------- Emit complete label list
    EmitHeader("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitHeader("extern char *gVariableLabels[%d];\n" % len(instanceAddressList))
    EmitHeader("#endif\n")
    
    EmitCode("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitCode("// List of system addresses:\n")
    EmitCode("char *gVariableLabels[%d] = {\n" % (len(instanceAddressList)))
    
    ID = 0
    for address, name, typeName, variableType in instanceAddressList:
        EmitCode('"%s"' % name)
        
        if ID <> len(instanceAddressList) - 1:
            EmitCode(", ")
        
        EmitCode(" // %s [%s]\n" % (typeName, address))
        ID += 1
    EmitCode("\n};\n")  
    EmitCode("#endif\n\n")
    
    #-------- Emit complete address list
    EmitHeader("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitHeader("extern int gVariableAddresses[%d];\n" % len(instanceAddressList))
    EmitHeader("#endif\n")
    
    EmitCode("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitCode("// List of system addresses:\n")
    EmitCode("int gVariableAddresses[%d] = {\n" % (len(instanceAddressList)))
    
    ID = 0
    for address, name, typeName, variableType in instanceAddressList:
        EmitCode("%s" % address)
        
        if ID <> len(instanceAddressList) - 1:
            EmitCode(", ")
        
        EmitCode(" // %s %s\n" % (typeName, name))
        ID += 1
    EmitCode("\n};\n")
    EmitCode("#endif\n\n")    

def SaveString(s, filename, noOverwrite):
    global VERBOSE
    if VERBOSE:
        print "* Saving output file '%s'" % filename
    
    if noOverwrite:
        if os.path.exists(filename):
            print >> sys.stderr, "**** ERROR: No overwrite specified but output file EXISTS ! Exiting !"
            sys.exit(4)
    
    # Fallthrough
    try:
        f = open(filename, "w+")
        f.write(s)
        f.close()
    except IOError:
        print >> sys.stderr,  "**** I/O ERROR while writing file ! Exiting !"
        sys.exit(5)
    
def ProcessStructs(filenameList, noOverwrite, outputPrefix):
    global VERBOSE, TARGET
    
    headerFilename = outputPrefix + ".h"
    codeFilename = outputPrefix + ".c"
    publishFilename = outputPrefix + ".htm"
    excelFilename = outputPrefix + ".tsv"
    
    instanceList = []
    
    codeHeader = """
/*****************************************
    THIS FILE IS GENERATED AUTOMATICALLY.      
    PLEASE DO NOT MODIFY DIRECTLY.
    
    GENERATED BY: StructDeclare
    GENERATED ON: %s
******************************************/
""" % time.asctime()

    EmitCode(codeHeader)
    
    EmitHeader(codeHeader)
    EmitHeader('#ifndef __STRUCTS_INC__\n#define __STRUCTS_INC__\n\n')
    EmitHeader('typedef unsigned int uint32_t;\ntypedef int int32_t;\n\n')
    
    EmitHeader("unsigned char *GetMemberPtr(int addr);\n");
    EmitHeader("#ifndef STRUCTS_TARGET_SIDE\n")
    EmitHeader("char *GetMemberLabel(int addr);\n");
    EmitHeader("char *GetStructLabel(int addr);\n");
    EmitHeader("#endif\n\n")
    
    EmitCode('#include "%s"\n\n' % os.path.basename(headerFilename))
    EmitCode("""
unsigned char *GetMemberPtr(int addr)
{
    int structAddr;
    
    structAddr = (addr >> 8) & 0x7f;
    if (structAddr > 0 && structAddr < N_INSTANCES)
        return (unsigned char *)(gInstanceTable[structAddr]) + (addr & 0xff);
    else
        return 0;
}

#ifndef STRUCTS_TARGET_SIDE
char *GetMemberLabel(int addr)
{
    int structAddr;
    
    structAddr = (addr >> 8) & 0x7f;
    if (structAddr > 0 && structAddr < N_INSTANCES)
        return gInstanceLabelTableList[structAddr][(addr & 0xff) >> 2];
    else
        return 0;
}

char *GetStructLabel(int addr)
{
    int structAddr;
    
    structAddr = (addr >> 8) & 0x7f;
    if (structAddr > 0 && structAddr < N_INSTANCES)
        return gInstanceLabelTable[(addr >> 8) & 0x7f];
    else
        return 0;
}
#endif

""" )
    
    if VERBOSE:
        print "* Target: '%s'" % TARGET
    
    for filename in filenameList:
        if VERBOSE:
            print "* Reading input file: '%s'" % filename
        if not os.path.exists(filename):
            print >> sys.stderr,  "**** Input file '%s' does not exists ! Exiting !" % filename
            sys.exit(6)
            
        structs = ReadVarFile(filename)
        for struct in structs:
            structName, instances, variables = struct
            if VERBOSE:
                print "* Adding Structure Definition: '%s'" % structName
            AddStructureDefinition(structName, variables)
            AddInstances(structName, instances, variables)
            instanceList.extend(instances)
        
    if VERBOSE:
        print "* Adding Instance Table"
    
    AddInstanceTable(instanceList)
    
    EmitHeader("#endif\n\n")
    EmitCode("\n")
    
    SaveString(headerString, headerFilename, noOverwrite)
    SaveString(codeString, codeFilename, noOverwrite)
    #SaveString(excelString, excelFilename)
    
    if VERBOSE:
        print "* Saving output file '%s'" % publishFilename
        
    core.publish_programmatically(source_class = io.StringInput, source = publishString, source_path = None,
                                     destination_class = io.FileOutput, destination = None, destination_path = publishFilename,
                                     reader = None, reader_name = 'standalone', parser = None, parser_name = 'restructuredtext',
                                     writer = None, writer_name = 'html', settings = None, settings_spec = None,
                                     settings_overrides = None, config_section = None, enable_exit_status = None  )


def usage():
    print "StructDeclare %s by Tennessee Carmel-Veilleux <tcv - at - ro.boto.ca>\n" % VERSION
    print "Usage: StructDeclare [-h] [-n] [-v] [-o outfile_prefix] [-t target] infile"
    print "Options:"
    print "    -h/-?: Display this help message"
    print "    -n: Do not overwrite destination"
    print "    -v: Verbose output"
    print "    -o outfile_prefix: Output filename prefix (default: 'structs')"
    print "    -t target_arch: Target architecture, one of [ARM, i386] (default: 'ARM')"
    print "    infile: Input filename of variable definition table (TSV format)"
    
def main():
    global TARGET, VERBOSE
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hnv?o:t:", "")
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    outputPrefix = "structs"
    verbose = False
    noOverwrite = False
     
    for o, a in opts:
        if o == "-v":
            VERBOSE = True
        elif o in ("-h", "-?"):
            usage()
            sys.exit()
        elif o in ("-o"):
            outputPrefix = a
        elif o in ("-n"):
            noOverwrite = True
        elif o in ("-t"):
            TARGET = a
    
    if len(args) > 0:
        ProcessStructs(args, noOverwrite, outputPrefix)
    else:
        usage()

if __name__ == "__main__":
        main()
    
