#!/usr/bin/python

# Encapsulation of lexer/parser pair
class PLYPair:
	def __init__(self, l=None, p=None):
		self.lexer = l
		self.parser = p
		self.result = None

	def set_lexer(self, l):
		self.lexer = l

	def set_parser(self, p):
		self.parser = p

	def parse_file(self, fname):
		f = open(fname, 'r')
		a = f.read()
		f.close()
		return self.parse(a)

	def parse(self, text):
		self.result = self.parser.parse(text, lexer=self.lexer)
		return self.result

# C-code generation
def generate_gate_h(lib):
    # Gate Types
    ## Special gates?
    ## - input
    ## - output
    ## - clock
    output = "//Elsa Gonsiorowski\n"
    output += "//Rensselaer Polytechnic Institute\n"
    output += "//Autogenerated for Library " + lib.name + "\n\n"
    output += "#ifndef _gate_h\n"
    output += "#define _gate_h\n\n"
    output += "//Gate Types/n"
    output += "#define GATE_TYPE_COUNT (" + str(len(lib.cells)) + ")\n"
    count = 0
    for cell_name in lib.cells:
        output += "#define " + cell_name + "_GATE (" + str(count) + ")\n"
        count += 1
    output += "\n#endif\n\n"
    return output

def generate_gate_func():
	output = ""
	return output

import ply_verilog_netlist
import ply_liberty
import ply_boolean_expressions
from time import time

def workflow():
	print "*** Step 1: Library File ***"
	lf = raw_input("Library File: ")
	l = PLYPair()
	l.set_lexer(ply_liberty.create_lexer())
	l.set_parser(ply_liberty.create_parser())
	l.parse_file(lf)
	l.stats()
	## set up database
	print "*** Step 2: Netlist File ***"
	vnf = raw_input("Verilog Netlist File: ")
	vn = PLYPair()
	# pass tokens from library to netlist parser
	cell_tokens = l.result.cell_tokens()
	vn.set_lexer(ply_verilog_netlist.create_lexer(cell_tokens))
	vn.set_parser(ply_verilog_netlist.create_parser())
	vn.parse_file(vnf)
	## fill database


def prompt(vars=None):
    prompt_message = "Brama Front End"
    try:
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed(argv=[''],banner=prompt_message,exit_msg="Goodbye")
        return  ipshell
    except ImportError:
        if vars is None:  vars=globals()
        import code
        import rlcompleter
        import readline
        readline.parse_and_bind("tab: complete")
        # calling this with globals ensures we can see the environment
        print prompt_message
        shell = code.InteractiveConsole(vars)
        return shell.interact

if __name__ == "__main__":

	if False:
		print "\n*** Liberty Parser"
		l = PLYPair()
		l.set_lexer(ply_liberty.create_lexer())
		l.set_parser(ply_liberty.create_parser())
		l.parse_file('Examples/example_library.lib')
		cd = l.result.cell_tokens()
		print l.result.stats

		print "\n*** Verilog Netlist Parser"
		vn = PLYPair()
		vn.set_lexer(ply_verilog_netlist.create_lexer(cd))
		vn.set_parser(ply_verilog_netlist.create_parser())
		vn.parse_file('Examples/example_netlist.v')

		print "\n*** Boolean Expression Parser"
		be = PLYPair()
		be.set_lexer(ply_boolean_expressions.create_lexer())
		be.set_parser(ply_boolean_expressions.create_parser())

		for cell_name in cd:
			cell = l.result.get_cell(cell_name)
			pd = cell.pin_tokens()
			pm = cell.pin_map()

			# this only works because of introspection at runtime
			ply_boolean_expressions.update(pd, pm)

			print cell_name
			for p in cell.boolexps():
				print "\tPin", p.name, "=", p.function, "\t--> ", p.cstr, "=", be.parse(p.function)

	# lsi_10k example
	print "Parsing Library"
	lsi_lib = PLYPair()
	lsi_lib.set_lexer(ply_liberty.create_lexer())
	lsi_lib.set_parser(ply_liberty.create_parser())
	lsi_lib.parse_file('Examples/lsi_10k.lib')
	# print lsi_lib.result['sql']
	# print lsi_lib.result['cells']
	exit()

	print "Parsing CCX"
	ccx = PLYPair()
	ccx.set_lexer(ply_verilog_netlist.create_lexer(cd))
	ccx.set_parser(ply_verilog_netlist.create_parser())
	start = time()
	ccx.parse_file('Examples/ccx_lsi_small.vSyn')
	total = time() - start
	print "Total Time:", total, "s"
	print ccx.result

	ccx.result.stats()
	ccx.result.net_stats()
	ccx.result.wire_stats(lsi_lib.result)

	p = prompt()
	p()

	# fan out
	# arangement and gid assignment
	# is one side of the assign always a wire?

	# l = lsi_lib.result
	# m = ccx.result
	# g = "digraph " + m.name + " {\n\t"
	# g += "node [shape=point]\n\t"
	# g1 = "node [color=blue]\n\t"
	# g2 = "node [color=red]\n\t"
	# for a in m.assigns:
	# 	g2 += "\"" + str(a.keys()[0]) + "\" -> \"" + str(a.values()[0]) + "\"\n\t"
	# for n in m.nets:
	# 	cell = l.get_cell(n.type)
	# 	g1 += "\"" + n.name + "\"\n\t"
	# 	for d in n.connections:
	# 		name = d.keys()[0]
	# 		wire = d.values()[0]
	# 		if name[0] == '.':
	# 			name = name[1:]
	# 		p = cell.get_pin(name)
	# 		if p.direction == 'input':
	# 			g2 += "\"" + str(wire) + "\" -> \"" + n.name + "\"\n\t"
	# 		elif p.direction == 'output':
	# 			g2 += "\"" + n.name + "\" -> \"" + str(wire) + "\"\n\t"
	# g += g1 + g2 + "}"

	# f = open('super_graph.gv', 'w')
	# f.write(g)
	# f.close()

	



