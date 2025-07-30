'''
	This function helps us scroll the texts.
'''
def right(n):
	'''
		This function helps us scroll text from the right.
	'''
	return f'\033[{n}C'

def left(n):
	'''
		This function helps us scroll text from the left.
	'''
	return f'\033[{n}D'
    
def top(n):
	'''
		This function helps us scroll text from the top.
	'''
	return f'\033[{n}D'
    
def bottom(n):
	'''
		This function helps us scroll text from the bottom.
	'''
	return f'\033[nD'
    
def textslide(n):
	'''
		This function helps us move the cursor down.
	'''
	return f'\033[{n}S'
    
def textdelete(n):
	'''
		this function helps us delete the text
	'''
	return f'\033[{n}K'
