from nalgene.parse import *
import os
import json

# Generate tokens up to $variable level

def walk_tree(root, current, context, start_w=0):
    print('\n[%d walk_tree]' % start_w, '"' + current.key + '"', 'context', context)

    seq = random.choice(current)

    flat = Node('>')
    tree = Node(current.key)
    for child in seq:
        child_key = child.key

        # Optionally skip optional tokens
        if child_key.endswith('?'):
            child_key = child_key[:-1]
            if random.random() < 0.5:
                continue

        # Expandable word, e.g. %phrase or ~synonym
        if child_key.startswith(('%', '~', '$')):

            # Existing variable, pass in context
            try:
                sub_context = context[child_key]

            except Exception:
                print('[ERROR] Key', child_key, 'not in', context)
                sub_context = None

            sub_flat, sub_tree = walk_tree(root, root[child_key], sub_context, start_w)

            # Add words to flat tree
            flat.merge(sub_flat)

            # Adjust position based on number of tokens
            len_w = len(sub_flat)
            sub_tree.position = (start_w, start_w + len_w - 1, len_w)
            start_w += len_w

            # Add to (or merge with) tree
            if not child_key.startswith('~'):
                if root[child_key].passthrough:
                    tree.merge(sub_tree)
                else:
                    tree.add(sub_tree)

        # Terminal node, e.g. a word
        else:
            start_w += 1
            len_w = 1
            has_parent, parent_line = current.has_parent('variable')
            if current.type == 'word' and has_parent:
                tree.type = 'variable'
                tree.key = '.'.join(parent_line)
                print('[terminal]', tree.key)
            flat.add(child_key)

    return flat, tree

def fix_sentence(sentence):
    return fix_punctuation(fix_newlines(fix_spacing(sentence)))

def fix_punctuation(sentence):
    return re.sub(r'\s([,.!])', '\\1', sentence)

def fix_newlines(sentence):
    return re.sub(r'\s*\\n\s*', '\n\n', sentence)

def fix_spacing(sentence):
    return re.sub(r'\s+', ' ', sentence)

def generate_from_file(base_dir, filename, root_context):
    parsed = parse_file(base_dir, filename)
    parsed.map_leaves(tokenizeLeaf)
    walked_flat, walked_tree = walk_tree(parsed, parsed['%'], root_context['%'])
    print(walked_flat)
    print('=', fix_sentence(walked_flat.raw_str))
    print('=', walked_tree)
    print('')
    return walked_flat, walked_tree

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate.py [grammar].nlg")
        sys.exit()

    filename = os.path.realpath(sys.argv[1])
    base_dir = os.path.dirname(filename)
    filename = os.path.basename(filename)

    test_json = json.load(open('test2.json'))
    root_context = Node('%').add(parse_dict(test_json))

    generate_from_file(base_dir, filename, root_context)

else:
    filename = sys.argv[1]
    base_dir = os.path.dirname(os.path.realpath(__file__))
    combined = os.path.join(base_dir, filename)
    base_dir = os.path.dirname(combined)
    filename = os.path.basename(combined)

    def generate(): return generate_from_file(base_dir, filename, Node('%'))
