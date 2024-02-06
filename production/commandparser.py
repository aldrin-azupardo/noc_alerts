import textfsm
import re

class CommandParser(object):
    def __init__(self, pattern, output):
        self.pattern = pattern
        self.output = output

    def parse_text(self):
        template = open(self.pattern)
        results_template = textfsm.TextFSM(template)
        parsed_results = results_template.ParseText(self.output)
        return parsed_results

    def regex_parse(self):
        reg_pattern = re.compile(self.pattern)
        parsed_result = re.findall(reg_pattern, self.output)
        parsed_result = parsed_result[0].split()
        return parsed_result

    def get_interface(self):
        result = self.regex_parse()
        return result[2].strip('()')

    def get_status(self):
        result = self.regex_parse()
        return result[4].strip(':')
    
    def get_txload(self):
        result = self.regex_parse()
        return result[3].strip(',')
    
    def get_rxload(self):
        result = self.regex_parse()
        return result[5]
    
    def get_first_index(self):
        result = self.parse_text()
        return result[0]
