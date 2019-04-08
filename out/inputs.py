arr_ips = [
    'declare an integer type array called prog count',
    'declare an array called x with type float of size 10',
    'declare an integer array x of size 10 by 20',
    'declare an array of type int called x of size 10',
    'declare an integer array of size 20 called x',
    'declare an array of size 20  of type int called x',
    'declare an array  called x of size 20 type int',
]

cond_ips = [
    'a less than 10',
    'program count greater than 20',
    'a greater than 2',
    'a is greater than 5 and a is less than 10',
    'a is equal to 10',
    'a is not equal to 10',
    'a equals 10',
    'a equal to 10',
    'a not equal to 10',
    'a not greater than 5',
    'i is less than test case',
    'a smaller than b',
    'x bigger than y',
    'a greater than equal to 20',
    'b less than or equal to y',
    'a less than 20 and b greater than x or c less than d',
    'true',
    'false',
]

exp_ips = [
    '2 times 2',
    '2 times 2 plus 1',
    '2 by 2',
    '2 divided by 2',
    'x plus 10',
    'increment x',
    '10 times 5 plus 1',
    '2 minus 1',
    'minus 1 minus 2',
    'decrement y',
    'x mod 10',
    'x modulo 10',
    'x by 10',
    'x cross y',
    'x plus 2 less than 10'
]

func_ips = [
    'declare a function func1',
    'declare a function abc of type int',
    'define a function of return type int func1',
    'define a function with name fun',
    'create a function having return type int called func1',
    'define a function called func of return type double',
    'declare a function called func with return value of type int',
    'create an integer type function func1',
    # 'declare a function func1 of type int and accepts parameter x of type double',
    # 'define a function abc of return type int and parameters of type int and char',
    # 'create a function hey that returns an integer and accepts two integer arguments called a and b',
    # 'create an integer type function func having a parameter x of type int, a parameter y of type char and a z of type int',
    # 'declare a function called fun of type float that accepts integer argument x and character argument y',
    # 'create a function func having parameters x of type int, parameter y of type char and z of type int and return type int',
    # 'create a function having name func1 return type int and parameters integer type x charater type y and integer type z',
]

func_param_ips = [
    'add parameter x of type double',
    'add parameter called x of type double',
    'add parameter integer x',
    'add a parameter of type double with name x',
    'add a parameter of integer type called x',
    'add an integer type parameter called max',
    'add a parameter x of type double at position 3',
    'add parameter x in position 3 of type double',
    'add a parameter at position 2 called x of type double',
    'add a parameter of integer type called x in position 4',
    'add a parameter of integer type at position 1 called x',
    'add a parameter at position 7 of integer type called x',
    'add an integer type parameter with name max in position 4',
    'add an integer type parameter at the third position called max',
    'add a parameter at fourth position called x of type double',
    'add a parameter of integer type called x in the fifth position',
    'add a parameter in the second position of integer type called x',
]
'''
func_param_ips = [
    'which accepts parameter x of type double',
    'and accepts parameter of type double called x',
    'with an integer type parameter',
    'with parameters of type int and char',
    'which takes parameters of type int abc and char called b',
    'and takes parameters x of type int and a parameter of char type',
    'which accepts parameters of type int called a and char called b',
    'and takes 2 integer arguments called a and b',
    'that accepts integer argument x and character argument y',
    'and parameters integer type x charater type y and integer type z',
    'having a parameter x of type int, a parameter y of type char and a parameter z of type int',
]
'''

func_call_ips = [
    'invoke the function ceil with parameter x',
    'call function max with arguments x and y',
    'call function called reverse with argument x',
    'execute function called toLowerCase with parameter x',
    'call the function max and pass it arguments 2 and 3',
    # 'call function func and pass it as arguments the variables x and y', not handling(..args variable x and func y)
    'invoke function fun and pass parameters x and y',
    'execute function func and give arguments g and h',
    'return value of function f with argument x',
    'return value of function func1 with parameters x and y',
    'invoke the function called printf and pass it parameters 6 and y',
    # 'invoke function max having parameters 2 and 10 and 5',
    # 'call the function func1 and pass it arguments 2 3 and 4',
]
f_c_printf_ips = [
    # 'call printf with string Hello World',
    # 'call function printf with string type argument Hey',
    # 'invoke the function printf with parameter Hello',
    # 'call function printf with argument of string type Hello World',
    # 'call function called printf with string Hey',
    # 'execute function called printf with parameter of type string Demoing Printf',
    # 'call the function printf and pass it string argument Hello World',
    # 'invoke function printf and pass string type parameter Test',
    # 'execute function printf and give argument of type string Hi',
    # 'return value of function printf with argument Hello World',
    'call printf with parameters Hi and name',
    'call the function printf with string Total Votes and integer parameter count',
    'call printf with string Value of variable and parameter x',
    'call printf with string Greetings and parameter user',
    'invoke function printf with string Greetings and parameter person',
    'invoke function printf with parameters of type string Value of Max and parameter max',
    'call function printf with string Today is and integer parameter date',
    'invoke function printf with parameters of type string Value of Max and float result',
]

f_c_scanf_ips = [
    'call scanf with parameters mod d and address of x',
    'call scanf and pass it string mod s and parameter text',
    'invoke scanf and pass parameter mod s and parameter text',
    'call scanf with string Enter Name: mod s and parameter user',
    'call scanf and pass it string Enter Value: modulus d and parameter address of limit',
    'call scanf with parameters mod d and an integer parameter address of x',
    'invoke function scanf with string modulus s and parameter person',
    'invoke function scanf with parameters of type string Value of Max mod d and address of max',
    'call function scanf with string Today is modulus d and parameter address of date',
    'invoke scanf with parameters string Value of Max is mod f and address of result',
    'call function called scanf with parameters Today is modulus d and address of date',
]

init_ips = [
    #              ---->Wrong Output
    'initialize variable x',
    'initialize variable x equal to 4',
    'initialize x to 4',
    'initialize x to y',
    'set x equals 20',
    'set x to y',
    'make y equals 20',
    'make y equal to 20',
    'change value of x to 15',
    'update value of y to 20',
    'update the value of variable x to variable y',
]

loop_ips = [
    'create a for loop',
    'define a while loop',
    'create a while loop',
    'declare a while loop',
    'run a for loop',
    'define a do while loop',
]

loop_init_ips = [
    'add loop variable i of type char',
    'add counter i of type int',
    'add integer type initializer called i',
    'add control variable called i having type integer',
    'add variable of integer type called i',
    'add initializer of type int called i',
    # 'add integer type variable i = 0',
    # 'add loop variable i = 0',
    # 'add control variable i of type integer initialized to 0',
    # 'add integer type loop variable i set to 0',
    # 'add control variable int i = 0',
    # 'add variable i = 0 of type integer',
    # 'add loop variable i of integer type set to 0',
]

loop_cond_ips = [
    'add condition x less than 10',
    'add a condition program count greater than 20',
    'add the condition a greater than 2',
    'add conditions a is greater than 5 and a is less than 10',
    'add loop condition a is equal to 10',
    # 'add the condition a is not equal to 10',
    # 'add condition x equals 10',
    # 'add a condition a equal to 10',
    # 'add loop condition a not equal to 10',
    # 'add a loop condition x not greater than 5',
    # 'add condition i is less than test case',
    # 'add a loop condition a smaller than b',
    # 'add the condition x bigger than y',
    # 'add loop condition a greater than equal to 20',
    # 'add the loop conditions b less than or equal to y',
    # 'add conditions a less than 20 and b greater than x or c less than d',
    # 'add loop condition true',
    # 'add condition false',
]

loop_update_ips = [
    'add an update plus plus a',
    'add a loop update x plus plus',
    'add loop step y plus plus',
    'add a loop modifier x minus minus',
    'add increment a plus plus',
    'add update statement x plus plus',
    'add decrement minus minus z',
    'add modifiers ++x and --y',
    'add loop updates a++ and --b',
    # 'add update statements x++ and y--',
    'add loop modifiers x++ --y and z--',
    # 'add loop steps ++a --b and c--',
    # 'add updates x++ ++z and y--',
]
'''
loop_ips = [
    'create a for loop with loop variable i',
    'create a for loop with counter i of type int',
    'define a loop having control variable i',
    'create a for loop with counter of type int called i',
    'declare a while loop with counter i of type int',
    'run a for loop with loop counter i of type int',
    'make a while loop with condition i less 10',
    'declare a while loop that runs until i equals 0',
    'run a for loop that goes from i equal to zero to i equal to 10',
    'define a loop with initializer i going from 0 to 10 in steps of 2',
]
'''

nav_ips = [
    'goto line number 10',
    'goto line 10',
    'goto function func',
    'goto the end of line',
    'goto the start of line',
    'go to the next line',
    'go to the previous line',
    'go three positions back',
    'go back 2 places',
    'go four places front',
    'go 8 lines up',
    'go a line up',
    'go down one line',
    'goto inner loop',
    'go to the inner if statement',
]

additional_ips = [
    'exit',
    'exit block',
    'leave current block',
    'start dictation',
    'stop dictation',

]



pack_ips = [
    'include the package stdio',
    'include a library package called stdio',
    'include the library stdlib',
    'add package string',
    'include package with name stdlib',
    'add library package called stdarg',
    'add package with name MyLib',
    'include package called SupportFunc',
    'include linked list',
]

ptr_ips = [
    'declare integer pointer ptr',
    'declare pointer x of type integer',
    'declare integer pointer called x',
    'declare an integer pointer ptr',
    'declare a pointer y of type int',
    'declare a double pointer called z',
    'declare a pointer called ptr idx of type double',
    'declare a pointer called x with type float',
    'declare an integer pointer with name y',
    'declare pointer x',
    'declare a pointer of type integer x',
    'declare integer type pointer ptr',
    'declare a pointer count with type integer',
]
ptr_init_ips = [
    'point x to y',
    'point x to address of y',
    'initialize ptr to x',
    'initialize ptr to address of x',
    'set pointer x to pointer y',
    'set ptr to address of variable x',
    'initialize pointer x to pointer y',
    'set pointer x to address of array y',
]
ptr_ips_1 = [
    'declare a pointer to an integer variable called p',
    'declare a pointer p of type integer',
    'declare a pointer variable p of integer type',
    'declare a pointer p to integer',
    'declare a variable that points to integer called p',
    'declare a pointer that points to pointer to integer',  #ERROR
    'declare a variable pointing to integer',
    'declare a pointer p',
    'declare a pointer to pointer to integer',      #ERROR
    'declare pointer ptr of integer',
    'declare pointer of pointer of float called p', #ERROR
]

return_stmt_ips = [
    'return abc',
    'return the value of max',
    'return the variable min',
    'return the value of variable sum',
    'return the variable called abc',
    'return the variable with name min',
    'return the value 100',
    'return 0',
    'return x',
    'return null',
    'return the array x',
    'return the array called arr',
    'return the function max',
    'return the string hello world',
    'return the value of function max',
]

struct_ips = [
    'define a structure called employee with struct variables emp1 emp2 emp3',
    'declare a structure employee ',
    'declare a structure with structure tag employee and variables emp1 and emp2',
    'create a structure employee with variables emp1 and emp2',
]

var_ips = [
    'declare integer variable x',
    'declare variable x type integer',
    'declare integer variable called x',
    'declare an integer variable x',
    'declare a variable y of type int',
    'declare an int variable x',
    'declare a double variable called z',
    'declare a variable called prog count of type double',
    'declare a variable x with type integer',
    'declare a variable called x with type float',
    'declare a variable called prog count of type int',
    'declare an integer variable with name y',
    'declare variable x',
    'declare a variable of type integer x',
    'declare a variable of integer type called program counter',
    'declare integer type variable program counter',
    'declare an integer x',
    'declare a variable count with type of integer',
    'declare a long integer program count'
]
#           -----> WITH PARAMETERS
'''

if_ips = [
    'declare an if statement',
    'declare a conditional statement',
    'declare if',
    'declare if else',
    'declare if else statement',

    # adding conditions and else if
    'add else if block',
    'add else if',
    'add condition x greater than 2',
    'add condition x less than y and z greater than x',
    'add a condition x less than 10',
    'add else'
]
'''