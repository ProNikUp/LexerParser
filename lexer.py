import re



Terminal = [
    ("VAR", "[a-zA-Z]+", 0),
    ("WHILE_KEYWORD", "while", 1),
    ("OP", "[+-/*]", 0),
    ("WS", "\\s+", 0),
    ("ASSIGN_OP", "=", 0),
    ("NUMBER", "0|[1-9][0-9]*", 0),
    ("LOGICAL_OP", ">|<", 0),
    ("FOR_KW", "for", 1),
    ("IF_KW", "if", 1),
    ("ELSE_KW", "else", 1),
    ("DO_KW", "do", 1),
    ("L_BR", "\\(", 0),
    ("R_BR", "\\)", 0),
    ("L_S_BR", "\\{", 0),
    ("R_S_BR", "\\}", 0),
    ("SC",";", 0),
    ("VAR_TYPE", "int|str|float", 1)
    
]

def GetLexemes (input):
    Lexemes = []

    while len(input) > 0:
        lexeme = extractNextLexeme(input)
        Lexemes.append(lexeme)
        input = input[len(lexeme[1]):]
    return Lexemes

def extractNextLexeme (input):
    buffer = input[0] 

    if len(lookupTerminals(buffer)) != 0:
        while len(lookupTerminals(buffer)) !=0 and len(buffer) != len(input):
            buffer = buffer + input[len(buffer)]
        
        
        if len(input)>1:
            buffer = buffer[:len(buffer)-1]
        terminals = lookupTerminals(buffer)
        return getPrioritizedTerminal(terminals)[0], buffer
    else:
        raise Exception("Unexpected symbol " + buffer)

def getPrioritizedTerminal(terminals):
    prioritizedTerminal = terminals[0]
   
    for terminal in terminals:
        if terminal[2] > prioritizedTerminal[2]:
            prioritizedTerminal = terminal
    
    return prioritizedTerminal

def lookupTerminals(buffer):
    terminals=[]

    for terminal in Terminal:
        if re.fullmatch(terminal[1], buffer):
            terminals.append(terminal)

    return terminals
test = "a = 2 + g l=l*2+1 if (c>0){a = a+1} else{k=k+1}"



Lexemes=GetLexemes(test)


grammer = [
    ("lang -> expr"),
    ("expr -> (assign_expr | if_expr)"),
    ("assign_expr -> VAR ASSIGN_OP value"),
    ("value_expr -> (value | L_BR value_expr R_BR) (OP value_expr)"),
    ("value -> NUMBER | VAR"),
    ("if_expr -> if_head if_body (else_head else_body)"),
    ("if_head -> IF_KW if_condition"),
    ("if_condition -> L_BR logical_expression R_BR"),
    ("logical_expression -> value_expr (LOGICAL_OP value_expr)"),
    ("if_else_body -> L_S_BR expr R_S_BR"),
    ("else_head -> ELSE_KW else_body")
]


 
out = list(filter(lambda it: it [0] != 'WS', Lexemes))

Lexemes = out
save=[]
def match(str):
    global Lexemes, save
    if Lexemes[0][0] == str:
        save.append(Lexemes[0])
        Lexem=Lexemes[0] 
        del Lexemes[0]
        
        return Lexem
    raise Exception("unexpected token " + str + " " + Lexemes[0][0])
 
def lang():
    a=[]
    while True:
        try:
            a.append(expr())
        except Exception as e:
            roll_back()
            print (e)
            break
    
    return 'lang', a

def value():
    try:
        return 'value', match('VAR')
    except:
        
        return 'value', match('NUMBER')
    

def assign_expr():
    return 'assign_expr', [match('VAR'), match('ASSIGN_OP'), value_expr()]

def roll_back():
    global Lexemes, save
    save.extend(Lexemes)
    Lexemes = save
    save = []

def value_expr():
    global save
    
    a=[]
    try:
        b=match('L_BR')
        
        a.append(b)
        try:
            a.append(value())
            
            while True:
                try:
                    
                    a.extend(OP_value()[1])
                    save = []
                except:
                    roll_back()
                    a.append(match('R_BR'))
                    return 'value_expr', a
        except:
            
            b=match('L_BR')
                
            a.append(b)
            a.append(value_expr())
                
            while True:
                try:
                    
                    a.extend(OP_value_expr()[1])
                    save = []
                except:
                    roll_back()
                    a.append(match('R_BR'))
                    return 'value_expr', a



        
    except:
       
        try:
            a.append(value())
        
            while True:
                try:
                
                    a.extend(OP_value()[1])
                    save = []
                except:
                    roll_back()
                    
                    return 'value_expr', a
        except:
            
            b=match('L_BR')
                
            a.append(b)
            a.append(value_expr())
                
            while True:
                try:
                    
                    a.extend(OP_value_expr()[1])
                    save = []
                except:
                    roll_back()
                    a.append(match('R_BR'))
                    return 'value_expr', a

    

def OP_value_expr():
    return 'OP_value', [match('OP'), value_expr()]

def OP_value():
    return 'OP_value', [match('OP'), value()]





def if_head():
    return 'if_head', [match('IF_KW'), if_condition()]

def if_condition():
    return 'if_condition', [match('L_BR'), logical_expression(), match('R_BR')]  

def logical_expression():
    return 'logical_expression', [value(), match('LOGICAL_OP'), value()] 

def if_else_body():
    a = [match('L_S_BR')]
    while True:
        try:
            a.append(expr())
        except:
            break
    
    a.append(match('R_S_BR'))
    return 'if_else_body', a

def else_head():
    return 'else_head', [match('ELSE_KW'), if_else_body()] 

def if_expr():
     return 'if_expr', [if_head(), if_else_body(), else_head()] 
     

def while_expr():
    return 'while_expr', [match('WHILE_KEYWORD'), if_condition(), if_else_body()] 


def expr():
    
    try:
        return 'expr', assign_expr()
    except:
        roll_back()
        try:
            return 'expr', if_expr()
        except:
            roll_back()
            return 'expr', while_expr()
            
def print_AST(AST, lvl):
    print('\n' + '\t' * lvl, end='')

    if isinstance(AST[1], list):
        print(AST[0])
        for j in AST[1]:
            if not isinstance(j, str):
                print_AST(j, lvl + 1)
    elif isinstance(AST[1], tuple):
        print(AST[0])
        print_AST(AST[1], lvl + 1)
    else:
        print(AST)
c=lang()
print_AST(c, 0)


   
