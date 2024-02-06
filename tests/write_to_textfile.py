with open('myfile.txt', 'w') as f:
    f.write('Just a line\n')
    f.write('2nd line')

#Appends new line of text to the file
with open('myfile.txt', 'a') as f:
    f.write('Just a line\n')
    f.write('2nd line')

#read and write on a textfile 'r+'
with open('configuration.txt', 'r+') as f:
    f.write('Line added with r+\n')