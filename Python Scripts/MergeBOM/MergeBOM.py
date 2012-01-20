#!/bin/env python
# -*- coding: cp1252 -*-
# MergeBOM.py ($Id: MergeBOM.py 501 2007-02-01 00:20:34Z veilleux $)
# MergeBOM: A Bill Of Materials utility.
#
# (C) 2005-2007 Tennessee Carmel-Veilleux
# Entreprises TenTech (<tcv - at - ro.boto.ca>)
#
# Permission is granted to use this program for any purpose, including
# commercial as long as no fee is charged for use or distribution. No 
# warranty, either express or implied is granted for the use of this
# program. The author is not liable for any loss of data, damage or
# injury arising from the use of this program.

import csv
import re
import os.path
from Tkinter import *
import tkFileDialog
import tkMessageBox
import tkFont

VERSION = "MergeBOM v2.0"

ABOUT_TEXT = """
MergeBOM: A Bill Of Materials utility.

(C) 2005-2007 Tennessee Carmel-Veilleux
Entreprises TenTech (<tcv - at - ro.boto.ca>)

Permission is granted to use this program for any purpose, including
commercial as long as no fee is charged for use or distribution. No 
warranty, either express or implied is granted for the use of this
program. The author is not liable for any loss of data, damage or
injury arising from the use of this program.
"""

HELP_TEXT = """
MergeBOM Help

(C) 2005-2007 Tennessee Carmel-Veilleux
Entreprises TenTech (veilleux - at - tentech.ca)

Table of contents
=================
1.0 What This Program Does
2.0 Input file formats
3.0 The Job List
  3.1 Add/Remove/Edit/View File buttons
  3.2 Description of the fields
  3.3 Clear/Load/Save List buttons
4.0 Running

1.0 What This Program Does
--------------------------
MergeBOM is a program that takes multiple BOM lists ("jobs") and 
outputs one BOM list per individual distributor with the quantities 
added together between jobs. The same part from the same distributor
in different parts list will thus be "merged". This greatly
simplifies the process of ordering parts for many different projects
and completely removes the need to extract individual parts lists
for each order.

This program also tries to validate part numbers from the following
distributors:
 * Digikey
 * Mouser
 * Newark
 
Finally, every part list is exported in a format that is either
directly loadable in Excel (CSV or TSV) or in the distributor's
website order import facility in the case of Digikey. 

2.0 Input file formats
----------------------
MergeBOM will try to load delimiter-separated text files, with one
part number per line. The delimiter can be either a comma (CSV), a
semicolon (French CSV) or a tabulation (TSV) character. More than one
part can be provided on a single line if they go together. These parts
must then be separated by a '+' sign, and the distributor column must
contain the same number of distributors separated by '+' also. In the
following example, the last line (QTY of 55) is a connector and a plug
that go together. IN THE OUTPUT LIST, the multiple items of a single
line will be SEPARATED add added as single items along with other 
parts from a same distributor.

The columns need to be in the following order (using CSV as an
example):

QTY,PART NUMBER,DISTRIBUTOR NAME

ex:

12,LM555-ND,Digikey
23,34M9567,NewarkInOne
2,LT3467BPbF,Linear(Direct)
4,345-1234-2-ND,Digikey
55,CONN234-ND+PLUG723,Digikey+Molex

If the distributor name is empty or omited, a default distributor
name for the current file can be selected in the dialog (see
section 3.2)

3.0 The Job List
----------------
The Job List contains itemized lines, one for each file that is to
be processed along  with the options selected.  The  format of a 
line is:

QTYx FILENAME [REFERENCE]

ex:

2x MotorDrive.tsv [Motor Drive REV A]
1x GasController.csv [Pressure controller]

3.1 Add/Remove/Edit
-------------------
 * Add Button: Adds a new item to the Job List
 * Remove Button: Removes the selected item from the list
 * Edit Button: Edits the selected item entry
 * View File: Shows the contents of the parts file from the currently
              selected job entry.
 
 Note: Double-clicking on a list item will edit it

3.2 Description of the fields
-----------------------------
The Add and Edit dialogs contain the following fields:

 * Multiplicity: 
     Number of times to multiply every line item quantity in the file
     in the final addition. 
 * Filename:
     Filename of the parts list file to load for this job entry. The
     "Browse..." button brings-up a file selection dialog.
 * Reference:
     Reference to be used for the current job entry. When exporting a
     Digikey parts list, this field will be included along with the
     part number and quantities. This feature allows Digikey to put
     the name of the projects which contained a part directly on the 
     label.
 * Default distributor: 
     If the input file does not have a third column containing the
     distributor name, this distributor will be used instead. This
     field is useful for lists that are already order part lists for
     a specific distributor (ie: the output of this program).
 * Headers Present:
     Flag that tells the loader that the file contains a headings
     line with column names as the first line of the file. It will
     be skipped without warning.
 * Separator:
     Character to be used as the delimiter between fields in the 
     input file.

3.3 Clear/Load/Save List buttons
--------------------------------
These buttons allow the user to act on the Job list as a whole. When
a Job list is created, it can be saved to be loaded later when a
similar job arises.

 * Clear list button: Clears the entire Job list
 * Load list: Loads a previously saved Job list from a file
 * Save list: Saves the current Job list configuration to a file

4.0 Running
-----------
When the Job list is ready, the "Execute" button will run the merging
algorithm on the files.

1- For every file in the job list, the following actions are done in 
   order:

 * Every line of the file is loaded
 * Blank lines are skipped
 * Lines that contain more than one part separated by '+' are split
 * Lines that contain more than one part but that don't have a
   matching number of distributor items in the list are skipped.
  
   Ex:
  
   '55,CONN234-ND+PLUG723,Digikey' would be skipped, unless the
   distributor was changed to 'Digikey+Molex' or any other two
   distributors (the same number are the number of files).

 * Parts from "known" distributors (Digikey, Mouser, Newark) are
   validated using regular expressions and rejected if they do not
   conform.
 * Quantities from the file are multiplied by the multiplicity
   associated with the Job list item.
 * The reference is associated with the loaded parts
 * All loaded parts are added in a cross-reference table

2- The cross-reference table is traversed to gather parts for every
   distributor.
   
3- An output parts list is generated for each distributor containing
   the total quantities of each part and the reference if applicable.
   
4- The parts list are exported in CSV format with a filename
   consisting of the "Output filename prefix" followed by the name of
   the distributor. In the case of parts lists for Digikey, the
   "Reference" column is also included and the format is suitable for
   direct import using the Digikey "Text File Import" feature.
   
   Ex:
   
   If "Output filename prefix" is "Order_" and the Jobs contained
   parts from Digikey and Mouser, the output filenames would be:
   
   * Order_digikey.csv
   * Order_mouser.csv
   
The lists are now ready to be used ! Enjoy !

"""

class Distributor:
    def __init__(self):
        self.validator = re.compile("")
    
    def Validate(self, partnum):
        return self.validator.search(partnum)
    
    def Header(self):
        return "Qty,Part Number\n"
        
    def Format(self, qty, partnum, references):
        return "%d,%s\n" % (qty, partnum)

class DistributorDigikey(Distributor):
    def __init__(self):
        Distributor.__init__(self)
        self.validator = re.compile("-ND$")
    
    def Header(self):
        return ""
        
    def Format(self, qty, partnum, references):
        return "%d,%s,%s\n" % (qty, partnum, "+".join(references))

class DistributorMouser(Distributor):
    def __init__(self):
        Distributor.__init__(self)
        self.validator = re.compile(r"^[0-9][0-9][0-9]-")
        
DISTRIBUTORS = {"digikey": DistributorDigikey(), 
                "mouser": DistributorMouser(),
                "DEFAULT": Distributor()}

def shortenFilename(filename, maxLen):
    if len(filename) > maxLen:
        s = "..." + filename[-(maxLen - 3):]
    else:
        s = filename
        
    return s

def LoadList(filename, quantity, reference, hasHeaders, separator, defaultDist = "DEFAULT"):
    """
    Chargement d'une liste de pièces en fichier délimité par "separator". Le fichier "filename"
    est chargé. Les quantités de pièces de la liste sont multipliés "quantity"
    fois. À chaque pièce, on ajoute une chaine "reference" qui identifie le
    projet source. Chaque élément de la liste créée contient un tuple du 
    format: (quantity, partKey, reference). Si la référence == "", la fonction
    essaie de loader la valeur d'une troisième colonne comme référence. Si 
    "hasHeaders" est vrai, la première ligne du fichier est skippée
    
    Retourne un tuple contenant le nombre de pièces ignorées et une copie 
    de la liste créée.
    """
    skip = 0
    lineNumber = 0
    partList = {}
    
    if not defaultDist:
        defaultDist = "DEFAULT"
        
    fin = file(filename,"r")
    if hasHeaders:
        fin.readline() # Skip la ligne
        lineNumber = 1
        
    reader = csv.DictReader(fin, fieldnames = ("qty","partnum","distributor"), delimiter = separator)
    
    for row in reader:
        #print row
        lineNumber += 1
        
        # Vérification de la validité du format
        if not row["qty"] or not row["partnum"]:
            skip += 1
            continue
            
        # Première colonne, quantité
        try:
            qty = int(row["qty"])
        except ValueError:
            skip += 1
            print >> logfile, "[LoadList] %s:%d -> Skip part: Quantity not a number" % (shortenFilename(filename,50), lineNumber)
            continue
        
        parts = row["partnum"].upper().strip().split("+")
        
        if not row["distributor"]:
            distributors = [defaultDist] * len(parts)
        else:
            distributors = row["distributor"].lower().strip().split("+")
        
        if len(parts) <> len(distributors):
            skip += 1
            print >> logfile, "[LoadList] %s:%d -> Skip part: len(parts) <> len(distributors)" % (shortenFilename(filename,50), lineNumber)
            continue
            
        for part, distributor in zip(parts, distributors):
            partKey = part.strip()
            distributor = distributor.strip().lower()
            # Skip pièces vides
            if partKey == '' or distributor == '': 
                print >> logfile, "[LoadList] %s:%d -> Skipped empty part number" % (shortenFilename(filename,60), lineNumber)
                skip += 1
                continue
            
            # Validation des numéros de pièce, le cas échéant
            if DISTRIBUTORS.has_key(distributor):
                if not DISTRIBUTORS[distributor].Validate(partKey):
                    print >> logfile, "[LoadList] %s:%d -> Skip non-%s part: %s" % (shortenFilename(filename,50), lineNumber, distributor, partKey)
                    skip += 1
                    continue
                
            # Ajout de la pièce à la liste
            if (partList.has_key(distributor)):
                partList[distributor].append((quantity*qty, partKey, reference))
            else:
                partList[distributor] = [(quantity*qty, partKey, reference)]

    fin.close()
    
    return (skip, partList.copy())

def MergeList(partsDict, partsList):
    """
    Insertion de la liste de pièces "partsList" à l'intérieur du dictionnaire
    "partDict". Les quantité sont ajoutées aux quantités déjà existantes d'une
    même clé. Les références sont ajoutés à la liste des références si la clé
    existe.
    
    Retourne un dictionnaire modifié. "partsDict" ne subit pas de mutation.
    """
    tempPartsDict = partsDict.copy()
    
    for distributor, partList in partsList.items():
        if not tempPartsDict.has_key(distributor):
            tempPartsDict[distributor] = {}

        for quantity, partKey, reference in partList:
            if not tempPartsDict[distributor].has_key(partKey):
                # Insertion d'un item
                tempPartsDict[distributor][partKey] = (quantity,(reference,))
            else:
                # Update de la quantité
                newQuantity = tempPartsDict[distributor][partKey][0] + quantity
                
                # Update de la référence
                newReference = tempPartsDict[distributor][partKey][1]
                if reference not in tempPartsDict[distributor][partKey][1]:
                    # Insertion du nom de la reference
                    tempList = list(newReference)
                    tempList.append(reference)
                    newReference = tuple(tempList)
                
                tempPartsDict[distributor][partKey] = (newQuantity, newReference)
                
    return tempPartsDict
    
def SavePartsDict(filename, distributor, partsDict):
    """
    Enregistre une liste CSV par fichier ayant comme préfixe "prefix" qui représente le
    contenu du dictionnaire "partsDict". Il y a un fichier par clé de partsDict (un par
    distributeur). Le format du fichier de sortie est:
    
    Quantity, Part Number, [Reference List (dans le cas de Digikey)]
    
    Retourne rien
    """
    fout = file(filename,"w+")
    
    if DISTRIBUTORS.has_key(distributor):
        fout.write(DISTRIBUTORS[distributor].Header())
    else:
        fout.write(DISTRIBUTORS["DEFAULT"].Header())
    
    # Sort list by part number
    items = [(part, info) for part, info in partsDict.iteritems()]
    items.sort(key = lambda k: str.lower(k[0]))
        
    # Écrit la liste dans le fichier en se servant du formatter propre au distributeur
    if DISTRIBUTORS.has_key(distributor):
        formatter = DISTRIBUTORS[distributor].Format 
    else:
        formatter = DISTRIBUTORS["DEFAULT"].Format
    
    for part, info in items:
        qty = info[0]
        references = info[1]
        fout.write(formatter(qty, part, references))
        
    fout.close()
    
def CollatePartsLists(prefix, BOMList):
    """
    Routine qui exécute la mise en commun de listes de pièces à partir
    de "BOMList". Enregistre le résultat dans le fichier "filename".
    
    La "BOMList" contient des tuples ayant le format suivant:
    
        (filename, quantity, reference identifier (REFERENCE), hasHeaders, separator)
        
    où: 
        "filename" est le nom du fichier CSV de source pour le projet
        "quantity" est le multiplicateur de quantité de pièces
        "reference identifier" est le nom à donner au projet (mnémonique)
        "hasHeaders" indique si une ligne de headers est présente au début du fichier
        "separator" est le séparateur utilisé
        
    Retourne rien
    """

    partsDict = {}
    
    skipTotal = 0
    for quantity, inFilename, reference, defaultDist, hasHeaders, separator in BOMList:
        print >> logfile, "*********\nInserting %d times %s" % (quantity, shortenFilename(inFilename,60))
        skipped, partsList = LoadList(inFilename, quantity, reference, hasHeaders, separator, defaultDist)
        partsDict = MergeList(partsDict, partsList)
        skipTotal += skipped
    
    for distributor in partsDict.keys():
        filename = prefix + distributor + ".csv"
        print >> logfile, "*********\nOutput in %s" % shortenFilename(filename,60)
        SavePartsDict(filename, distributor, partsDict[distributor])
       
    print >> logfile, "*********\nTotal number of skipped parts: %d" % skipTotal

#**************************************** DIALOG PORTION ************************************************************
class Dialog(Toplevel):
    def __init__(self, parent, title = None):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        
        self.parent = parent
        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()
    
        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)
    #
    # construction hooks
    def body(self, master):
    # create dialog body. return widget that should have
    # initial focus. this method should be overridden
        pass
    
    def buttonbox(self):
    # add standard button box. override if you don't want the
    # standard buttons
        box = Frame(self)
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()
    #
    # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()
        
    def cancel(self, event=None):
    # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
    
    #
    # command hooks
    def validate(self):
        return 1 # override
    
    def apply(self):
        pass # override

class OpenFileCommand:
    def __init__(self, stringVar, entry):
        self.stringVar = stringVar
        self.entry = entry
        
    def command(self):
        self.stringVar.set(tkFileDialog.askopenfilename(filetypes=[("All files", "*")]))
        self.entry.icursor(END)
        self.entry.focus_set()
        
class EditorDialog(Dialog):
    def __init__(self, items, parent, title = None, defaults = None):
        self.entries = []
        self.items = items
        self.results = None
        
        if defaults:
            self.defaults = defaults
        else:
            self.defaults = ("",) * len(items)
        
        Dialog.__init__(self, parent, title)
        
    def body(self, master):
        i = 0
        self.commands = []
        self.vars = []
        
        for item, default in zip(self.items, self.defaults):
            self.vars.append(StringVar())
            cmd = None
            
            if item[0] == '_':
                # Special case: label starts with underscore: add browse button
                
                # Create entry field, identification label and browse button
                Label(master, text = (item[1:] + ":")).grid(row = i, padx = 5, pady = 5, sticky = E)
                entry = Entry(master, width = 30, textvariable = self.vars[i])
                entry.grid(row = i, column = 1, pady = 5, sticky = E+W) 
                cmd = OpenFileCommand(self.vars[i], entry)
                
                button = Button(master, text = "Browse...", command = cmd.command )
                button.grid(row = i, column = 2)
                
                entry.icursor(END)
                entry.focus_set()
            elif item[0] == '?':
                # Special case: label starts with question mark: entry is a checkbutton
                
                # Create checkbutton
                Label(master, text = (item[1:] + ":")).grid(row = i, column = 0, padx = 5, sticky = E)
                entry = Checkbutton(master, text = "", onvalue = "1", offvalue = "0", variable = self.vars[i])
                entry.grid(row = i, column = 1, pady = 5, sticky = W)
                if not default: default = "0"
                
            elif item[0] == '$':
                # Special case: label starts with $: entry is Radiobutton
                parts = item[1:].split('$')
                text = parts[0]
                choices = parts[1].split('|')
                
                j = 0
                
                Label(master, text = text+":").grid(column = 0, row = i, padx = 5, sticky = N+E)
                
                bFrame = Frame(master, relief = "groove", border = "2")
                for choice in choices:
                    entry = Radiobutton(bFrame, variable = self.vars[i], text = choice, value = str(j))
                    entry.grid(column = 0, row = j, padx = 5, sticky = W)
                    j += 1
                
                if not default: default = "0"
                    
                bFrame.grid(columnspan = 2, column = 1, row = i, padx = 5, pady = 5, sticky = W)
            else:
                
                # Create entry field and identification label
                Label(master, text = (item + ":")).grid(row = i, padx = 5, pady = 5, sticky = E)
                entry = Entry(master, width = 40, textvariable = self.vars[i])          
                entry.grid(row = i, columnspan = 2, column = 1, pady = 5, sticky = E+W)                 

            if default : self.vars[i].set(default) # Initialize default value in the field
            
            self.commands.append(cmd)            
            self.entries.append(entry) # Store object for further access
            
            i += 1
        
        return self.entries[0]

    def apply(self):
        self.results = tuple([str(v.get()) for v in self.vars])
        # print self.results

class ListItem:
    pass
    
class ItemListFrame(Frame):
    """
    Frame that shows a listBox frame that allows:
     * Adding an item
     * Editing an item
     * Remove an item
     * Load/Save the list
     
    The listBox shows a formatted representation of each list item. 
    Each list item is a tuple of values. Callback functions are used to process
    the item for use by this frame
    
    parameters:
     * items: The reference to the list of items
     * master: Master frame for this frame
     
    callback parameters:
     * editor(item): Edits the item
     * formatter(item): returns a flat string that correctly represents the item
     * validator(item): validates an item for correctness
     * itemizer(item): return an item from a tuple of string containing the raw values
     * itemizer(item): returns a flat string of comma-separated tokens that allows saving of the item
    """
    
    def __init__(self, items, editor, formatter, validator, itemizer, serializer, master=None):
        Frame.__init__(self, master, relief = "groove", borderwidth = "2")
        self.items = items
        self.editor = editor
        self.formatter = formatter
        self.validator = validator
        self.itemizer = itemizer
        self.serializer = serializer
        self.createWidgets()
        
    def createWidgets(self):
        # Listbox for input files and associated commands
        self.yScroll1 = Scrollbar(self, orient=VERTICAL)
        self.yScroll1.grid(row = 0, column = 4, sticky = N+S)
        
        self.listBox = Listbox(self, width = 70, height = 10, yscrollcommand = self.yScroll1.set)
        self.listBox.grid(columnspan = 4, row = 0, column = 0, sticky = N+S+E+W)
        
        self.yScroll1["command"] = self.listBox.yview
        
        self.bFrame = Frame(self)
        
        self.addButton = Button(self.bFrame, text="Add...", command = self.onAdd)
        self.addButton.grid(row = 0, column = 0, pady = 5, padx = 5)
        
        self.removeButton = Button(self.bFrame, text="Remove", command = self.onRemove)
        self.removeButton.grid(row = 0, column = 1, padx = 5)
        
        self.editButton = Button(self.bFrame, text="Edit...", command = self.onEdit)
        self.editButton.grid(row = 0, column = 2, padx = 5)
        
        self.clearButton = Button(self.bFrame, text="Clear list", command = self.onClearList)
        self.clearButton.grid(row = 0, column = 3, padx = 5)
        
        self.saveButton = Button(self.bFrame, text="Load list...", command = self.onLoadList)
        self.saveButton.grid(row = 0, column = 4, padx = 5)
        
        self.saveButton = Button(self.bFrame, text="Save list...", command = self.onSaveList)
        self.saveButton.grid(row = 0, column = 5, padx = 5)
        
        self.bFrame.grid(columnspan = 5, row = 1, column = 0, sticky = E+W)
        self.listBox.bind("<Double-Button-1>", self.onEdit)
        
    def loadList(self, filename):
        if not os.path.exists(filename):
            return
        else:
            f = open(filename, "r")
            
        reader = csv.reader(f)
        for row in reader:
            item = self.itemizer(tuple(row))
            if item:
                self.addItem(item, END)
                
    def saveList(self, filename):
        f = open(filename,"w+")
        for item in self.items:
            f.write(self.serializer(item) + "\n")
        f.close()

    def onClearList(self):
        for i in range(len(self.items)):
            self.listBox.delete("0")
        self.items = []
        
    def onLoadList(self):
        filename = tkFileDialog.askopenfilename(filetypes=[("All files", "*")])
        
        if not os.path.exists(filename):
            tkMessageBox.showerror(title="Wrong Value !", message="File '%s' does not exist !" % filename)
            return
        else:
            self.loadList(filename)
            
    def onSaveList(self):
        filename = tkFileDialog.asksaveasfilename(filetypes=[("All files", "*")])
        if filename:
            self.saveList(filename)
        
    def onEdit(self, *args):
        if len(self.listBox.curselection()) > 0:
            selection = self.listBox.curselection()[0]
            #print self.items[int(selection)]
            tokens = self.editor(self.items[int(selection)])
            if tokens and len(tokens) > 0:
                item = self.itemizer(tokens)
                if item:
                    self.listBox.delete(selection)
                    self.addItem(item, selection)
                
    def onRemove(self):
        if len(self.listBox.curselection()) > 0:
            selection = self.listBox.curselection()[0]
            self.listBox.delete(selection)
            del self.items[int(selection)]
        
    def onAdd(self):
        tokens = self.editor(None)
        if tokens and len(tokens) > 0:
            item = self.itemizer(tokens)
            if item:
                self.addItem(item, END)

    def addItem(self, item, position):
        self.listBox.insert(position, self.formatter(item))
        
        if position <> END:
            self.items[int(position)] = item
        else:
            self.items.append(item)
    
class TextLogger:
    def __init__(self, textField):
        self.textField = textField
        self.s = []

    def write(self, c):
        self.s.append(c)
        if (c == '\n'):
            self.flush()    
    
    def flush(self):
        self.textField.insert(END, ''.join(self.s))
        self.s = []

class TextViewer(Toplevel):
    """
    simple text viewer dialog for idle
    """
    def __init__(self, parent, title, fileName, data=None, xsize = 625, ysize = 500, font = None):
        """If data exists, load it into viewer, otherwise try to load file.

        fileName - string, should be an absolute filename
        """
        Toplevel.__init__(self, parent)
        self.configure(borderwidth=5)
        self.geometry("=%dx%d+%d+%d" % (xsize, ysize,
                                        parent.winfo_rootx() + 10,
                                        parent.winfo_rooty() + 10))
        #elguavas - config placeholders til config stuff completed
        self.bg = '#ffffff'
        self.fg = '#000000'

        self.font = font
        self.CreateWidgets()
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.Ok)
        self.parent = parent
        self.textView.focus_set()
        #key bindings for this dialog
        self.bind('<Return>',self.Ok) #dismiss dialog
        self.bind('<Escape>',self.Ok) #dismiss dialog
        if data:
            self.textView.insert(0.0, data)
        else:
            self.LoadTextFile(fileName)
        self.textView.config(state=DISABLED)
        self.wait_window()

    def LoadTextFile(self, fileName):
        textFile = None
        try:
            textFile = open(fileName, 'r')
        except IOError:
            tkMessageBox.showerror(title='File Load Error',
                    message='Unable to load file %r .' % (fileName,))
        else:
            self.textView.insert(0.0,textFile.read())

    def CreateWidgets(self):
        frameText = Frame(self, relief=SUNKEN, height=700)
        frameButtons = Frame(self)
        self.buttonOk = Button(frameButtons, text='Close',
                               command=self.Ok, takefocus=FALSE)
        self.scrollbarView = Scrollbar(frameText, orient=VERTICAL,
                                       takefocus=FALSE, highlightthickness=0)
                                       
        self.textView = Text(frameText, wrap=WORD, highlightthickness=0,
                             fg=self.fg, bg=self.bg)
        if self.font:
            self.textView.configure(font = self.font)
            
        self.scrollbarView.config(command=self.textView.yview)
        self.textView.config(yscrollcommand=self.scrollbarView.set)
        self.buttonOk.pack()
        self.scrollbarView.pack(side=RIGHT,fill=Y)
        self.textView.pack(side=LEFT,expand=TRUE,fill=BOTH)
        frameButtons.pack(side=BOTTOM,fill=X)
        frameText.pack(side=TOP,expand=TRUE,fill=BOTH)

    def Ok(self, event=None):
        self.destroy()

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.items = []
        self.SEPARATORS = [',',';','\t']

        self.grid(padx = 10, pady = 10)
        self.createWidgets()
        #self.ed = EditorDialog(("Roboto","Patate","Chip   Chip "), self, title= "Edit Roboto", defaults = ("A","B",""))
        #print self.ed.results
        
    def getLog(self):
        return self.outputText
        
    def createWidgets(self):
        # Version title
        self.f1 = tkFont.Font(size = "12", weight = "bold")
        self.titleLabel = Label(self, font = self.f1, text = (VERSION + "\nBy Tennessee Carmel-Veilleux"))
        self.titleLabel.grid(columnspan = 3, row = 0, column = 0, pady = 5)
        
        # Entry for output filename prefix
        self.pFrame = Frame(self)
        self.l1 = Label(self.pFrame, text = "Output filename prefix:")
        self.l1.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = W)
        
        self.outputPrefixVar = StringVar()
        self.prefixEntry = Entry(self.pFrame, width = 30, textvariable = self.outputPrefixVar)
        self.prefixEntry.grid(row = 0, column = 1, sticky = E+W)
        self.outputPrefixVar.set("Order_")
        
        self.pFrame.grid(row = 1, column = 0, columnspan = 3, sticky = W)
        
        # Add the ItemListFrame
        self.l1 = Label(self, text = "Job list:")
        self.l1.grid(row = 2, column = 0, sticky = W)
        
        self.lFrame = ItemListFrame(self.items, self.editItem, self.formatItem, self.validateItem, self.makeItem, self.serializeItem, self)
        
        self.viewButton = Button(self.lFrame.bFrame, text="View file", command = self.onViewFile)
        self.viewButton.grid(row = 0, column = 6, padx = 5)
        
        self.lFrame.grid(columnspan = 3, row = 3, column = 0, padx = 5, sticky = N+S+E+W, pady = 5)
        
        # Add output log
        self.l2 = Label(self, text = "Output log:")
        self.l2.grid(row = 4, column = 0, sticky = W)
        
        self.oFrame = Frame(self)
        
        self.yScroll2 = Scrollbar(self.oFrame, orient=VERTICAL)
        self.yScroll2.grid(row = 0, column = 1, sticky = N+S)
        
        self.xScroll1 = Scrollbar(self.oFrame, orient=HORIZONTAL)
        self.xScroll1.grid(columnspan = 2, row = 1, column = 0, sticky = E+W)
        
        self.outputText = Text(self.oFrame, width = 70, height = 10, wrap = NONE, yscrollcommand = self.yScroll2.set, xscrollcommand = self.xScroll1.set)
        self.outputText.grid(row = 0, column = 0, sticky = N+S+E+W)
        
        self.yScroll2["command"] = self.outputText.yview
        self.xScroll1["command"] = self.outputText.xview
        
        self.oFrame.grid(columnspan = 3, row = 5, column = 0, padx = 5, pady = 5)
        
        # Add execution buttons frame
        self.b2Frame = Frame(self)
        
        self.execButton = Button(self.b2Frame, text="Execute", command=self.onExecute)
        self.execButton.grid(column = 0, row = 0, padx = 10, sticky = E+W)
        
        self.aboutButton = Button(self.b2Frame, text="About...",command=self.onAbout )
        self.aboutButton.grid(column = 1, row = 0, padx = 10, sticky = E+W)
        
        self.aboutButton = Button(self.b2Frame, text="Instructions...",command=self.onHelp )
        self.aboutButton.grid(column = 2, row = 0, padx = 10, sticky = E+W)
        
        self.quitButton = Button(self.b2Frame, text="Quit",command=self.onQuit )
        self.quitButton.grid(column = 3, row = 0, padx = 10, sticky = E+W)
        
        self.b2Frame.grid(columnspan = 3, row = 6, column = 0, sticky = E+W, pady = 10)
        self.bind("<Return>", self.onExecute)
        self.bind("<Escape>", self.onQuit)
        
    def editItem(self, item):
        if item:
            defaults = tuple([k.strip('"') for k in self.serializeItem(item).split(',')])
        else:
            defaults = ("1","","","","","")
    
        ed = EditorDialog(("Multiplicity","_Filename","Reference","Default distributor","?Headers present","$Separator$comma (,)|semicolon (;)|tab"), 
                           self, title= "Edit item...", defaults = defaults)
                           
        return ed.results
        
    def formatItem(self, item):
        # Generate a string suitable for context-accurate display in a listbox
        multiplicity, filename, reference, defaultDist, hasHeaders, separator = item        
        
        s = shortenFilename(filename, 60)
            
        return '%dx "%s" [%s]' % (multiplicity, s, reference)
        
    def serializeItem(self, item):
        # Generate a string representation of the item for saving
        multiplicity, filename, reference, defaultDist, hasHeaders, separator = item
        
        return '"%s","%s","%s","%s","%s","%s"' % (str(multiplicity), filename, reference, defaultDist, str(hasHeaders), str(self.SEPARATORS.index(separator)))
        
    def makeItem(self, tokens):
        # Makes an item tuple with type-conform values from the tokens list
        if self.validateItem(tokens):
            multiplicity, filename, reference, defaultDist, hasHeaders, separator = tokens
            
            multiplicity = int(multiplicity)
            filename = filename.strip()
            reference = reference.strip()
            defaultDist = defaultDist.strip()
            separator = self.SEPARATORS[int(separator)]
            hasHeaders = int(hasHeaders)
            
            return (multiplicity, filename, reference, defaultDist, hasHeaders, separator)
        else:
            return None
                        
    def validateItem(self, tokens):
        # Validate the item from the tokens provided by the editor dialog
        multiplicity, filename, reference, defaultDist, hasHeaders, separator = tokens

        try:
            separator = int(separator)
        except ValueError:
            tkMessageBox.showerror(title="Wrong Value !", message="Separator value incorrect")
            return None
            
        try:
            hasHeaders = int(hasHeaders)
        except ValueError:
            tkMessageBox.showerror(title="Wrong Value !", message="hasHeaders value incorrect")
            return None
            
        try:
            multiplicity = int(multiplicity)
        except ValueError:
            tkMessageBox.showerror(title="Wrong Value !", message="Multiplicity is not an integer")
            return None
            
        if separator not in range(len(self.SEPARATORS)):
            tkMessageBox.showerror(title="Wrong Value !", message="Separator not in correct range")
            return None
            
        if hasHeaders not in range(3):
            tkMessageBox.showerror(title="Wrong Value !", message="Headers thruth value not in correct range")
            return None
            
        if multiplicity < 1:
            tkMessageBox.showerror(title="Wrong Value !", message="Multiplicity must be positive and non-zero")
            return None
        
        if not os.path.exists(filename):
            tkMessageBox.showerror(title="Wrong Value !", message="File '%s' does not exist !" % filename)
            return None
            
        return True

    def onAbout(self, *args):
        v = TextViewer(self, "About %s" % VERSION, None, ABOUT_TEXT, xsize = 400, ysize = 240)
    
    def onHelp(self, *args):
        v = TextViewer(self, "Instructions for MergeBOM", None, HELP_TEXT, font = ("Courier",10))
        
    def onViewFile(self, *args):
        if len(self.lFrame.listBox.curselection()) > 0:
            selection = self.lFrame.listBox.curselection()[0]
            #print self.items[int(selection)]
            filename = self.items[int(selection)][1]
            v = TextViewer(self, "Showing " +  shortenFilename(filename, 50), filename, None)
        
    def onExecute(self, *args):
        self.outputText.delete("1.0", END)
        CollatePartsLists(self.outputPrefixVar.get(), self.items)
        
    def onQuit(self, *args):
        self.quit()

# *********** Mainline **********
if __name__ == "__main__":
    app = Application()
    logfile = TextLogger(app.getLog())
    app.master.title(VERSION)
    app.mainloop() 
