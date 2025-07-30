import inspect

def RGB(R, G, B):
	"""
		This function allows you to color text according to RGB color codes.

		example;
			color = colorOS.color.RGB(255, 255, 0)
			print(color + "hi")
	"""
	return f'\033[38;2;{R};{G};{B}m'
    
def black():
	"""
		This function makes the text black.
	"""
	return "\033[0;30m"
    
def red():
	"""
		This function makes the text red.
	"""
	return "\033[0;31m"
    
def green():
	"""
		This function makes the text green.
	"""
	return "\033[0;32m"
    
def brown():
	"""
		This function makes the text brown.
	"""
	return "\033[0;33m"
    
def blue():
	"""
		This function makes the text blue.
	"""
	return "\033[0;34m"
    
def purple():
	"""
		This function makes the text purple.
	"""
	return "\033[0;35m"
    
def cyan():
	"""
		This function makes the text cyan.
	"""
	return "\033[0;36m"
    
def lightgray():
	"""
		This function makes the text light gray.
	"""
	return "\033[0;37m"
    
def darkgray():
	"""
		This function makes the text dark gray.
	"""
	return "\033[1;30m"
    
def lightred():
	"""
		This function makes the text light red.
	"""
	return "\033[1;31m"
    
def lightgreen():
	"""
		This function makes the text light green.
	"""
	return "\033[1;32m"
    
def yellow():
	"""
		This function makes the text yellow.
	"""
	return "\033[1;33m"
    
def lightblue():
	"""
		This function makes the text light blue.
	"""
	return "\033[1;34m"
    
def lightpurple():
	"""
		This function makes the text light purple.
	"""
	return "\033[1;35m"
    
def lightcyan():
	"""
		This function makes the text light cyan.
	"""
	return "\033[1;36m"
    
def white():
	"""
		This function makes the text white.
	"""
	return "\033[1;37m"
	
def get_color():
	functs = [obj for name, obj in globals().items() if inspect.isfunction(obj) and obj.__module__ == __name__]
	
	for f in functs:
		if f.__name__ != "get_color" and f.__name__ != None:
			print(f.__name__)
