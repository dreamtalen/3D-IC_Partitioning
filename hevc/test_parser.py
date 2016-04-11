import sys
from parser import parse

def main():
	if sys.argv[1]:
		filelist = [sys.argv[1]]
	print sys.argv
	ast, directives = parse(filelist)
	ast.show(showlineno=False)
        
if __name__ == '__main__':
	main()
