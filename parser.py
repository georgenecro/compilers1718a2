#!/usr/bin/env python3
# -*- coding: utf_8 -*-

"""
Example of recursive descent parser written by hand using plex module as scanner
NOTE: This progam is a language recognizer only.

Sample grammar from p.242 of:
Grune, Dick, Jacobs, Ceriel J.H., "Parsing Techniques, A Practical Guide" 2nd ed.,Springer 2008.

"""


import plex



class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass



class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """
	
	def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """

		# define some pattern constructs
		letter = plex.Range("AZaz")
		digit = plex.Range("09")
		
		bools1 = plex.Str("true","false")											# orismos boolean operator
		bools2 = plex.Str("t","f")													# orismos boolean operator
		bools3 = plex.Str("0", "1")													# orismos boolean operator
	
		AND = plex.Str("and")														# orismos logical operator
		OR = plex.Str("or")															# orismos logical operator
		NOT = plex.Str("not")														# orismos logical operator
		
		string = plex.Rep1(letter | digit)
		operator = plex.Any("!?()")		
		space = plex.Any(" \t\n")

		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		lexicon = plex.Lexicon([
			(bools1,plex.TEXT),
			(bools2,plex.TEXT),
			(bools3,plex.TEXT),
			(AND,plex.TEXT),
			(NOT,plex.TEXT),
			(OR,plex.TEXT),
			(operator,plex.TEXT),
			(space,plex.IGNORE),
			(string, 'string')
			])
		
		# create and store the scanner object
		self.scanner = plex.Scanner(lexicon,fp)
		
		# get initial lookahead
		self.la,self.val = self.next_token()


	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		

	
	def position(self):
		""" Utility function that returns position in text in case of errors.
		Here it simply returns the scanner position. """
		
		return self.scanner.position()
	

	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		
		if self.la==token:
			self.la,self.val = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	
	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		
		# create the plex scanner for fp
		self.create_scanner(fp)
		
		# call parsing logic
		self.session()
	
			
	def session(self):																# checking and / not
		
		if self.la=='AND' or self.la=='NOT':
			self.facts()
			self.question()
		elif self.la=='(':
			self.match('(')
			self.session()
			self.match(')')
			self.session()	
		else:
			raise ParseError("in facts: NOT/AND/(")
			 	
	
	def facts(self):																# checking and, not
		
		if self.la=='AND':
			self.fact()
			self.facts()
		elif self.la=='NOT':	# from FOLLOW set!
			return
		else:
			raise ParseError("in facts: AND/NOT")
	
	
	def fact(self):																# checking not
		
		if self.la=='NOT':
			self.match('not')
			self.match('string')
		else:
			raise ParseError("in fact: NOT")
			 	

	def question(self):
		
		if self.la=='?':
			self.match('?')
			self.match('string')
		else:
			raise ParseError("in question: ? expected")

		
# the main part of prog

# create the parser object
parser = MyParser()

fp = input('give some input>')

	# parse file
try:
	parser.parse(fp)
except plex.errors.PlexError:
	_,lineno,charno = parser.position()	
	print("Scanner Error: at line {} char {}".format(lineno,charno+1))
except ParseError as perr:
	_,lineno,charno = parser.position()	
	print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))
