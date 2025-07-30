import inspect

def RGB(R, G, B):
	"""
		This function allows you to color the background of the text according to RGB color codes.
		
		example;
			color = colorOS.background.RGB(255, 255, 0)
			print(color + "hello")
	"""
	return f'\033[48;2;{R};{G};{B}m'
    
def black():
	"""
		This function makes the background of the text black.
	"""
	return "\033[0;40m"
    
def red():
	"""
		This function makes the background of the text red.
	"""
	return "\033[0;41m"
    
def green():
	"""
		This function makes the background of the text green.
	"""
	return "\033[0;42m"
    
def brown():
	"""
		This function makes the background of the text brown.
	"""
	return "\033[0;43m"
    
def blue():
	"""
		This function makes the background of the text blue.
	"""
	return "\033[0;44m"
   
def purple():
	"""
		This function makes the background of the text purple.
	"""
	return "\033[0;45m"
    
def cyan():
	"""
		This function makes the background of the text cyan.
	"""
	return "\033[0;46m"
    
def lightgray():
	"""
		This function makes the background of the text light gray.
	"""
	return "\033[0;47m"
    
def darkgray():
	"""
		This function makes the background of the text dark gray.
	"""
	return "\033[1;40m"
    
def lightred():
	"""
		This function makes the background of the text light red.
	"""
	return "\033[1;41m"
    
def lightgreen():
	"""
		This function makes the background of the text light green.
	"""
	return "\033[1;42m"
    
def yellow():
	"""
		This function makes the background of the text yellow.
	"""
	return "\033[1;43m"
    
def lightblue():
	"""
		This function makes the background of the text light blue.
	"""
	return "\033[1;44m"
    
def lightpurple():
	"""
		This function makes the background of the text light purple.
	"""
	return "\033[1;45m"
 
def lightcyan():
	"""
		This function makes the background of the text light cyan.
	"""
	return "\033[1;46m"
    
def white():
	"""
		This function makes the background of the text white.
	"""
	return "\033[1;47m"

def get_color():
	functs = [obj for name, obj in globals().items() if inspect.isfunction(obj) and obj.__module__ == __name__]
	
	for f in functs:
		if f.__name__ != "get_color" and f.__name__ != None:
			print(f.__name__)
