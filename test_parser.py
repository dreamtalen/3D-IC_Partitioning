from parser import parse

def main():

    filelist = ['idct_module.v']

    ast, directives = parse(filelist)
    ast.show(showlineno=False)
        
if __name__ == '__main__':
    main()
