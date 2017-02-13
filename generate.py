import re
import random
import sys
import os

def parseSections(filename, base_dir='.'):
    sections = open(os.path.join(base_dir, filename)).read().strip().split('\n\n')
    sections = [section.split('\n') for section in sections]
    all_sections = []
    if sections[0][0].startswith('@'):
        import_filenames = [line.split(' ')[1] for line in sections[0]]
        for import_filename in import_filenames:
            all_sections += parseSections(import_filename, base_dir)
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

def generate(generate_token='%', indent=0):
    ind = ' ' * indent * 4
    section = sections[generate_token]
    tokens = random.choice(section['lines'])
    output = ''
    output_ = []

    for token in tokens:
        if token.endswith('?'):
            token = re.sub(r'\?$', '', token)
            if random.random() < 0.5:
                continue
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
    if generate_token == '%':
        output_ = ['%'] + output_

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

if len(sys.argv) < 2:
    print("Usage: python generate.py [grammar].nlg")
    sys.exit()
filename = os.path.basename(sys.argv[1])
base_dir = os.path.dirname(sys.argv[1])
sections = dict(parseSections(filename, base_dir))
generated_output, generated_output_ = generate()
print('>', generated_output)
lprint(generated_output_)
print()
