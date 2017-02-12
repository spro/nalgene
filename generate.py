import re
import random
import sys

def parseSections(filename):
    sections = open(filename).read().strip().split('\n\n')
    sections = [section.split('\n') for section in sections]
    all_sections = []
    if sections[0][0].startswith('@'):
        import_filenames = [line.split(' ')[1] for line in sections[0]]
        for import_filename in import_filenames:
            all_sections += parseSections(import_filename)
    all_sections += [parseSection(section) for section in sections]
    return all_sections

def parseSection(section):
    key = section.pop(0)
    options = {'passthrough': False}
    if key.endswith('='):
        options['passthrough'] = True
        key = re.sub(r'=$', '', key)
    lines = [re.sub(r'^    ', '', line) for line in section]
    lines = [line.split(' ') for line in lines if not line.startswith('#')]
    return (key, {'lines': lines, 'options': options})

def generate(generate_token='%entry', indent=0):
    ind = ' ' * indent * 4
    section = sections[generate_token]
    tokens = random.choice(section['lines'])
    output = ''
    output_ = []
    for token in tokens:
        if token.startswith(('%', '$', '~')):
            token_output, token_output_ = generate(token, indent+1)
            output += token_output + ' '
            if sections[token]['options']['passthrough']:
                output_ += token_output_
            elif token.startswith('%'):
                output_ += [[token] + token_output_]
            elif token.startswith('$'):
                output_ += [[token, token_output]]
        else:
            output += token + ' '

    output = output.strip()
    if generate_token == '%entry':
        output_ = output_[0]

    return output, output_

def w(s): sys.stdout.write(s)

def lprint(a, n_indent=0):
    indent = ' ' * n_indent * 4
    w(indent + '(')
    for i in a:
        if isinstance(i, list):
            w('\n')
            lprint(i, n_indent + 1)
        else:
            w(' ' + i)
    w(' )')

sections = dict(parseSections('test.nlg'))
generated_output, generated_output_ = generate()
print('>', generated_output, '\n')
lprint(generated_output_)
w('\n')
