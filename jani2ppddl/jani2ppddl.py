# -*- coding: utf-8 -*-


import argparse
import imp
import sys      
import os
import math
import json
from sympy import *
import re


class Options(object):
        EQUAL = False
        LESS = False
        GREATER = False
        LESS_EQUAL = False 
        GREATER_EQUAL = False
        SUM = False
        SUBSTRACTION = False
        MULTIPLICATION = False
        DIVISION = False
        MAX = False
        MIN = False
        @staticmethod
        def load(f):
                config = imp.load_source("", f)
                for x in ["LESS", "EQUAL", "GREATER", "LESS_EQUAL", "GREATER_EQUAL", "SUM", "SUBSTRACTION", "MULTIPLICATION", "DIVISION", "MAX", "MIN"]:
                        try:
                                val = getattr(config, x)
                                setattr(Options, x, val)
                        except AttributeError:
                                pass


def replace_special_characters(s):
    return re.sub(r"\W", "_", s)


boolVars = set()		#set containing names of all boolean variables
numDummyVars = -1		#counts the dummy variables introduced as helper variables in nested arithmetic expressions
helperVariables = set()	#store helper variables introduced in current action to add them to the precondition list
#effHelperVariables = set()	#store helper variables introduced in the effects of the current action to add them to the precondition list

def isBoolean(varName):	#check if a varaible is a boolean
	return varName in boolVars


def runTree(node):		#run through the restrict-initial tree representation (conjunction of variable initializations)
	if node["op"] == "=":
			if isBoolean(node["left"]):
				if node["right"] == True:
					ppddl_problem.write("\t\t(fulfiled " + node["left"] + ")\n")
			else:
				ppddl_problem.write("\t\t(value " + node["left"] + " n" + str(node["right"]) + ")\n")
	elif node["op"] == u"\u2227":
		runTree(node["left"])
		runTree(node["right"])
	else:
		print "The operator: " + node["op"] + "is not allowed in restrict-initial\n"
		
		
		
def runTreeRI(node, resInit):		#run through the restrict-initial tree representation to collect the variables
	if isinstance(node, bool):		#restrict initial block is empty, i.e. exp: "true"
		return
	if node["op"] == "=":
			if isBoolean(node["left"]):
				if node["right"] == True:
					resInit.add(node["left"])
			else:
				resInit.add(node["left"])
	elif node["op"] == u"\u2227":
		runTreeRI(node["left"], resInit)
		runTreeRI(node["right"], resInit)
	else:
		print "The operator: " + node["op"] + "is not allowed in restrict-initial\n"
		
		
		
def printTree(node, s):		#print expressions for probability
	if isinstance(node, dict):
		s = s + printTree(node["left"], s)
		s = s + node["op"]
		s = s + printTree(node["right"], s)
		return s
	else: 
		return str(node)
		
def searchLeaves(node, destCount):		#search for variables needed in parameters of actions

	if isinstance(node, dict):
		if node.has_key("op"):
			if node["op"] == "=":
				if (not isinstance(node["right"], int)) & (not isinstance(node["left"], bool)):
					leaves.add(node["left"])
					leftLeaves.add(node["left"] + str(destCount))		#need parameter for old and new value
					if not isinstance(node["right"], dict):	#variable name (var1 = var2)
						leaves.add(node["right"])
					return
				elif isinstance(node["right"], int) & (not isinstance(node["left"], dict)):
					preSetInt.add(node["left"])
					return
				else:
					"check what to do with this nested calculation"
					return
			if node["op"] == u"\u2260":
				if (not isinstance(node["right"], int)):		# to avoid parameters for preconditions like (pay != 0)
					searchLeaves(node["left"], destCount)
					searchLeaves(node["right"], destCount)
				return
			if node["op"] in {u"\u003C", u"\u003E",  u"\u2264" , u"\u2265"}:
				if (not isinstance(node["right"], int)):
					leaves.add(node["right"])
				if (not isinstance(node["left"], int)):
					leaves.add(node["left"])
				return
			if node["op"] == "min":
				if isinstance(node["left"], dict):
					leftLeaves.add("x0")
				if isinstance(node["right"], dict):
					leftLeaves.add("x0")
		if node.has_key("left"):						
			if (not isinstance(node["right"], int)):		
				searchLeaves(node["left"], destCount)
				searchLeaves(node["right"], destCount)
				return
			else:
				if (not isinstance(node["left"], int) and not isinstance(node["left"], dict)):
					#print node["left"]
					leftLeaves.add(node["left"] + str(destCount))
					return
				else:
					searchLeaves(node["left"], destCount)
		else:											#case (not ...)
			searchLeaves(node["exp"], destCount)
			return
	else:
		if (not isinstance(node, int)) & (not node in boolVars):
			leaves.add(node)
			#print node
		else:
			return
		
		
def decExp(e, j):		#print expressions in PPDDL syntax for preconditions
	#print e
	global numDummyVars
	s = ""
	if isinstance(e, unicode):		#string, i.e. variable
		if e in boolVars:
			if e in locVars[j]:
				return "(fulfiled " + e +  "_" + data["automata"][j]["name"] + ")"
			else:
				return "(fulfiled " + e + ")"
		elif e in locVars[j]:			#check if it is a local variable
			return "(value " + e + "_" + data["automata"][j]["name"] + " ?vl" + e +")"
		else:
			return "(value " + e + " ?v" + e + ")"
	elif isinstance(e, bool):
		return s
	elif str(e).isdigit():
		return "n"+str(e) 
	elif ((str(e))[1:]).isdigit():			#handle negative integers as 0
		return "n0"
	elif not isinstance(e, dict):
		return "Error: not dict, bool or string\n"
	else:
		#print "162" + str(e)
		eLeftName = ""
		eRightName = ""
		if e.has_key("left"):
			if (not isinstance(e["left"], dict)):
				if (e["left"] in locVars[j]):
					eLeftName = e["left"] + "_" + data["automata"][j]["name"] 
				else:
					eLeftName = e["left"]
			if (not isinstance(e["right"], dict)):
				if (e["right"] in locVars[j]):
					eRightName = e["right"] + "_" + data["automata"][j]["name"] 
				else:
					eRightName = e["right"]
		if e["op"] == u"\u2227":		#logical and
			return "\t\t\t(and \n\t\t\t\t" + decExp(e["left"], j) + "\n\t\t\t\t" + decExp(e["right"], j) + "\n\t\t\t)\n"
		elif e["op"] == u"\u2228":		#logical or
			return "\t\t\t(or \n\t\t\t\t" + decExp(e["left"], j) + "\n\t\t\t\t" + decExp(e["right"], j) + "\n\t\t\t)\n"
		elif e["op"] == u"\u00AC":		#logical not
			return "\t\t\t(not \n" + decExp(e["exp"], j) + "\n\t\t\t)\n"
		elif e["op"] == "=":			#check for equality
			if e["right"] is True:
				return "\t\t\t(fulfiled " + eLeftName + ")\n"
			elif e["right"] is False:
				return "\t\t\t(not (fulfiled " + eLeftName + "))\n"
			else:										#check if it is an integer to avoid variable usage in effects to reset value, reset statement should contain explicit number not a variable
				
				if isinstance(e["right"], int):
					precNum[eLeftName] = e["right"]
					return  "\t\t\t(value " + eLeftName + " n" + str(e["right"]) + ")\n"
				else:			#variable name (var1 != var2) -> (value var1 ?var2) (not(value var1 ?var1))
					if e["left"] in locVars[j]:
						eLeftName = e["left"] + "_" + data["automata"][j]["name"] 
					else:
						eLeftName = e["left"]
				
					if (not isinstance(e["right"], dict)):
						if e["right"] in locVars[j]:
							eRightName = e["right"] + "_" + data["automata"][j]["name"] 
						else:
							eRightName = e["right"]
						
						return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (equal ?v" + eLeftName + " ?v" + eRightName + ")\n"
					else:
						if str(e["right"]["left"]).isdigit():
							eRightLeftName = " n" + str(e["right"]["left"])
						elif e["right"]["left"] in locVars[j]:
							eRightLeftName = " ?v" + e["right"]["left"] + "_" + data["automata"][j]["name"] 
						else:
							eRightLeftName = " ?v" + e["right"]["left"]
					
						if str(e["right"]["right"]).isdigit():
							eRightRightName = " n" +  str(e["right"]["right"])
						elif e["right"]["right"] in locVars[j]:
							eRightRightName = " ?v" + e["right"]["right"] + "_" + data["automata"][j]["name"] 
						else:
							eRightRightName = " ?v" + e["right"]["right"]
						if e["right"]["op"] == "+":
							numDummyVars += 1
							#print numDummyVars
							helperVariables.add("		 ?vlxhelper" + str(numDummyVars))
							#print numDummyVars
							return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"]["left"], j) + " " + "(add" + eRightLeftName + "" + eRightRightName + " ?vlxhelper" + str(numDummyVars) + ") " + "(equal ?v" + eLeftName + " ?vlxhelper" + str(numDummyVars) + ")\n"
						if e["right"]["op"] == "-":
							numDummyVars += 1
							helperVariables.add("		 ?vlxhelper" + str(numDummyVars))
							return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"]["left"], j) + " " + "(sub" +eRightLeftName + eRightRightName + " ?vlxhelper" + str(numDummyVars) + ") " + "(equal" + eLeftName + " ?vlxhelper" + str(numDummyVars) + ")\n"
						if e["right"]["op"] == "*":
							numDummyVars += 1
							helperVariables.add("		 ?vlxhelper" + str(numDummyVars))
							return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"]["left"], j) + " " + "(mult" +eRightLeftName + eRightRightName + " ?vlxhelper" + str(numDummyVars) + ") " + "(equal" + eLeftName + " ?vlxhelper" + str(numDummyVars) + ")\n"
						if e["right"]["op"] == "%":
							numDummyVars += 1
							helperVariables.add("		 ?vlxhelper" + str(numDummyVars))
							return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"]["left"], j) + " " + "(mod" +eRightLeftName + eRightRightName + " ?vlxhelper" + str(numDummyVars) + ") " + "(equal" + eLeftName + " ?vlxhelper" + str(numDummyVars) + ")\n"		
		elif e["op"] == u"\u2260":		#!=		
			if e["left"] in locVars[j]:
				eq = e["left"] + "_" + data["automata"][j]["name"] 
			else:
				eq = e["left"]
				
			if str(e["right"]).isdigit():			#variable name compared to integer
				return "\t\t\t(not (value " + eq + " " + decExp(e["right"], j) + "))\n"
			else:									#two values of variables should be different -> take value of each variable and say that one of them should not have value of the other
				if e["left"] in locVars[j]:
					eLeftName = e["left"] + "_" + data["automata"][j]["name"] 
				else:
					eLeftName = e["left"]
				if (not isinstance(e["right"], dict)):
					if e["right"] in locVars[j]:
						eRightName = e["right"] + "_" + data["automata"][j]["name"] 
					else:
						eRightName = e["right"]
					
					return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (not (equal ?v" + eLeftName + " ?v" + eRightName + "))\n"
				else:
					if str(e["right"]["left"]).isdigit():
						eRightLeftName = " n" + str(e["right"]["left"])
					elif e["right"]["left"] in locVars[j]:
						eRightLeftName = " ?v" + e["right"]["left"] + "_" + data["automata"][j]["name"] 
					else:
						eRightLeftName = " ?v" + e["right"]["left"]
				
					if str(e["right"]["right"]).isdigit():
						eRightRightName = " n" +  str(e["right"]["right"])
					elif e["right"]["right"] in locVars[j]:
						eRightRightName = " ?v" + e["right"]["right"] + "_" + data["automata"][j]["name"] 
					else:
						eRightRightName = " ?v" + e["right"]["right"]
					if e["right"]["op"] == "+":
						numDummyVars += 1
						#print numDummyVars
						helperVariables.add("		 ?vlxhelper" + str(numDummyVars))
						#print numDummyVars
						return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"]["left"], j) + " " + "(add" + eRightLeftName + "" + eRightRightName + " ?vlxhelper" + str(numDummyVars) + ") " + "(not (equal ?v" + eLeftName + " ?vlxhelper" + str(numDummyVars) + "))\n"
					if e["right"]["op"] == "-":
						numDummyVars += 1
						helperVariables.add("		 ?vlxhelper" + str(numDummyVars))
						return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"]["left"], j) + " " + "(sub" +eRightLeftName + eRightRightName + " ?vlxhelper" + str(numDummyVars) + ") " + "(not (equal" + eLeftName + " ?vlxhelper" + str(numDummyVars) + "))\n"
					if e["right"]["op"] == "*":
						numDummyVars += 1
						helperVariables.add("		 ?vlxhelper" + str(numDummyVars))
						return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"]["left"], j) + " " + "(mult" +eRightLeftName + eRightRightName + " ?vlxhelper" + str(numDummyVars) + ") " + "(not (equal" + eLeftName + " ?vlxhelper" + str(numDummyVars) + "))\n"
					if e["right"]["op"] == "%":
						numDummyVars += 1
						helperVariables.add("		 ?vlxhelper" + str(numDummyVars))
						return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"]["left"], j) + " " + "(mod" +eRightLeftName + eRightRightName + " ?vlxhelper" + str(numDummyVars) + ") " + "(not (equal" + eLeftName + " ?vlxhelper" + str(numDummyVars) + "))\n"		
		elif e["op"] == u"\u2264": 		#<=
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + "(leq ?v" + eLeftName + " ?v" + e["right"] + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(leq ?v" + eLeftName + " n" + str(e["right"]) + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + "(leq n" + str(e["left"]) + " ?v" + eRightName + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(leq n" + str(e["left"]) + " n" + str(e["right"]) + ")\n"
			else:
				print "No nested expressions in preconditions\n"		
		elif e["op"] == u"\u2265":		#>=
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (geq ?v" + eLeftName + " ?v" + eRightName + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(geq ?v" + eLeftName + " n" + str(e["right"]) + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + "(geq n" + str(e["left"]) + " ?v" + eRightName + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(geq n" + str(e["left"]) + " n" + str(e["right"]) + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"])[1:].isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(geq ?v" + eLeftName + " n0)\n"
			elif str(e["left"])[1:].isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + "(geq n0" + " ?v" + eRightName + ")\n"
			else:
				print "No nested expressions in preconditions\n"
		elif e["op"] == u"\u003C":		#<
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (less ?v" + eLeftName + " ?v" + eRightName + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(less ?v" + eLeftName + " n" + str(e["right"]) + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + "(less n" + str(e["left"]) + " ?v" + eRightName + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(less n" + str(e["left"]) + " n" + str(e["right"]) + ")\n"
			else:
				print "No nested expressions in preconditions\n"
		elif e["op"] == u"\u003E":		#>
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				#print str(e)
				return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (greater ?v" + eLeftName + " ?v" + eRightName + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(greater ?v" + eLeftName + " n" + str(e["right"]) + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + "(greater n" + str(e["left"]) + " ?v" + eRightName + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(greater n" + str(e["left"]) + " n" + str(e["right"]) + ")\n"
			else:
				print "No nested expressions in preconditions\n"
		elif e["op"] == "+":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (add ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(add ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + " (add n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(add n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in preconditions\n"
		elif e["op"] == "-":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (sub ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(sub ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + " (sub n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit:
				return "\t\t\t(sub n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in preconditions\n"	
		elif e["op"] == "*":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (mult ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(mult ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + " (mult n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(mult n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in preconditions\n"		
		elif e["op"] == "%":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (mod ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(mod ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + " (mod n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(mod n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in preconditions\n"	
		elif e["op"] == "max":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (max ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(max ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + " (max n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(max n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in preconditions\n"	
		elif e["op"] == "min":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["left"], j) + " " + decExp(e["right"], j) + " (min ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + decExp(e["left"], j) + " " + "(min ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + decExp(e["right"], j) + " "  + " (min n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(min n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in preconditions\n"	
		#implications handeled in DNF transformation
		#elif e["op"] == "filter":
		#	if e["fun"] == u"\u2200":		#universal quantifier
		#		return "\t\t\t(forall " +  ")\n"
		#	elif e["fun"] == u"\u2203":		#existential quantifier
		#		return "\t\t\t(exists " +  ")\n"
		else:
			return "Error: not supported in PPDDL\n"

			
							#this function is used to bring the formulas into an abstract form, abstracting away from concrete variables, i.e. only x1 /\ x2 \/ ~ x3, ..., used for DNF transformation of preconditions
def boolExp(e):				#get boolean expression for jani guards, i.e. preconditions
	global b				#global counter for expression abstraction
	global varXValues		#dictionary for expression and abstract variable
	if isinstance(e, dict): 
		if e["op"] ==  u"\u2227":  #and
			return And(boolExp(e["left"]), boolExp(e["right"]))
		elif e["op"] ==  u"\u2228":	#or
			return Or(boolExp(e["left"]), boolExp(e["right"]))
		elif e["op"] ==  u"\u00AC":	#not
			return Not(boolExp(e["exp"]))
		elif e["op"] == u"\u21D2":	#impl
			return Implies(boolExp(e["left"]), boolExp(e["right"]))
		else:
			varXValues.append(e)
			b += 1
			return symbols("x" + str(b))		#the expression is now encoded as a variable xN and can be reconstructed by accessing varXValues at the index b
	else:
		varXValues.append(e)
		b += 1
		return symbols("x" + str(b))
				
		
def getOclauses(expr):    #get clauses for DNFs 
    if not isinstance(expr, Or):
        return expr,
    return expr.args
	
def getAclauses(expr):    #get clauses for CNFs
    if not isinstance(expr, And):
        return expr,
    return expr.args			

	
def preconFromAss(assList, j, resInit, leaves, destCount, preconSet):			#calculate results of arithm. operations in effects which need to be already in preconditions
	lName = ""																	#preconSet is used to avoid duplicates if the precondition is introduced by multiple destinations/effect parts
	rName = ""
	
	global numDummyVars
	global helperVariables
	#global effHelperVariables
	
	retVars = set()						#set of return variables, i.e. ref-values
	if len(assList) > 1:				#check if there are variables introduced only for help to split up calculations 
		for ass in assList:
			if isinstance(ass["value"], dict):
				retVars.add(ass["ref"])
	retVars = retVars.difference(resInit)
	
	
	for ass in assList:
		if str(ass["value"]).isdigit():
			if ass["ref"] in locVars[j]:		#figure out name of participating variables (local/global)
				refName = ass["ref"]  +  "_" + data["automata"][j]["name"] 
			else:
				refName = ass["ref"] 
			if not (ass["ref"] in retVars):			#if variable where result is assigned to is not a helper variable, current value is needed to delete it in effects
				if ass["ref"] in leaves:
					preconSet.add("\t\t\t(value " + refName + " ?v" + refName + ")\n")
		elif isinstance(ass["value"], bool):
			print "Usually no effect on preconditions, but check what to do in your special case ;-)"
			pass
		elif (isinstance(ass["value"], basestring)):	#the value of another variable is assigned, e.g. x = y
			refName = ass["ref"]
			preconSet.add( "\t\t\t(value " + refName + " ?v" + refName + ")\n")
			assName = ass["value"]
			preconSet.add( "\t\t\t(value " + assName + " ?vl" + refName + str(destCount)+ ")\n"	)		#no ?vl only ?v, because the variables are either different or it is really the same value
		else:							#value is result of arithm. operation
			op = ass["value"]["op"]		
			if ass["ref"] in locVars[j]:		#figure out name of participating variables (local/global)
				refName = ass["ref"] +  "_" + data["automata"][j]["name"] 
			else:
				refName = ass["ref"] 
			if not (ass["ref"] in retVars):			#if variable where result is assigned to is not a helper variable, current value needed to delete it in effects
				preconSet.add( "\t\t\t(value " + refName + " ?v" + refName + ")\n")
			if (not str(ass["value"]["left"]).isdigit()) & (not isinstance(ass["value"]["left"], dict)):	#filter out nested calculations like max(1, x + y)
				if ass["value"]["left"] in locVars[j]:
					lName = ass["value"]["left"]  +  "_" + data["automata"][j]["name"] 
				else:
					lName = ass["value"]["left"]
			if (not str(ass["value"]["right"]).isdigit()) & (not isinstance(ass["value"]["right"], dict)):
				if ass["value"]["right"] in locVars[j]:
					rName = ass["value"]["right"]  +  "_" + data["automata"][j]["name"] 
				else:
					rName = ass["value"]["right"]
			if op == "+":										#check combination of int and variable names in expression
				if isinstance(ass["value"]["left"], unicode) & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["left"] in retVars)) & (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(add ?v" + lName + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					elif (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(add ?v" + lName + " ?vl" + rName + " ?vl" + refName+ str(destCount) + ")\n")
					elif (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(add ?vl" + lName + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					else:
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet("\t\t\t(add ?v" + lName + " ?vl" + rName + " ?vl" + refName + str(destCount)+ ")\n")
						
				elif isinstance(ass["value"]["left"], unicode) & str(ass["value"]["right"]).isdigit():
					if (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(add ?v" + lName + " n" + str(ass["value"]["right"])+ " ?vl" + refName + str(destCount)+ ")\n")
					else:
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(add ?v" + lName + " n" + str(ass["value"]["right"])+ " ?vl" + refName+ str(destCount) + ")\n")
				elif str(ass["value"]["left"]).isdigit() & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(add n" + str(ass["value"]["left"]) + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					else:
						preconSet.add( "\t\t\t(add n" + str(ass["value"]["left"])+ " ?vl" + rName + " ?vl"+ str(destCount) + refName + ")\n")
				elif str(ass["value"]["left"]).isdigit() & str(ass["value"]["right"]).isdigit():
					preconSet.add( "\t\t\t(add n" + str(ass["value"]["left"]) + " n" + str(ass["value"]["right"]) + " ?vl" + refName + str(destCount)+ ")\n")
			elif op == "-":
				if isinstance(ass["value"]["left"], unicode) & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["left"] in retVars)) & (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(sub ?v" + lName + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					elif (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(sub ?v" + lName + " ?vl" + rName + " ?vl" + refName +  + str(destCount) + ")\n")
					elif (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(sub ?vl" + lName + " ?v" + rName + " ?vl"+ refName +  str(destCount) + ")\n")
					else:
						preconSet.add( "\t\t\t(sub ?vl" + lName + " ?vl" + rName + " ?vl" + refName + str(destCount) + ")\n")
						
				elif isinstance(ass["value"]["left"], unicode) & str(ass["value"]["right"]).isdigit():
					if ((not (ass["value"]["left"] in retVars)) | (ass["value"]["left"] == ass["ref"])):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(sub ?v" + lName + " n" + str(ass["value"]["right"]) + " ?vl" + refName + str(destCount)+  ")\n")
					else:
						preconSet.add( "\t\t\t(sub ?vl" + lName + " n" + str(ass["value"]["right"]) + " ?vl" + refName + str(destCount)+ ")\n")
				elif str(ass["value"]["left"]).isdigit() & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(sub n" + str(ass["value"]["left"]) + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					else:
						preconSet.add( "\t\t\t(sub n" + str(ass["value"]["left"])+ " ?vl" + rName + " ?vl" + refName+ str(destCount) + ")\n")
				elif str(ass["value"]["left"]).isdigit() & str(ass["value"]["right"]).isdigit():
					preconSet.add( "\t\t\t(sub n" + str(ass["value"]["left"]) + " n" + str(ass["value"]["right"])+ " ?vl" + refName + str(destCount)+ ")\n")
			elif op == "*":
				if isinstance(ass["value"]["left"], unicode) & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["left"] in retVars)) & (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(mult ?v" + lName + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					elif (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(mult ?v" + lName + " ?vl" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					elif (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(mult ?vl" + lName + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					else:
						preconSet.add( "\t\t\t(mult ?vl" + lName + " ?vl" + rName + " ?vl" + refName+ str(destCount) + ")\n")
						
				elif isinstance(ass["value"]["left"], unicode) & str(ass["value"]["right"]).isdigit():
					if (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(mult ?v" + lName + " n" + str(ass["value"]["right"]) + " ?vl" + refName+ str(destCount) + ")\n")
					else:
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(mult ?v" + lName + " n" + str(ass["value"]["right"])+ " ?vl" + refName + str(destCount)+ ")\n")
				elif str(ass["value"]["left"]).isdigit() & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(mult n" + str(ass["value"]["left"])+ " ?v" + rName + "? vl" + refName + str(destCount)+ ")\n")
					else:
						preconSet.add( "\t\t\t(mult n" + str(ass["value"]["left"]) + " ?vl" + rName + "? vl" + refName + str(destCount) + ")\n")
				elif str(ass["value"]["left"]).isdigit() & str(ass["value"]["right"]).isdigit():
					preconSet.add( "\t\t\t(mult n" + str(ass["value"]["left"]) + " n" + str(ass["value"]["right"]) + "? vl" + refName + str(destCount)+ ")\n")
			elif op == "%":
				if isinstance(ass["value"]["left"], unicode) & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["left"] in retVars)) & (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(mod ?v" + lName + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					elif (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(mod ?v" + lName + " ?vl" + rName + " ?vl" + refName + str(destCount) + ")\n")
					elif (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(mod ?vl" + lName + " ?v" + rName + " ?vl" + refName+ str(destCount) + ")\n")
					else:
						preconSet.add( "\t\t\t(mod ?vl" + lName + " ?vl" + rName + " ?vl" + refName + str(destCount)+ ")\n")
						
				elif isinstance(ass["value"]["left"], unicode) & str(ass["value"]["right"]).isdigit():
					if (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(mod ?v" + lName + " n" + str(ass["value"]["right"]) + " ?vl" + refName+ str(destCount) + ")\n")
					else:
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(mod ?v" + lName + " n" + str(ass["value"]["right"]) + " ?vl" + refName + str(destCount)+ ")\n")
				elif str(ass["value"]["left"]).isdigit() & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(mod n" + str(ass["value"]["left"])+ " ?v" + rName + " ?vl" + refName+ str(destCount) + ")\n")
					else:
						preconSet.add( "\t\t\t(mod n" + str(ass["value"]["left"])+ " ?vl" + rName + " ?vl" + refName+ str(destCount) + ")\n")
				elif str(ass["value"]["left"]).isdigit() & str(ass["value"]["right"]).isdigit():
					preconSet.add( "\t\t\t(mod n" + str(ass["value"]["left"])+ " n" + str(ass["value"]["right"]) +  " ?vl" + refName + str(destCount)+ ")\n")
			elif op == "max":
				if isinstance(ass["value"]["left"], unicode) & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["left"] in retVars)) & (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(max ?v" + lName + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					elif (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(max ?v" + lName + " ?vl" + rName + " ?vl" + refName + str(destCount) + ")\n")
					elif (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(max ?vl" + lName + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					else:
						preconSet.add( "\t\t\t(max ?vl" + lName + " ?vl" + rName + " ?vl" + refName + str(destCount)+ ")\n")
						
				elif isinstance(ass["value"]["left"], unicode) & str(ass["value"]["right"]).isdigit():
					if (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(max ?v" + lName + " n" + str(ass["value"]["right"]) + " ?vl" + refName+ str(destCount) + ")\n")
					else:
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(max ?v" + lName + " n" + str(ass["value"]["right"]) + " ?vl" + refName + str(destCount)+ ")\n")
				elif str(ass["value"]["left"]).isdigit() & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(max n" + str(ass["value"]["left"])+ " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					else:
						preconSet.add( "\t\t\t(max n" + str(ass["value"]["left"])+ " ?vl" + rName + " ?vl" + refName+ str(destCount) + ")\n")
				elif str(ass["value"]["left"]).isdigit() & str(ass["value"]["right"]).isdigit():
					preconSet.add( "\t\t\t(max n" + str(ass["value"]["left"]) + " n" + str(ass["value"]["right"]) + " ?vl" + refName + str(destCount)+ ")\n")
			elif op == "min":
				#print "min case found"
				if isinstance(ass["value"]["left"], unicode) & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["left"] in retVars)) & (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(min ?v" + lName + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					elif (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(min ?v" + lName + " ?vl" + rName + " ?vl" + refName + str(destCount) + ")\n")
					elif (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(min ?vl" + lName + " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					else:
						preconSet.add( "\t\t\t(min ?vl" + lName + " ?vl" + rName + " ?vl" + refName + str(destCount)+ ")\n")
						
				elif isinstance(ass["value"]["left"], unicode) & str(ass["value"]["right"]).isdigit():
					if (not (ass["value"]["left"] in retVars)):
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(min ?v" + lName + " n" + str(ass["value"]["right"]) + " ?vl" + refName+ str(destCount) + ")\n")
					else:
						preconSet.add( "\t\t\t(value " + lName + " ?v" + lName + ")\n")
						preconSet.add("\t\t\t(min ?v" + lName + " n" + str(ass["value"]["right"]) + " ?vl" + refName + str(destCount)+ ")\n")
				elif str(ass["value"]["left"]).isdigit() & isinstance(ass["value"]["right"], unicode):
					if (not (ass["value"]["right"] in retVars)):
						preconSet.add( "\t\t\t(value " + rName + " ?v" + rName + ")\n")
						preconSet.add("\t\t\t(min n" + str(ass["value"]["left"])+ " ?v" + rName + " ?vl" + refName + str(destCount)+ ")\n")
					else:
						preconSet.add( "\t\t\t(min n" + str(ass["value"]["left"])+ " ?vl" + rName + " ?vl" + refName+ str(destCount) + ")\n")
				elif str(ass["value"]["left"]).isdigit() & str(ass["value"]["right"]).isdigit():
					preconSet.add( "\t\t\t(min n" + str(ass["value"]["left"]) + " n" + str(ass["value"]["right"]) + " ?vl" + refName + str(destCount)+ ")\n")
				elif str(ass["value"]["left"]).isdigit() & isinstance(ass["value"]["right"], dict):		#nested calculation in min(), pay attention to predicates and if necessary (value ...) is taken in precondition
					#print "in min case !!!!!!!!!!!!!!!!!!!!!!!!"
					numDummyVars += 1
					helperVariables.add("		 ?vlxhelper" + str(numDummyVars))
					#effHelperVariables.add("		?vlxhelper" + str(numDummyVars))
					preconSet.add("\t\t\t(value " + str(ass["value"]["right"]["left"]) + " ?v" + str(ass["value"]["right"]["left"]) + ")\n")
					preconSet.add("\t\t\t(add ?v" + str(ass["value"]["right"]["left"]) + " n" + str(ass["value"]["right"]["right"])+ " ?vlxhelper" + str(numDummyVars) + ")\n")
					preconSet.add( "\t\t\t(min n" + str(ass["value"]["left"])+ " ?vlxhelper" + str(numDummyVars) + " ?vl" + refName+ str(destCount) + ")\n")
			else:
				print "operation " + op + " in " + str(ass) + " not supported\n"
	return				
			
			
def no_syncs():		#check if synchronisation between two or more actions is needed
	ret = True
	if not data["system"].has_key("syncs"):
		return True
	else:
		syncList = [list() for _ in xrange(len(data["system"]["syncs"]))]	#list of actions (names) synchronising with each other
		i = 0
		for s in data["system"]["syncs"]:
			syn = 0
			for act in s["synchronise"]:
				if act != None:
					syncList[i].append(act)
					syn += 1
			if syn > 1:
				ret = False
			i += 1
		return ret
			
	
	
def printGoal(e):		#parse properties expression to figure out goal expression behind until, similar to decExp
	s = ""
	if isinstance(e, unicode):		#string, i.e. variable
		if e in boolVars:
			return "(fulfiled " + e + ")"
		else:
			return "(value " + e + " ?v" + e + ")"
	elif isinstance(e, bool):
		return s
	elif str(e).isdigit():
		return "n"+str(e) 
	elif not isinstance(e, dict):
		return "Error: not dict, bool or string\n"
	else:
		eLeftName = ""
		eRightName = ""
		if e.has_key("left"):
			if (not isinstance(e["left"], dict)):
				eLeftName = e["left"]
			if (not isinstance(e["right"], dict)):
				eRightName = e["right"]
		if e["op"] == u"\u2227":		#logical and
			return "\t\t\t(and \n\t\t\t\t" + printGoal(e["left"]) + "\t\t\t\t" + printGoal(e["right"]) + "\n\t\t\t)\n"
		elif e["op"] == u"\u2228":		#logical or
			return "\t\t\t(or \n\t\t\t\t" + printGoal(e["left"]) + "\t\t\t\t" + printGoal(e["right"]) + "\n\t\t\t)\n"
		elif e["op"] == u"\u00AC":		#logical not
			return "\t\t\t(not \n" + printGoal(e["exp"]) + "\n\t\t\t)\n"
		elif e["op"] == "=":			#check for equality
			if e["right"] is True:
				return "\t\t\t(fulfiled " + eLeftName + ")\n"
			elif e["right"] is False:
				return "\t\t\t(not (fulfiled " + eLeftName + "))\n"
			else:										#check if it is an integer to avoid variable usage in effects to reset value
				return"\t\t\t(value " + eLeftName + " " + printGoal(e["right"]) + ")\n"
		elif e["op"] == u"\u2260":		#!=
			eq = e["left"]
			return "\t\t\t(not (and " + printGoal(e["left"]) + " " + printGoal(e["right"]) + "))\n"
		elif e["op"] == u"\u2264": 		#<=
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["left"]) + " " + printGoal(e["right"]) + "(leq ?v" + eLeftName + " ?v" + e["right"] + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + printGoal(e["left"]) + " " + "(leq ?v" + eLeftName + " n" + str(e["right"]) + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["right"]) + " "  + "(leq n" + str(e["left"]) + " ?v" + eRightName + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(leq n" + str(e["left"]) + " n" + str(e["right"]) + ")\n"
			else:
				print "No nested expressions in goals\n"		
		elif e["op"] == u"\u2265":		#>=
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["left"]) + " " + printGoal(e["right"]) + " (geq ?v" + eLeftName + " ?v" + eRightName + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + printGoal(e["left"]) + " " + "(geq ?v" + eLeftName + " n" + str(e["right"]) + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["right"]) + " "  + "(geq n" + str(e["left"]) + " ?v" + eRightName + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(geq n" + str(e["left"]) + " n" + str(e["right"]) + ")\n"
			else:
				print "No nested expressions in goals\n"
		elif e["op"] == u"\u003C":		#<
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["left"]) + " " + printGoal(e["right"]) + " (less ?v" + eLeftName + " ?v" + eRightName + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + printGoal(e["left"]) + " " + "(less ?v" + eLeftName + " n" + str(e["right"]) + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["right"]) + " "  + "(less n" + str(e["left"]) + " ?v" + eRightName + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(less n" + str(e["left"]) + " n" + str(e["right"]) + ")\n"
			else:
				print "No nested expressions in goals\n"
		elif e["op"] == u"\u003E":		#>
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["left"]) + " " + printGoal(e["right"]) + " (greater ?v" + eLeftName + " ?v" + eRightName + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + printGoal(e["left"]) + " " + "(greater ?v" + eLeftName + " n" + str(e["right"]) + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["right"]) + " "  + "(greater n" + str(e["left"]) + " ?v" + eRightName + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(greater n" + str(e["left"]) + " n" + str(e["right"]) + ")\n"
			else:
				print "No nested expressions in goals\n"
		elif e["op"] == "+":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["left"]) + " " + printGoal(e["right"]) + " (add ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + printGoal(e["left"]) + " " + "(add ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["right"]) + " "  + " (add n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(add n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in goals\n"
		elif e["op"] == "-":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["left"]) + " " + printGoal(e["right"]) + " (sub ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + printGoal(e["left"]) + " " + "(sub ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["right"]) + " "  + " (sub n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit:
				return "\t\t\t(sub n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in goals\n"	
		elif e["op"] == "*":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["left"]) + " " + printGoal(e["right"]) + " (mult ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + printGoal(e["left"]) + " " + "(mult ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["right"]) + " "  + " (mult n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(mult n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in goals\n"		
		elif e["op"] == "%":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["left"]) + " " + printGoal(e["right"]) + " (mod ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + printGoal(e["left"]) + " " + "(mod ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["right"]) + " "  + " (mod n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(mod n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in goals\n"	
		elif e["op"] == "max":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["left"]) + " " + printGoal(e["right"]) + " (max ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + printGoal(e["left"]) + " " + "(max ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["right"]) + " "  + " (max n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(max n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in goals\n"	
		elif e["op"] == "min":
			if isinstance(e["left"], unicode) & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["left"]) + " " + printGoal(e["right"]) + " (min ?v" + eLeftName + " ?v" + eRightName +" ?v" + eq + ")\n"
			elif isinstance(e["left"], unicode) & str(e["right"]).isdigit():
				return "\t\t\t" + printGoal(e["left"]) + " " + "(min ?v" + eLeftName + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & isinstance(e["right"], unicode):
				return "\t\t\t" + printGoal(e["right"]) + " "  + " (min n" + str(e["left"]) + " ?v" + eRightName + " ?v" + eq + ")\n"
			elif str(e["left"]).isdigit() & str(e["right"]).isdigit():
				return "\t\t\t(min n" + str(e["left"]) + " n" + str(e["right"]) + " ?v" + eq + ")\n"
			else:
				print "No nested expressions in goals\n"
		#elif e["op"] == u"\u21D2":		#"⇒" Implication
		#	return "\t\t\t(imply " +  decExp(e["left"], j) + " " + decExp(e["right"], j) + ")\n"
		#elif e["op"] == "filter":
		#	if e["fun"] == u"\u2200":		#universal quantifier
		#		return "\t\t\t(forall " +  ")\n"
		#	elif e["fun"] == u"\u2203":		#existential quantifier
		#		return "\t\t\t(exists " +  ")\n"
		else:
			return "Error: not supported in PPDDL\n"
			
				
def parseArith(e):
	stack = []
	currVal = 0
	
	while(isinstance(e, dict)):
		if(isinstance(e["right"], int)):
			stack.append(e["right"])
		else:
			r = parseArith(e["right"])
			stack.append(r)
		stack.append(e["op"])
		e = e["left"]
		
	currVal = e
	
	while stack:			#not empty
		op = stack.pop()
		nextVal = stack.pop()
		currVal = eval(str(currVal) + op + str(nextVal))
		
	return currVal



arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("jani", help="JANI input file")
arg_parser.add_argument("--config", "-c", default=None, help="configuration file")
args = arg_parser.parse_args()

if args.config:
        Options.load(args.config)

with open(args.jani, "rb") as f:
        data = json.load(f)					  # error if it is not a valid JSON file

try:
	domain_file = args.jani[:-5]+"-domain.ppddl"
	ppddl_domain = open(domain_file, "w")
	
	problem_file = args.jani[:-5]+"-problem.ppddl"
	ppddl_problem = open(problem_file, "w")
	
	#domain file
	
	ppddl_domain.write("; " + data["type"] + "\n")		#automata type and metadata as comments
	if data.has_key("metadata"):
		ppddl_domain.write("; " + str(data["metadata"]) + "\n")
	
	
	ppddl_domain.write("(define (domain " + replace_special_characters(data["name"]) + ")\n")
	
	#requirements		#commented out because planner can not cope with it
	#"\t(:requirements :strips :typing :equality :conditional-effects  :probabilistic-effects :rewards :expression-evaluation :action-costs :fluents :negative-preconditions :disjunctive-preconditions :existential-preconditions :universal-preconditions)\n")
	
	ppddl_domain.write("\t(:types ")	#types
	types = set()
	numNeed = False
	types.add("loc") 				#location always needed
	types.add("bool")				#bool for goal_condition always needed
	for t in data["variables"]:
		if isinstance(t["type"], dict):
			types.add(t["type"]["base"])	#bounded "int" or "real" build own type "type_lower_upper"
			if t["type"]["base"] == "int":
				numNeed = True				
		else:
			types.add(t["type"])
			if t["type"]== "int":
				numNeed = True	
	if data.has_key("constants"):
		for t in data["constants"]:
			if isinstance(t["type"], dict):
				types.add(t["type"]["base"])
				if t["type"]["base"] == "int":
					numNeed = True	
			else:
				types.add(t["type"])
				if t["type"] == "int":
					numNeed = True	
	locVars = [set() for _ in xrange(len(data["automata"]))]	#needed to change the names st. all names are globally unique
	i = 0
	for a in data["automata"]:	#local variables in automatons
		if a.has_key("variables"):
			for v in a["variables"]:
				locVars[i].add(v["name"])
				if isinstance(v["type"], dict):
					types.add(v["type"]["base"])
					if v["type"]["base"] == "int":
						numNeed = True	
				else:
					locVars[i].add(v["name"])
					types.add(v["type"])
					if v["type"] == "int":
						numNeed = True	
		i = i+1
	ppddl_domain.write(re.sub('[,]'," ",', '.join(types)))		#no ',' separating types
	if numNeed:
		ppddl_domain.write("  num")
	ppddl_domain.write(")\n")
	
	
	
	minVar = sys.maxint		#to figure out the range of arithmetic calculations
	maxVar = 0
	
	varDict = {}			#dictionnary to find type of global vars
	locVarDict = {}			#dictionnary to find type of local vars of automatons
	
	
	ppddl_domain.write("\t(:constants\n")		#constants
	
	ppddl_domain.write("\t\tgoal_condition - bool\n")
		
	#declare objects from problem file in domain as constants to be able to use them directly in action descriptions
	for v in data["variables"]:
		if isinstance(v["type"], dict):			#variableName - type
			ppddl_domain.write("\t\t" + v["name"] + " - " + v["type"]["base"] + "\n")
			varDict[v["name"]] = v["type"]["base"]
			if minVar > v["type"]["lower-bound"]:
				minVar = v["type"]["lower-bound"]
			if maxVar < v["type"]["upper-bound"]:
				maxVar = v["type"]["upper-bound"]	
		else:
			ppddl_domain.write("\t\t" + v["name"] + " - " + v["type"] + "\n")
			if(v["type"] == "bool"):
					boolVars.add(v["name"])
			varDict[v["name"]] = v["type"]
		
	if data.has_key("constants"):
		for c in data["constants"]:					#constantName - type
			if isinstance(c["type"], dict):
				ppddl_domain.write("\t\t" + c["name"] + " - " + c["type"]["base"] + "\n")
				varDict[c["name"]] = c["type"]["base"]
				if minVar > v["type"]["lower-bound"]:
					minVar = v["type"]["lower-bound"]
				if maxVar < v["type"]["upper-bound"]:
					maxVar = v["type"]["upper-bound"]
			else:
				ppddl_domain.write("\t\t" + c["name"] + " - " + c["type"] + "\n")
				if(c["type"] == "bool"):
					boolVars.add(c["name"])
				varDict[c["name"]] = c["type"]
			
	for a in data["automata"]:			#local variables in automatons: variableName_automatonName - type
		locVarDict[a["name"]] = {}
		if a.has_key("variables"):
			for v in a["variables"]:
				if isinstance(v["type"], dict):
					ppddl_domain.write("\t\t" + v["name"] + "_" + a["name"] + " - " + v["type"]["base"] + "\n")
					locVarDict[a["name"]][v["name"]] = v["type"]["base"]
					if minVar > v["type"]["lower-bound"]:
						minVar = v["type"]["lower-bound"]
					if maxVar < v["type"]["upper-bound"]:
						maxVar = v["type"]["upper-bound"]
				else:
					ppddl_domain.write("\t\t" + v["name"] + "_" + a["name"] + " - " + v["type"] + "\n")	
					locVarDict[a["name"]][v["name"]] = v["type"]
					if v["type"] == "bool":
						locVarDict[a["name"]][v["name"]] = "bool"
						boolVars.add(v["name"])
						#print("added" + v["name"] +"\n") 
		for l in a["locations"]:			#locationName 
			ppddl_domain.write("\t\t" + l["name"] + "_" + a["name"] + " - loc\n")
			
			
	ppddl_domain.write("\t\t")	
	for i in range(minVar, maxVar+1):			#introduce numbers in required range
		ppddl_domain.write("n" + str(i) + " ")   
	ppddl_domain.write("- num\n")	
		
	ppddl_domain.write("\t)\n")
	
	
	
	ppddl_domain.write("\t(:predicates\n")		#predicates
	if "bool" in types:
		ppddl_domain.write("\t\t(fulfiled ?x - bool)\n")	#predicate "fulfiled" for boolean variables
		
	ppddl_domain.write("\t\t(at ?l - loc)\n")				#predicate for locations
	for t in types:
		if ((t != "bool") & (t != "loc")):						#only ints (+ reals)
			ppddl_domain.write("\t\t(value ?v - " + str(t) + " ?n - num)\n")
	
	if Options.EQUAL:
			ppddl_domain.write("\t\t(equal ?n1 ?n2 - num)\n")		#arithmetic =
	if Options.LESS:
			ppddl_domain.write("\t\t(less ?n1 ?n2 - num)\n")		#arithmetic <
	if Options.GREATER:
			ppddl_domain.write("\t\t(greater ?n1 ?n2 - num)\n")		#>
	if Options.LESS_EQUAL:
			ppddl_domain.write("\t\t(leq ?n1 ?n2 - num)\n")			#<=
	if Options.GREATER_EQUAL:
			ppddl_domain.write("\t\t(geq ?n1 ?n2 - num)\n")			#>=
	if Options.SUM:
			ppddl_domain.write("\t\t(add ?n1 ?n2 ?n3 - num)\n")		#+
	if Options.SUBSTRACTION:
			ppddl_domain.write("\t\t(sub ?n1 ?n2 ?n3 - num)\n")		#-
	if Options.MULTIPLICATION:
			ppddl_domain.write("\t\t(mult ?n1 ?n2 ?n3 - num)\n")		#*
	if Options.DIVISION:
			ppddl_domain.write("\t\t(mod ?n1 ?n2 ?n3 - num)\n")		#/
	if Options.MAX:
			ppddl_domain.write("\t\t(max ?n1 ?n2 ?n3 - num)\n")			#maximum
	if Options.MIN:
			ppddl_domain.write("\t\t(min ?n1 ?n2 ?n3 - num)\n")			#minimum
	ppddl_domain.write("\t)\n")
	
	
	ppddl_domain.write("\t(:functions\n")		#functions
	#ppddl_domain.write("\t\t(total-cost)\n")
	ppddl_domain.write("\t)\n")

	
	if no_syncs():
		j = 0
		for a in data["automata"]:					#actions
			name = a["name"]
			actionNames = set()						#make sure that all actions have unique names
			countActions = 0
			for e in a["edges"]:
				countActions = countActions+1
				actionName = ""
				act1 = ""							#partition action string into two parts: before preconditions (containing or) and after preconditions
				act2 = ""
				act1 += "\t(:action "
				endDest = ""
				for d in e["destinations"]:
					endDest += "_" + d["location"]
				if e.has_key("action"): 				#if the edge has an action name
					actionName = replace_special_characters(e["action"]) +"_"+ name +"_"+ e["location"] + "_to_" + endDest	#action name: "[actionName]_automataName_startLocation_to_endLocations"
					i = 0
					if actionName in actionNames:			#if action names are still not unique, number them
						i = 1
						actionName += "_" + str(i)
						while actionName in actionNames:
							i += 1 
							actionName = actionName.rsplit("_", 1)[0] + "_" + str(i)
					actionNames.add(actionName)
				else: 
					actionName = name +"_"+ e["location"] + "_to_" + endDest
					i = 0
					if actionName in actionNames:
						i = 1
						actionName += "_" + str(i)
						while actionName in actionNames:
							i += 1
							actionName = actionName.rsplit("_", 1)[0] + "_" +str(i)
					actionNames.add(actionName)
					
				actParam = "" 				#action PPDDL string until end of parameter list	
				act11 = ""					#split action PPDDL String such that action name can be indexed for each DNF clause 
				
				helperVariables.clear()	#clean the set for every action
					
				actParam += "\n\t\t:parameters ("					#parameters = variables for predicates
				leaves = set()									#all variables affected arithmetically
				leftLeaves = set()								#variables on the left of = affected arithmetically, old and new value needed
				preSetInt = set()
				destCount=0
				if e.has_key("guard"):
					searchLeaves(e["guard"]["exp"], destCount)
					#print leftLeaves
				destCount=0
				for d in e["destinations"]:
					if d.has_key("assignments"):
						for asg in d["assignments"]:
							if (not isinstance(asg["value"], int)) & (not isinstance(asg["value"], bool)):		#exclude integers !and booleans!
								leftLeaves.add(str(asg["ref"])+ str(destCount))
								leaves.add(str(asg["ref"]))
								searchLeaves(asg["value"], destCount)
							else:
								if (not (asg["ref"] in preSetInt)) & (not asg["ref"] in boolVars):		#for int effects where value in precondition is not known
									leaves.add(str(asg["ref"]))
					destCount += 1
				for l in leaves:								#which variables have to be introduced? (only for one or also for old value)
					if varDict.has_key(l):
						actParam += "\n\t\t ?v" + l + " - num"
					elif locVarDict[name].has_key(l):
						actParam += "\n\t\t ?v" + l + "_" + name + " - num"
					else:
						actParam += "\n\t\t ?v" + l + " - num"
				for ll in leftLeaves:							#for new and old value
					m = re.search(r'\d+$', ll)
					# if the string ends in digits m will be a Match object, or None otherwise.
					if m is not None:
						test_var = ll[:-1]
					else:
						test_var = ll
					if varDict.has_key(test_var):
						actParam += "\n\t\t ?vl" + ll + " - num"
					elif locVarDict[name].has_key(ll):
						actParam += "\n\t\t ?vl" + ll + "_" + name + " - num"
					else:
						actParam += "\n\t\t ?vl" + ll + " - num"
				
				act11 += "\n\t\t)"
				
				
				act11 += "\n\t\t:precondition ("					#preconditions
				precNum = {}										#to store precondition value of integers
				preconSet = set()									#store preconditions in set to avoid duplicates
				if e.has_key("guard"):
					if isinstance(e["guard"]["exp"], bool):			#no preconditions on variables
						parts = []									#partition list of preconditions, stays empty in this case
						tmp = ""
						destCount = 0								#number of destinations for indexing parameters
						for d in e["destinations"]:
							if d.has_key("assignments"):
								resInit = set() 					#set of variables used in restrict initial
								if data.has_key("restrict-initial"):
									runTreeRI(data["restrict-initial"]["exp"], resInit)	#check which are hepler variables to split calculations
								preconFromAss(d["assignments"], j, resInit, leaves, destCount, preconSet)	
							destCount += 1
						if len(preconSet) == 0:
							act11 += "\n\t\t\t at " + e["location"] + "_" + name + "\n"	#correct start location
						else:
							act11 += "\n\t\t\t and (at " + e["location"] + "_" + name + ")\n" 
						for s in preconSet:
							tmp += s
						act11 += tmp + "\n"
					else:
						act11 += "\n\t\t\tand (at " + e["location"]+ "_" + name + ")\n"
																
						#boolean expressions in guards
						#create list containing all precondition partitions
						b=0		#count variables in boolean formula (DNF)
						varXValues = []
						parts = []							#partition list of preconditions
						res = boolExp(e["guard"]["exp"])	#encode the guard as an abstract boolean expression
						#print res
						if (isinstance(res, Or) | isinstance(res, And) | isinstance(res, Not) | isinstance(res, Implies)):
							resDNF = to_dnf(res)			#convert the bexp into DNF
							#print resDNF

							Oclauses = getOclauses(resDNF)	#get the clauses of the DNF (connected by \/)

							for o in Oclauses:
								#print o
								precDict = {}
								if isinstance(o, And):
									Aclauses = getAclauses(o)
									#print Aclauses
									a1 = Aclauses[0]
									if isinstance(a1, Not):	
										if not isinstance(varXValues[int(str(a1.args[0])[1:])-1], unicode):
											if varXValues[int(str(a1.args[0])[1:])-1]["op"] == u"\u2264":		#<=
												left = {"op": u"\u003E", "left": varXValues[int(str(a1.args[0])[1:])-1]["left"], "right": varXValues[int(str(a1.args[0])[1:])-1]["right"]}		#the full jani expression of an abstract variable can be reconstructed by a look-up in the varXValues dictionary, take the abstract variable (xb), cut off the first letter ([1:])(here 'x') and receive the index number 'b' (from the construction in boolExp), subtract 1, because we started with b = 1, but indexing starts with 0 
											elif varXValues[int(str(a1.args[0])[1:])-1]["op"] == u"\u2265":		#>=
												left = {"op": u"\u003C", "left": varXValues[int(str(a1.args[0])[1:])-1]["left"], "right": varXValues[int(str(a1.args[0])[1:])-1]["right"]}
											elif varXValues[int(str(a1.args[0])[1:])-1]["op"] == u"\u003E":		#>
												left = {"op": u"\u2264", "left": varXValues[int(str(a1.args[0])[1:])-1]["left"], "right": varXValues[int(str(a1.args[0])[1:])-1]["right"]}
											elif varXValues[int(str(a1.args[0])[1:])-1]["op"] ==  u"\u003C":	#<
												left = {"op": u"\u2265", "left": varXValues[int(str(a1.args[0])[1:])-1]["left"], "right": varXValues[int(str(a1.args[0])[1:])-1]["right"]}
												#print "\n 1128: " + str(left)
										else:			# it is only a negated variable not a negated expression
											left = {"op": u"\u00AC", "exp": varXValues[int(str(a1.args[0])[1:])-1]}
									else:
										left = varXValues[int(str(a1)[1:])-1]
									
									a2 = Aclauses[1]			#there should always be at least two entries for a disjunction
									if isinstance(a2, Not):	
										if not isinstance(varXValues[int(str(a2.args[0])[1:])-1], unicode):									
											if varXValues[int(str(a2.args[0])[1:])-1]["op"] == u"\u2264":		#<=
												right = {"op": u"\u003E", "left": varXValues[int(str(a2.args[0])[1:])-1]["left"], "right": varXValues[int(str(a2.args[0])[1:])-1]["right"]}
											elif varXValues[int(str(a2.args[0])[1:])-1]["op"] == u"\u2265":		#>=
												right = {"op": u"\u003C", "left": varXValues[int(str(a2.args[0])[1:])-1]["left"], "right": varXValues[int(str(a2.args[0])[1:])-1]["right"]}
											elif varXValues[int(str(a2.args[0])[1:])-1]["op"] == u"\u003E":		#>
												right = {"op": u"\u2264", "left": varXValues[int(str(a2.args[0])[1:])-1]["left"], "right": varXValues[int(str(a2.args[0])[1:])-1]["right"]}
											elif varXValues[int(str(a2.args[0])[1:])-1]["op"] ==  u"\u003C":	#<
												right = {"op": u"\u2265", "left": varXValues[int(str(a2.args[0])[1:])-1]["left"], "right":varXValues[int(str(a2.args[0])[1:])-1]["right"]}
												#print "\n 1144: " + str(right)
										else:
											right = {"op": u"\u00AC", "exp": varXValues[int(str(a2.args[0])[1:])-1]}
									else:
										right = varXValues[int(str(a2)[1:])-1]
									precDict["op"] = u"\u2227"
									precDict["left"] = left
									precDict["right"] = right
									for aelem in Aclauses[2:]:		#skip first 2 elements
										if isinstance(aelem, Not):
											if not isinstance(varXValues[int(str(aelem.args[0])[1:])-1], unicode):			
												if varXValues[int(str(aelem.args[0])[1:])-1]["op"] == u"\u2264":		#<=
													precDict = {"op": u"\u2227", "left": {"op": u"\u003E", "left": varXValues[int(str(aelem.args[0])[1:])-1]["left"], "right": varXValues[int(str(aelem.args[0])[1:])-1]["right"]} , "right": precDict}
												elif varXValues[int(str(aelem.args[0])[1:])-1]["op"] == u"\u2265":		#>=
													precDict = {"op": u"\u2227", "left": {"op": u"\u003C", "left": varXValues[int(str(aelem.args[0])[1:])-1]["left"], "right": varXValues[int(str(aelem.args[0])[1:])-1]["right"]} , "right": precDict}
												elif varXValues[int(str(aelem.args[0])[1:])-1]["op"] == u"\u003E":		#>
													precDict = {"op": u"\u2227", "left": {"op": u"\u2264", "left": varXValues[int(str(aelem.args[0])[1:])-1]["left"], "right": varXValues[int(str(aelem.args[0])[1:])-1]["right"]} , "right": precDict}
												elif varXValues[int(str(aelem.args[0])[1:])-1]["op"] ==  u"\u003C":	#<
													precDict = {"op": u"\u2227", "left": {"op":  u"\u2265", "left": varXValues[int(str(aelem.args[0])[1:])-1]["left"], "right": varXValues[int(str(aelem.args[0])[1:])-1]["right"]}, "right": precDict}
													#print "\n 1164: " + str(precDict)
												else:	#=
													precDict = {"op": u"\u2227", "left": {"op": u"\u2260", "left": varXValues[int(str(aelem.args[0])[1:])-1]["left"], "right": varXValues[int(str(aelem.args[0])[1:])-1]["right"]} , "right": precDict}
											else:	#onyl a negated boolean variable
												precDict = {"op": u"\u2227", "left": {"op": u"\u00AC", "exp": varXValues[int(str(aelem.args[0])[1:])-1]} , "right": precDict}
										else:
											precDict = {"op": u"\u2227", "left": varXValues[int(str(aelem)[1:])-1], "right": precDict}
									parts.append(precDict)
									#print precDict
								else:
									if isinstance(o, Not):
										parts.append({"op": u"\u00AC", "exp": varXValues[int(str(o)[2:])-1]})		#cut off the negation ~ with [2:]
									else:
										parts.append(varXValues[int(str(o)[1:])-1])

									pass #parts.append({"op": u"\u00AC", "left": {"op": u"\u00AC", "exp": }, "right": {"op": u"\u00AC", "exp": })#Verneinung aus Verundung der verneinten Elemente
						else:
							parts.append(varXValues[0])	
						
						tmpDE = decExp(e["guard"]["exp"], j)		#relict from former code without DNF transformation, call needed to get precNum dictionnary needed for effects on integer variables refering to preconditions
						destCount = 0
						for d in e["destinations"]:					#preconditions required for int assignments
							if d.has_key("assignments"):
								resInit = set() 		#set of variables used in restrict initial
								if data.has_key("restrict-initial"):
									runTreeRI(data["restrict-initial"]["exp"], resInit)	#check which are hepler variables to split calculations
								preconFromAss(d["assignments"], j, resInit, leaves, destCount, preconSet)
							destCount += 1
						for s in preconSet:
							act11 += s
				else:
					tmp = ""
					parts = []		#partition list of preconditions
					destCount = 0
					for d in e["destinations"]:
						if d.has_key("assignments"):
							resInit = set() 		#set of variables used in restrict initial
							if data.has_key("restrict-initial"):
								runTreeRI(data["restrict-initial"]["exp"], resInit)	#check which are hepler variables to split calculations
							preconFromAss(d["assignments"], j, resInit, leaves, destCount, preconSet)
							#if resPFA == "":
							#	act11 += "\n\t\t\t at " + e["location"] + "_" + name + "\n"	#correct start location
							#else:
							#	act11 += "\n\t\t\t and( (at " + e["location"] + "_" + name + ")\n" + resPFA + "\n"
						destCount += 1
					if len(preconSet) == 0:
						act11 += "\n\t\t\t at " + e["location"] + "_" + name + "\n"	#correct start location
					else:
						act11 += "\n\t\t\t and (at " + e["location"] + "_" + name + ")\n"
						for s in preconSet:
							act11 += s
						act11 += "\n"
					
				act2 += "\n\t\t)"
				
				#effHelperVariables.clear()
				
				act2 += "\n\t\t:effect ("				#effects
				act2 += "\n\t\t\tprobabilistic\n"
				destCount = 0
				for d in e["destinations"]:
					s = ""  
					
					if d.has_key("assignments"):		#assignments are effects
						if ((len(d["assignments"]) == 0) & (e["location"] == d["location"])):
							act2 += "\t\t\t" + printTree(d["probability"]["exp"], s) + "()\n" #empty effect
							print "Empty effects are not supported in FD!\n"
						else:
							if d.has_key("probability"):
								act2 += "\t\t\t" + printTree(d["probability"]["exp"], s) + "\n"   #probability of ending in new "location" when taking this edge
							else:
								act2 += "\t\t\t 1 \n"  
							if e["location"] != d["location"]:						
								act2 += "\t\t\t\t(and (at " + d["location"] + "_" + a["name"] + ")\n"		#new location, delete old location
								act2 += "\t\t\t\t\t(not (at " + e["location"] + "_" + a["name"] + "))\n" 
							if (e["location"] == d["location"]):
								act2 += "\t\t\t\t(and \n"
							for assign in d["assignments"]:
								if assign["value"] is True:			#boolean effects
									if assign["ref"] in locVars[j]:	#check if it is a local variable -> extend name
										act2 += "\t\t\t\t\t(fulfiled " + assign["ref"] + "_" + a["name"] + ")\n"
									else:
										act2 += "\t\t\t\t\t(fulfiled " + assign["ref"] + ")\n"
								elif assign["value"] is False:
									if assign["ref"] in locVars[j]:
										act2 += "\t\t\t\t\t(not (fulfiled " + assign["ref"] + "_" + a["name"] + "))\n"
									else:
										act2 += "\t\t\t\t\t(not (fulfiled " + assign["ref"] + "))\n"
								elif str(assign["value"]).isdigit():		#integer effects
									if assign["ref"] in leaves:				#there is a predicate for the variable value
										if assign["ref"] in locVars[j]:
											act2 += "\t\t\t\t\t(not (value " + str(assign["ref"]) + "_" + a["name"] + " ?v" + str(assign["ref"]) + "_" + a["name"] + "))\n"
											act2 += "\t\t\t\t\t(value " + str(assign["ref"]) + "_" + a["name"] + " n" + str(assign["value"]) + ")\n" 	#number nX, X=value
										else:
											act2 += "\t\t\t\t\t(not (value " + str(assign["ref"]) + " ?v" + str(assign["ref"]) + "))\n"
											act2 += "\t\t\t\t\t(value " + str(assign["ref"]) + " n" + str(assign["value"]) + ")\n"
									else:									#no predicate variable, value in preconditions was int
										if assign["ref"] in locVars[j]:
											if precNum.has_key(assign["ref"]):
												act2 += "\t\t\t\t\t(not (value " + str(assign["ref"]) + "_" + a["name"] + " n" + precNum[assign["ref"]] + "))\n"
											else:
												act2 += "\t\t\t\t\t(not (value " + str(assign["ref"]) + "_" + a["name"] + " ?v" + str(assign["ref"]) + "_" + a["name"] + "))\n"
											act2 += "\t\t\t\t\t(value " + str(assign["ref"]) + "_" + a["name"] + " n" + str(assign["value"]) + ")\n" 	#number nX, X=value
										else:
											if precNum.has_key(assign["ref"]):
												act2 += "\t\t\t\t\t(not (value " + str(assign["ref"]) + " n" + str(precNum[assign["ref"]]) + "))\n"
											act2 += "\t\t\t\t\t(value " + str(assign["ref"]) + " n" + str(assign["value"]) + ")\n"
										
								else:											#handle arithmetic expressions -> calculation in preconditions
									if data.has_key("restrict-initial"):		#restrict-initial in automaton
										if (data["restrict-initial"]["exp"] != True):		#if true: no initial restrictions
											resInit = set() 		#set of variables used in restrict initial
											runTreeRI(data["restrict-initial"]["exp"], resInit)
									#if assign["ref"] in resInit:				#if it is not a hepler variable to split calculations
									#	print "passiert nichts"
									act2 += "\t\t\t\t\t(not (value " + str(assign["ref"]) + " ?v" + str(assign["ref"]) + "))\n"
									act2 += "\t\t\t\t\t(value " + str(assign["ref"]) + " ?vl" + str(assign["ref"]) + str(destCount) + ")\n"
							#if (len(d["assignments"]) > 0):
							act2 += "\t\t\t\t)\n"			#close and
					elif e["location"] != d["location"]:														#only change location, no further effects
						act2 += ("\n\t\t\tprobabilistic " + printTree(d["probability"]["exp"], s) + 
						"\n\t\t\t\t and (at " + d["location"] + "_" + a["name"] + ")\n")	
											#delete old location
						act2 += "\t\t\t\t\t(not (at " + e["location"] + "_" + a["name"] + "))\n"
					destCount += 1
					
				act2 += "\t\t)\n"			#close effect
				act2 += "\t)\n\n"			#close action
				
				
				pNum = 0		#count number of clauses in DNF for this action
				if len(parts) == 0:
					for hvar in helperVariables:
						actParam += "\n" + hvar + " - num"
					ppddl_domain.write(act1 + actionName + str(pNum) + actParam +act11 + act2)		
					pNum += 1
				else:
					for p in parts:			#print all actions resulting from partitioning disjunctions, each disjunct (clause) has unique action name (index)
						actParamPart = actParam
						helperVariables.clear()
						dep = decExp(p, j)
						#print helperVariables
						for hvar in helperVariables:
							actParamPart += "\n" + hvar + " - num"
						#for hvareff in effHelperVariables:
						#	actParamPart += "\n" + hvareff + " - num"
						ppddl_domain.write(act1 + actionName + str(pNum) + actParamPart + act11 + dep + act2)		#!!!hier wirds zusammen gebaut!!!
						pNum += 1
				
			j = j+1
			
		
		# get one action per clause in goal DNF, precondition: clause, effect: goal condition fullfilled 
		
		goalDisjuncts = []		#partition list of clauses
		
		for p in data["properties"]:
		
			b=0		#count variables in boolean formula (DNF)
			varXValues = []
			goalDisjuncts = []		#partition list of clauses
		
																		#search for goal description in property
			goalOp = p["expression"]["values"]["op"]					#parse down until binary op reached, step over exp like neg
			#print str(p["expression"]["values"]) +"\n" 
			if p["expression"]["values"].has_key("right"):
				goalRight = p["expression"]["values"]["right"]
			else:
				goalOp = p["expression"]["values"]["exp"]["op"]
				goalRight = p["expression"]["values"]["exp"]["right"]
			while ((goalOp != "U") & (goalOp != "F")):										#search for until or finally operator, expression behind describes properties of goal states
				goalOp = goalRight["op"]
				if goalRight.has_key("right"):
					goalRight = goalRight["right"]
				else:
					goalOp = goalRight["exp"]["op"]
					goalRight = goalRight["exp"]["right"]
			#ppddl_problem.write(printGoal(goalRight))
		
			res = boolExp(goalRight)			#convert goal description (starting at goalRight) into boolExp, like for disjunctive actions
			#print res							#same procedure as above for preconditions, see comments there for explanation
			if (isinstance(res, Or) | isinstance(res, And) | isinstance(res, Not) | isinstance(res, Implies)):
				resDNF = to_dnf(res)
				#print resDNF

				Oclauses = getOclauses(resDNF)

				for o in Oclauses:
					precDict = {}
					if isinstance(o, And):
						Aclauses = getAclauses(o)
						a1 = Aclauses[0]
						if isinstance(a1, Not):	
							if varXValues[int(str(a1.args[0])[1:])-1]["op"] == u"\u2264":		#<=
								left = {"op": u"\u003E", "left": varXValues[int(str(a1.args[0])[1:])-1]["left"], "right": varXValues[int(str(a1.args[0])[1:])-1]["right"]}
							elif varXValues[int(str(a1.args[0])[1:])-1]["op"] == u"\u2265":		#>=
								left = {"op": u"\u003C", "left": varXValues[int(str(a1.args[0])[1:])-1]["left"], "right": varXValues[int(str(a1.args[0])[1:])-1]["right"]}
							elif varXValues[int(str(a1.args[0])[1:])-1]["op"] == u"\u003E":		#>
								left = {"op": u"\u2264", "left": varXValues[int(str(a1.args[0])[1:])-1]["left"], "right": varXValues[int(str(a1.args[0])[1:])-1]["right"]}
							elif varXValues[int(str(a1.args[0])[1:])-1]["op"] ==  u"\u003C":	#<
								left = {"op": u"\u2265", "left": varXValues[int(str(a1.args[0])[1:])-1]["left"], "right": varXValues[int(str(a1.args[0])[1:])-1]["right"]}
							else:
								left = {"op": u"\u00AC", "exp": varXValues[int(str(a1.args[0])[1:])-1]}
						else:
							left = varXValues[int(str(a1)[1:])-1]
						a2 = Aclauses[1]
						if isinstance(a2, Not):	
							if varXValues[int(str(a2.args[0])[1:])-1]["op"] == u"\u2264":		#<=
								right = {"op": u"\u003E", "left": varXValues[int(str(a2.args[0])[1:])-1]["left"], "right": varXValues[int(str(a2.args[0])[1:])-1]["right"]}
							elif varXValues[int(str(a2.args[0])[1:])-1]["op"] == u"\u2265":		#>=
								right = {"op": u"\u003C", "left": varXValues[int(str(a2.args[0])[1:])-1]["left"], "right": varXValues[int(str(a2.args[0])[1:])-1]["right"]}
							elif varXValues[int(str(a2.args[0])[1:])-1]["op"] == u"\u003E":		#>
								right = {"op": u"\u2264", "left": varXValues[int(str(a2.args[0])[1:])-1]["left"], "right": varXValues[int(str(a2.args[0])[1:])-1]["right"]}
							elif varXValues[int(str(a2.args[0])[1:])-1]["op"] ==  u"\u003C":	#<
								right = {"op": u"\u2265", "left": varXValues[int(str(a2.args[0])[1:])-1]["left"], "right": varXValues[int(str(a2.args[0])[1:])-1]["right"]}
							else:
								right = {"op": u"\u00AC", "exp": varXValues[int(str(a2.args[0])[1:])-1]}
						else:
							right = varXValues[int(str(a2)[1:])-1]
						precDict["op"] = u"\u2227"
						precDict["left"] = left
						precDict["right"] = right
						for aelem in Aclauses[2:]:		#skip first 2 elements
							if isinstance(aelem, Not):	
								if not isinstance(varXValues[int(str(aelem.args[0])[1:])-1], unicode):
									if varXValues[int(str(aelem.args[0])[1:])-1]["op"] == u"\u2264":		#<=
										precDict = {"op": u"\u2227", "left": {"op": u"\u003E", "left": varXValues[int(str(aelem.args[0])[1:])-1]["left"], "right": varXValues[int(str(aelem.args[0])[1:])-1]["right"]} , "right": precDict}
									elif varXValues[int(str(aelem.args[0])[1:])-1]["op"] == u"\u2265":		#>=
										precDict = {"op": u"\u2227", "left": {"op": u"\u003C", "left": varXValues[int(str(aelem.args[0])[1:])-1]["left"], "right": varXValues[int(str(aelem.args[0])[1:])-1]["right"]} , "right": precDict}
									elif varXValues[int(str(aelem.args[0])[1:])-1]["op"] == u"\u003E":		#>
										precDict = {"op": u"\u2227", "left": {"op": u"\u2264", "left": varXValues[int(str(aelem.args[0])[1:])-1]["left"], "right": varXValues[int(str(aelem.args[0])[1:])-1]["right"]} , "right": precDict}
									elif varXValues[int(str(aelem.args[0])[1:])-1]["op"] ==  u"\u003C":	#<
										precDict = {"op": u"\u2227", "left": {"op":  u"\u2265", "left": varXValues[int(str(aelem.args[0])[1:])-1]["left"], "right": varXValues[int(str(aelem.args[0])[1:])-1]["right"]} , "right": precDict}
									else:
										precDict = {"op": u"\u2227", "left": {"op": u"\u2260", "left": varXValues[int(str(aelem.args[0])[1:])-1]["left"], "right": varXValues[int(str(aelem.args[0])[1:])-1]["right"]} , "right": precDict}
								else:	#onyl a negated boolean variable
									precDict = {"op": u"\u2227", "left": {"op": u"\u00AC", "exp": varXValues[int(str(aelem.args[0])[1:])-1]} , "right": precDict}
							else:
								precDict = {"op": u"\u2227", "left": varXValues[int(str(aelem)[1:])-1], "right": precDict}
						goalDisjuncts.append(precDict)
						#print precDict
					else:
						if isinstance(o, Not):
							goalDisjuncts.append({"op": u"\u00AC", "exp": varXValues[int(str(o)[2:])-1]})		#cut off the negation ~ with [2:]
						else:
							goalDisjuncts.append(varXValues[int(str(o)[1:])-1])

						pass
			else:
				goalDisjuncts.append(varXValues[0])	

		g=0									#one action for each clause of goal DNF
		for goalClause in goalDisjuncts:
			ppddl_domain.write("\t(:action achieveGoal" + str(g) + "\n")
			ppddl_domain.write("\t\t:parameters(\n")
			
															#like in normal actions, but without local variables
			leaves = set()									#all variables affected arithmetically
			leftLeaves = set()								#variables on the left of = affected arithmetically, old and new value needed
			preSetInt = set()
			destCount = 0
			searchLeaves(goalClause, destCount)
			
			for l in leaves:								
				if varDict.has_key(l):
					ppddl_domain.write("\t\t\t?v" + l + " - num\n")
				else:
					print "local variable in goal\n"
			for ll in leftLeaves:							#for new and old value
				if varDict.has_key(ll):
					ppddl_domain.write("\t\t\t?vl" + ll + " - num\n")
				else:
					print "local variable in goal\n"
	
		
		
			ppddl_domain.write("\t\t)\n")
			ppddl_domain.write("\t\t:precondition\n" + decExp(goalClause, 0) + "\n")	#convert goalClause from Jani into PPDDL
			ppddl_domain.write("\t\t:effect(\n\t\t\tprobabilistic\n\t\t\t 1 \n \t\t\t (fulfiled goal_condition)\n\t\t)\n")
			ppddl_domain.write("\t)\n\n")
			g += 1
		
		
	else:
		print "Non-trivial synchronisation is not supported, please preprocess the input-file\n"
		#TODO: combined action for synchronisation: precondition: precond of all actions, effect: effects of all actions
		#combine all actions of name1 with all actions of name2 (for sync of 2 actions)
		#how to support indices indicating order of assignments/value changes?
	ppddl_domain.write("\n)")
		
		
		
			
			
	#problem file
	
	ppddl_problem.write("(define (problem " + replace_special_characters(data["name"]) + 
							")\n\t(:domain " + replace_special_characters(data["name"]) + 
							")\n\t(:objects\n")						#objects	#shifted to domain->constants to be able to use them directly in the action definitions		
	ppddl_problem.write("\t)\n")
	
	
	
	ppddl_problem.write("\t(:init \n")			#init
	#ppddl_problem.write("\t\t(= (total-cost) 0)\n")
	for a in data["automata"]:					#initial locations in automaton
		for l in a["initial-locations"]:
			ppddl_problem.write("\t\t(at " + l + "_" + a["name"] + ")\n")
		if a.has_key("restrict-initial"):		#restrict-initial in automaton
			if (a["restrict-initial"]["exp"] != True):		#if true: no initial restrictions
				runTree(a["restrict-initial"]["exp"])	
		if a.has_key("variables"):		#local variables of automata
			for t in a["variables"]:	
				if isinstance(t["type"], dict):
					if t.has_key("initial-value"):
						if isinstance(t["initial-value"], dict):
							val = parseArith(t["initial-value"])
							ppddl_problem.write("\t\t(value " + t["name"] + "_" + a["name"] + " n" + str(val) + ")\n") 
						else:
							ppddl_problem.write("\t\t(value " + t["name"] + "_" + a["name"] + " n" + str(t["initial-value"]) + ")\n")		#it is a number nX
					else: 
						pass
			
	for t in data["variables"]:			#variables
		if isinstance(t["type"], dict):
			if t.has_key("initial-value"):
				if isinstance(t["initial-value"], dict):
					val = parseArith(t["initial-value"])
					ppddl_problem.write("\t\t(value " + t["name"] + " n" + str(val) + ")\n") 
				else:
					ppddl_problem.write("\t\t(value " + t["name"] + " n" + str(t["initial-value"]) + ")\n")		#it is a number nX
			else: 
				pass
		else:
			if t["type"] == "bool":
				boolVars.add(t["name"])
				if t.has_key("initial-value"):
					if t["initial-value"] == True:
						ppddl_problem.write("\t\t(fulfiled " + t["name"] + " )\n")
				else:
					pass
			else:
				if t.has_key("initial-value"): 
					if isinstance(t["initial-value"], dict):
						val = parseArith(t["initial-value"])
						ppddl_problem.write("\t\t(value " + t["name"] + " n" + str(val) + ")\n") 
					else:
						ppddl_problem.write("\t\t(value " + t["name"] + " n" + str(t["initial-value"]) + ")\n")		#it is a number nX
				else:
					pass
	if data.has_key("constants"):							
		for t in data["constants"]:			#constants
			if t.has_key("value"):
				if isinstance(t["type"], dict):
					if isinstance(t["value"], dict):
						val = parseArith(t["value"])
						ppddl_problem.write("\t\t(value " + t["name"] + " n" + str(val) + ")\n") 
					else:
						ppddl_problem.write("\t\t(value " + t["name"] + " n" + str(t["value"]) + ")\n") 		#it is a number nX
				else:
					if t["type"] == "bool":
						boolVars.add(t["name"])
						if t["value"] == True:
							ppddl_problem.write("\t\t(fulfiled " + t["name"] + " )\n")
					else:
						if isinstance(t["value"], dict):
							val = parseArith(t["value"])
							ppddl_problem.write("\t\t(value " + t["name"] + " n" + str(val) + ")\n") 
						else:
							ppddl_problem.write("\t\t(value " + t["name"] + " n" + str(t["value"]) + ")\n")		#it is a number nX
	
	if data.has_key("restrict-initial"):
		if (data["restrict-initial"]["exp"] != True):	#restrict-initial, if true: no initial restrictions
			runTree(data["restrict-initial"]["exp"])
			
	#arithmetic
	for n1 in range(minVar, maxVar+1, 1): 
		for n2 in range(minVar, maxVar+1, 1):
                        if Options.SUM and n1 + n2 <= maxVar:
                                ppddl_problem.write("\t\t(add n" + str(n1) + " n" + str(n2) + " n" + str(n1+n2) + ")\n")
			if Options.SUBSTRACTION and n1 - n2 >= minVar:
				ppddl_problem.write("\t\t(sub n" + str(n1) + " n" + str(n2) + " n" + str(n1-n2) + ")\n")
			if Options.MULTIPLICATION and n1 * n2 <= maxVar:
				ppddl_problem.write("\t\t(mult n" + str(n1) + " n" + str(n2) + " n" + str(n1*n2) + ")\n")
			if Options.DIVISION and n2 != 0:
				if n1/n2 >= minVar:
					ppddl_problem.write("\t\t(mod n" + str(n1) + " n" + str(n2) + " n" + str(n1%n2) + ")\n")
			if Options.MAX:
				ppddl_problem.write("\t\t(max n" + str(n1) + " n" + str(n2) + " n" + str(max(n1,n2)) + ")\n")
			if Options.MIN:
				ppddl_problem.write("\t\t(min n" + str(n1) + " n" + str(n2) + " n" + str(min(n1,n2)) + ")\n")
			
	for n1 in range(minVar, maxVar+1, 1):
                if Options.EQUAL:
                        ppddl_problem.write("\t\t(equal n" + str(n1) + " n" + str(n1) + ")\n")
                if Options.LESS_EQUAL:
                	ppddl_problem.write("\t\t(leq n" + str(n1) + " n" + str(n1) + ")\n")
		for n2 in range(n1+1, maxVar+1, 1):
                    if Options.LESS:
                                ppddl_problem.write("\t\t(less n" + str(n1) + " n" + str(n2) + ")\n")
                    if Options.LESS_EQUAL:
                		ppddl_problem.write("\t\t(leq n" + str(n1) + " n" + str(n2) + ")\n")
			
	for n1 in range(maxVar, minVar-1, -1):
                if Options.GREATER_EQUAL:
                        ppddl_problem.write("\t\t(geq n" + str(n1) + " n" + str(n1) + ")\n")
		for n2 in range(minVar, n1, 1):
                        if Options.GREATER:
                                ppddl_problem.write("\t\t(greater n" + str(n1) + " n" + str(n2) + ")\n")
                        if Options.GREATER_EQUAL:
                                ppddl_problem.write("\t\t(geq n" + str(n1) + " n" + str(n2) + ")\n")
	

	ppddl_problem.write("\t)")
	
	
	ppddl_problem.write("\n\t(:goal \n")	
	
	if data.has_key("properties"):
		#try:
		#	if data["property"]["expression"]["op"] == "filter":
		#		pass
		#	elif data["property"]["expression"]["op"] == "Pmin":
		#		pass
		#	elif data["property"]["expression"]["op"] == "Pmax":
		#		pass
		#	elif data["property"]["expression"]["op"] == u"\u2200":		#universal quantifier
		#		pass
		#	elif data["property"]["expression"]["op"] == u"\u2203":		#existential quantifier
		#		pass
		#except:
		#	ppddl_problem.write("\t;Goal not transferable to PPDDL\n")
			
		ppddl_problem.write("\t\t(fulfiled goal_condition)")
			
	else:
		ppddl_problem.write("\t;No goal specified\n")
	
	ppddl_problem.write("\n\t)")
	
	#ppddl_problem.write("\n\t(:metric minimize (total-cost))")
	#ppddl_problem.write("\n\t(:metric maximize (goal-achieved))")		 #probability to achieve goal
	#ppddl_problem.write("\n\t(:metric minimize (reward))")
	
	ppddl_problem.write("\n)")
	
			
finally:
	ppddl_domain.close()
	ppddl_problem.close()
