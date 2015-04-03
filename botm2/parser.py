import os
import re
import xml.etree.ElementTree as ET




class Parser:
    ws = re.compile(r'\s+')
    empty = re.compile(r'^$|[^a-zA-Zа-яА-Я]')

    def __init__(self, filename):
        self.filename = filename
        self.text = str()

    def remove_ws(self):
        self.text = self.ws.sub(' ', self.text)

    def get_text(self):
        with open(self.filename, 'r') as f:
            for line in f:
                self.text += line.rstrip() + ' '
        self.remove_ws()


    def parse(self):
        self.get_text()
        return self.text


    @classmethod
    def get_parser(cls, filename):
        parser_cls = cls
        ext = os.path.splitext(filename)[1]
        for subclass in cls.__subclasses__():
            if ext in subclass.extensions:
                parser_cls = subclass
        return parser_cls(filename)

class SrtParser(Parser):
    extensions = ('.srt')

    def get_text(self):
        with open(self.filename, 'r') as f:
            for line in f:
                line = line.rstrip()
                if not self.empty.match(line):
                    self.text += line + ' '
        self.text = re.sub(r'[^A-Za-zА-Яа-я0-9\!\?\.\,\s\']', '', self.text)


class Fb2Parser(Parser):
    extensions = ('.fb2')

    def get_text(self):
        tree = ET.parse(self.filename)
        root = tree.getroot()
        for child in root.iter():
            if child.tag == '{http://www.gribuser.ru/xml/fictionbook/2.0}p':
                if child.text and not self.empty.match(child.text):
                    self.text += child.text.rstrip() + ' '
        self.text = re.sub(r'[^A-Za-zА-Яа-я0-9\!\?\.\,\s\']', '', self.text)


def main():
    parser = Parser.get_parser('Zhelyazny.fb2')
    parser.parse()
    # try:
    #     save_text(parser.filename, *parser.parse())
    # except Exception as e:
    #     print(e)
    # print(get_texts())
    # print(Parser.get_parser('test.txt'))
    # print(Parser.get_parser('test.'))
    # print(Parser.get_parser('test'))
    # print(Parser.get_parser('test.fb2'))
    # print(Parser.get_parser('test.srt'))

if __name__ == '__main__':
    main()
