#!/usr/bin/env python 
# -*- coding: utf-8 -*-

################################################################################
# Besier-console is a "console" comands based extension to create besier paths 
# with exact dimensions.
#
# Syntax:
#	command[; command]
# Command:
#	type  [parameters]; 
#	Types:
#		a (arc)	
#		l (line)
#		h (hline)
#		v (vline)
#		m (move)
#	Parameters :
#		l - length
#		a - angle
#		x,y - coordinates
#		all values are relative if the case is lover to use absolute coordinates use upper case.
################################################################################

from csp import CSP
from points import P
from math import *
import inkex
import re
import sys
import traceback


def warn(s) :
	if bezier_console.options.silent : return
	s = str(s)
	inkex.errormsg(s+"\n")		
	
def error(s) :
	if bezier_console.options.silent : return
	s = str(s)
	inkex.errormsg(s+"\n")		
	sys.exit()

class BezierConsole(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("", "--string",					action="store", type="string", 		dest="s", default="",					help="Draw string")
		self.OptionParser.add_option("", "--silent",					action="store", type="inkbool", 	dest="silent", default=True,				help="Do not show an errors, usable for live preview")
		self.OptionParser.add_option("",   "--units",					action="store", type="float", 		dest="units", default="3.543307",		help="Units scale")		
	def get_line_xy(self,x,y,a,l) :
		x1,y1 = self.p.x,self.p.y
		#warn((x,y,a,l))
		if x==None : 
			if y != None :
				if a!=None : 
					a = tan(a)
					if abs(a)>16331778728300000 :
						return P(x1,y)
					if a == 0 : 
						error("Bad param a=0 for y defined line. Command: %s"%self.command)
					return x1+(y-y1)/a,y
				elif l!=None :
					try :
						x = sqrt(l**2 - (y-y1)**2)	
					except :
						error("Bad params, l to small. Command: %s"%self.command)	
					return P(x,y)	
				else :
					return P(x1,y)
								
			else : 
				if a!=None and l!=None :
					return  self.p+P(cos(a),sin(a))*l 
		else : 
			if y!=None :
				return P(x,y)
			else :
				if a!=None :
					a = tan(a)
					if abs(a)>16331778728300000 :
						error("Bad param a=pi/2 for x defined line. Command: %s"%self.command)
					else: 
						return x, a*(x-x1) + y1 
						
				elif l!=None :
					try :
						y = sqrt(l**2 - (x-x1)**2)	
					except :
						error("Bad params, l to small. Command: %s"%self.command)	
				else : 
					return P(x,y1)	
					
		error("""Bad params for the line. Command: %s\n
					x = %s,
					y = %s,
					a = %s,
					l = %s
				"""%(self.command,x,y,a,l))						
		
	def draw_line(self,x,y,a,l) : 
		p1 = self.get_line_xy(x,y,a,l)
		self.path.join( CSP([[[self.p,self.p,self.p],[p1,p1,p1]]]) )
		
		
	def parse_command(self, a) :
		if a.strip() == "" : return
		r = re.match("\s*([almhvALMHV])?\s*([alxyrijALXYRIJ\d\.\-\s]*)",a) 
		self.command = a
		if not r: 
			error("Cannot parse command: \"%s\""% a)
		else : 
			t,params = r.groups()
			if t == None or t == "" :
				t = self.last_command 
			# parse the parameters 
			x,y,a,l,r,i,j = None, None, None, None, None, None, None
			for p in re.findall("([alxyrijALXYRIJ])\s*(\-?\d*\.?\d*)",params) :
				#warn(p)				
				p = list(p)
				if p[0] in ("a","A") : a = -float(p[1])/180*pi
				else :	p[1] = float(p[1])*self.options.units
				if   p[0] == "x" : x = self.p.x + p[1]
				elif p[0] == "X" : x = p[1]
				elif p[0] == "y" : y = self.p.y - p[1]
				elif p[0] == "Y" : y = - p[1]
				elif p[0] == "i" : i = self.p.x + p[1]
				elif p[0] == "I" : I = p[1]
				elif p[0] == "j" : j = self.p.y - p[1]
				elif p[0] == "J" : J = -p[1]

				# TODO add relative angles
				elif p[0] in ("l","L") : l = p[1]
				
			# exec command
			if t in ("l","L") : self.draw_line(x,y,a,l)
			if t in ("h","H") : self.draw_line(x,self.p.y,None,l)
			if t in ("v","V") : self.draw_line(self.p.x,y,None,l)
			if t in ("a","A") : self.draw_line(self.p.x,y,None,l)
			self.last_command = t

	def effect(self) :
		if self.options.silent :
			try :
				self.run()
			except :
				pass
		else :
			self.run()
			
	def run(self) :		
			s = self.options.s.split(";")
			node = None
			
			if len(self.selected) > 0 :
				node = self.selected.itervalues().next()
				if node.tag == '{http://www.w3.org/2000/svg}path' :
					self.path = CSP(node)
				else : 
					error("Select a path or select nothing to create new path!")
		
			try :
				self.p = self.path.items[-1].points[-1][1]
			except :
				self.path = CSP( [[[P(self.view_center),P(self.view_center),P(self.view_center)]]], clean=False)
				self.p = self.path.items[-1].points[-1][1]
				
			self.last_command = None
			for a in s :
				self.parse_command(a)
				try :
					self.p = self.path.items[-1].points[-1][1]
				except :
					pass

			if node == None : self.path.draw(group = self.current_layer) 
			else :	node.set("d",self.path.to_string())
		
		
bezier_console = BezierConsole()
bezier_console.affect()					

