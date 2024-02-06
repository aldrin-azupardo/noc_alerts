import textfsm
# from prettytable import prettytable
from tabulate import tabulate

# template = open('show_env_all.textfsm')
# results_template = textfsm.TextFSM(template)
# content2parse = open('env.txt')
# content = content2parse.read()
# parsed_results = results_template.ParseText(content)
# # print(results_template.header)
# print(parsed_results)
# content2parse.close()

# test this once 'pip install tabulate' is available
template = open('show_env_all.textfsm')
results_template = textfsm.TextFSM(template)
content2parse = open('show_env_all.txt')
header = results_template.header
parsed_results = results_template.ParseText(content2parse.read())
print(parsed_results)
# print(tabulate(parsed_results, headers=header))
content2parse.close()