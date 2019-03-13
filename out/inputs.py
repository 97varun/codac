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
    'declare an integer variable with name y',
    'declare variable x',
    'declare a variable of type integer x',
    'declare a variable of integer type called program counter',
    'declare integer type variable program counter',
    'declare an integer x',
    'declare a variable count with type of integer'
]

init_ips = [
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
    'declare a function of return type int func1',
    'declare a function having return type int called func1',
    'declare a function called func of return type double',
    'declare a function called func with return value of type int',
    'declare a function func1 of type int',
    'declare an integer type function func1',
]

pack_ips = [
    'include the package stdio',
    'include a library package called stdio',
    'include the library stdlib',
    'add package stdlib',
    'include package with name stdlib',
]

loop_ips = [
    'create a for loop',
    'define a while loop',
    'create a while loop',
    'declare a while loop that runs until i equals 0',
    'run a for loop',
    'define a do while loop that runs until i equals 0',
]
'''           -----> WITH PARAMETERS
loop_ips = [
    'create a for loop',
    'define a loop with initializer i going from 0 to 10 in steps of 2',
    'make a while loop with condition i less 10',
    'declare a while loop that runs until i equals 0',
    'run a for loop that goes from i equal to zero to i equal to 10',
]
'''



struct_ips = [
    'define a structure called employee with struct variables emp1 emp2 emp3',
    'declare a structure employee',
    'declare a structure with strcture tag employee and variables emp1 and emp2',
    'create a structure employee with variables emp1 and emp2',
]