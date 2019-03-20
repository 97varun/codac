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
    'update the value of variable x to variable y'
]

arr_ips = [
    'declare an integer type array called prog count',
    'declare an array called x with type float of size 10',
    'declare an integer array x of size 10 by 20',
    'declare an array of type int called x of size 10',
    'declare an integer array of size 20 called x',
    'declare an array of size 20  of type int called x',
    'declare an array  called x of size 20 type int',
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

ptr_ips = [
    'declare a pointer to an integer variable called p',
    'declare a pointer p of type integer',
    'declare a pointer variable p of integer type',
    'declare a pointer p to integer',
    'declare a variable that points to integer called p',
    'declare a pointer that points to pointer to integer',
    'declare a variable pointing to integer',
    'declare a pointer p',
    'declare a pointer to pointer to integer',
    'declare pointer of integer',
    'declare pointer of pointer of float called p',
]

struct_ips = [
    'define a structure called employee with struct variables emp1 emp2 emp3',
    'declare a structure employee ',
    'declare a structure with structure tag employee and variables emp1 and emp2',
    'create a structure employee with variables emp1 and emp2',
]

loop_ips = [
    'create a for loop with loop variable i',
    'create a for loop with counter i of type int',
    'define a loop having control variable i',
    'create a for loop with counter of type int called i',
    'declare a while loop with counter i of type int',
    'run a for loop with loop counter i of type int',
]

'''
loop_ips = [
    'create a for loop',
    'define a while loop',
    'create a while loop',
    'declare a while loop',
    'run a for loop',
    'define a do while loop',
]
loop_ips = [
    'with loop variable i',
    'with counter i of type int',
    'having control variable i',
    'with counter of type int called i',
    'with counter i of type int',
    'with loop counter i of type int',
]
loop_ips = [
    'create a for loop with loop variable i',
    'create a for loop with counter i of type int',
    'define a loop with initializer i going from 0 to 10 in steps of 2',
    'make a while loop with condition i less 10',
    'declare a while loop that runs until i equals 0',
    'run a for loop that goes from i equal to zero to i equal to 10',
]
#           -----> WITH PARAMETERS
'''
