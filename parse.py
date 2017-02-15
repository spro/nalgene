import re
import math
import random

print('-' * 80)
file = open('nests.nlg').read()
SHIFT_WIDTH = 4

start_space = r'^(    )*'

types = {
    '%': 'phrase',
    '#': 'hash',
    '~': 'synonym',
    '$': 'value',
    '@': 'function'
}

class Node:
    def __init__(self, key, type='*'):
        self.key = key
        self.children = []
        self.children_by_key = {}
        self.is_leaf = True
        self.type = type

    @property
    def value(self):
        return self.children[0].key

    def __str__(self):
        return self.str(0)

    def __getitem__(self, key):
        return self.children_by_key[key]

    def __contains__(self, key):
        return self.children_by_key.__contains__(key[0])

    def str(self, indent=0):
        s = ""
        s += (' ' * indent * 4) + self.type + ' ' + str(self.key)
        for child in self.children:
            s += "\n" + child.str(indent + 1)
        return s

    def add(self, child):
        if not isinstance(child, Node):
            child = Node(child)
        self.children.append(child)
        self.children_by_key[child.key] = child
        self.is_leaf = False
        return child

    def merge(self, child):
        if not isinstance(child, Node):
            child = Node(child)
        for child_child in child.children:
            self.children.append(child_child)
            self.children_by_key[child_child.key] = child_child
            self.is_leaf = False
        return self

    def descend(self, i_s):
        child = self.children[i_s[0]]
        if len(i_s) == 1:
            return child
        else:
            return child.descend(i_s[1:])

    def add_at(self, child, i_s):
        if len(i_s) == 1:
            self.add(child)
        else:
            self.children[i_s[0]].add_at(child, i_s[1:])

    @property
    def is_array(self):
        if len(self.children) == 0:
            return False
        for child in self.children:
            if not child.is_leaf:
                return False
        return True

    def __iter__(self):
        self.iter_c = 0
        return self

    def __next__(self):
        if self.iter_c >= len(self.children):
            raise StopIteration
        else:
            child = self.children[self.iter_c]
            self.iter_c += 1
            return child

    def mapLeaves(self, f):
        for child in self.children:
            if child.is_leaf:
                f(child)
            else:
                child.mapLeaves(f)

def count_indent(s):
    indent = len(re.match(start_space, s).group(0))
    return math.floor(indent / SHIFT_WIDTH)

def parse_section(section):
    lines = section.split('\n')
    lines = [line for line in lines if not re.match(r'^\s*#', line)]
    parsed = Node('')
    i_s = [-1]
    level = 0
    last_ind = 0
    for li in range(len(lines)):
        line = lines[li]
        ind = count_indent(line)
        line = re.sub(start_space, '', line).strip()
        if len(line) == 0: continue

        if ind == last_ind: # Next item in a list
            i_s[level] += 1
        elif ind > last_ind: # Child item
            level += 1
            i_s.append(0)
        elif ind < last_ind: # Up to next item in parent list
            diff = (last_ind - ind)
            for i in range(last_ind - ind):
                level -= 1
                i_s.pop()
            i_s[level] += 1

        parsed.add_at(line, i_s)
        last_ind = ind
    return parsed

parsed = parse_section(file)

# Iterate over generic parsed tree to create specific node types
for p in parsed:
    p.type = types[p.key[0]]
    if p.key.endswith('='):
        p.passthrough = True
        p.key = p.key[:-1]

def tokenizeLeaf(n):
    n.type = 'sequence'
    n.sequence = n.key.split(' ')

parsed.mapLeaves(tokenizeLeaf)

def generate(from_node, context={}):
    print('[generate]', from_node)
    sentence = ""
    tree = Node(from_node.key)
    sequence = random.choice(from_node.children)

    for token in sequence.sequence:
        print('[generate] %s' % from_node.key, token)

        # Optional
        if token.endswith('?'):
            if random.random() < 0.5:
                continue
            else:
                token = token[:-1]

        # Hash
        if token.startswith('#'):
            hash_name = token.split('[')[0]
            hash_ref = token.split('[')[1].split(']')[0]

            # Get the object referenced
            token_parts = hash_ref.split('.')
            token = token_parts[0]
            sub_token = token_parts[1]
            obj = context[token]
            hash_key = obj[sub_token].value

            # Get the hash and value from it
            hash = parsed[hash_name]
            tree.add(hash[hash_key].value)

        # Value
        elif token.startswith(('$', '%')):
            token_parts = token.split('.')

            # Object value
            if len(token_parts) == 2:
                super_token = token_parts[0]
                sub_token = token_parts[1]

                # Check if super-object exists
                if super_token in context:
                    obj = context[super_token]

                # Or choose one
                else:
                    type = parsed[super_token]
                    obj = random.choice(type.children)
                    context[super_token] = obj

                sentence += obj[sub_token].value
                tree.add(obj[sub_token].value)

            # Regular value
            else:
                sub_sentence, sub_tree = generate(parsed[token], context)
                sentence += sub_sentence
                tree.add(sub_tree)

        # Syonym
        elif token.startswith('~'):
            sub_sentence, sub_tree = generate(parsed[token], context)
            sentence += sub_sentence
            tree.merge(sub_tree)

        # Other
        else:
            sentence += token + ' '
            if from_node.type == 'value':
                tree.add(token)

    return sentence, tree

sentence, tree = generate(parsed['%'])
print('>', sentence)
print(tree)

def extract(generated):
    sentence = ""
    tree = Node(generated.key)
    for node in generated:
        # Add words to sentence
        if node.is_leaf:
            sentence += node.key + ' '
            # Keep variable values
            if generated.key[0] == '$':
                tree.add(node.key)
        # Add other nodes to tree
        else:
            sub_sentence, sub_tree = extract(node)
            sentence += sub_sentence
            tree.add(sub_tree)
    return sentence, tree


