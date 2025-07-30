'''
	This function helps in editing the format of the text.
'''
def hide():
	'''
		This function helps in making the text invisible.
	'''
	return "\033[8m"
    
def show():
	'''
		This function helps in making the text visible.
	'''
	return "\033[28m"
    
def bold():
	'''
		This function helps in making the text bold.
	'''
	return "\033[1m"
    
def faint():
	'''
		This function helps in making the text faint.
	'''
	return "\033[2m"
    
def italic():
	'''
		This function helps in making the text italic.
	'''
	return "\033[3m"
    
def underline():
	'''
		This function helps in making the text underline.
	'''
	return "\033[4m"
    
def blink():
	'''
		This function helps in making the text blink.
	'''
	return "\033[5m"
    
def negative():
	'''
		This function helps in making the text negative.
	'''
	return "\033[7m"
    
def crossed():
	'''
		This function helps in making the text crossed.
	'''
	return "\033[9m"
    
def normal():
	'''
		This function helps in making the text normal.
	'''
	return "\033[22m"
    
def closeitalic():
	'''
		This function helps in making the text close italic.
	'''
	return "\033[23m"
    
def closeunderline():
	'''
		This function helps in making the text close underline.
	'''
	return "\033[24m"
    
def closenegative():
	'''
		This function helps in making the text close negative.
	'''
	return "\033[27m"
    
def lettersunderline():
	'''
		This function helps to make the next letter of the text also underline.
	'''
	return '\033[4:1m'

def letterstopline():
	'''
		This function helps to make the next letter of the text also cross out.
	'''
	return '\033[9:1m'
    
def lettersbold():
	'''
		This function helps to make the next letter of the text also bold.
	'''
	return '\033[22m'
