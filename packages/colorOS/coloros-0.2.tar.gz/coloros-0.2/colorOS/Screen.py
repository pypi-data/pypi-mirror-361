'''
	This function helps you organize the terminal screen.
'''
def clear():
	'''
		This function helps us clear the terminal screen.
	'''
	return "\033[2J"
    
def rstart():
	'''
		This function also helps us return to the beginning of the terminal screen.
	'''
	return "\033[H"
    
def rbase():
	'''
		This function also helps us return to the end on the terminal screen.
	'''
	return "\033[1H"
