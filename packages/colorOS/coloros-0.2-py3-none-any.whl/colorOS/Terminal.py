def size(rows, cols):
	'''
		This function helps us determine the terminal size.
		
		cols ==> x
		
		row ==> y
		
		example;
			size = colorOS.terminal.size(369, 400)
	'''
	return f'\033[8;{rows};{cols}t'
