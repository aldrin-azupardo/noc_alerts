#Reading Files into a List
#Each line of file w/o '\n' will be an element of the list
with open('configuration.txt') as file:
    my_list = file.read().splitlines()
    print(my_list)

with open('configuration.txt','r') as file:
    my_list = file.readlines()
    print(my_list)

#reads the configuration.txt by line and iterates
with open('configuration.txt','r') as file:
    print(file.readlines())
    print(file.readlines())

#prints each line without \n
with open('configuration.txt', 'r') as file:
    for line in file:
        print(line, end='')
