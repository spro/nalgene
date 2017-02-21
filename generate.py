from nalgene.parse import *
import os
import json

# Generate tokens up to $value level

def walk_tree(root, current, context, start_w=0):
    # print('[walk_tree]', '"' + current.key + '"')

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

            # Existing value, pass in context
            if (context != None) and (child_key in context):
                sub_context = context[child_key]

            else:
                sub_context = None

            sub_flat, sub_tree = walk_tree(root, root[child_key], sub_context, start_w)

            flat.merge(sub_flat)

            # Adjust position based on number of tokens
            len_w = len(sub_flat)
            sub_tree.position = (start_w, start_w + len_w - 1, len_w)
            start_w += len_w

            if not child_key.startswith('~'):
                if root[child_key].passthrough:
                    tree.merge(sub_tree)
                else:
                    tree.add(sub_tree)

        # Terminal node, e.g. a word
        else:
            start_w += 1
            len_w = 1
            flat.add(child_key)

    return flat, tree

def generate_from_file(base_dir, filename):
    root_context = Node('')
    parsed = parse_file(base_dir, filename)
    parsed.map_leaves(tokenizeLeaf)
    walked_flat, walked_tree = walk_tree(parsed, parsed['%'], root_context['%'])
    print(walked_flat)
    print('>', walked_flat.raw_str)
    print('= tree', walked_tree)
    print('')
    return walked_flat, walked_tree

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate.py [grammar].nlg")
        sys.exit()

    filename = os.path.realpath(sys.argv[1])
    base_dir = os.path.dirname(filename)
    filename = os.path.basename(filename)

# test_json = json.load(open(base_dir + '/test2.json'))
# root_context = Node('').add(parse_dict(test_json))
    root_context = Node('')

    generate_from_file(base_dir, filename)

else:
    filename = sys.argv[1]
    base_dir = os.path.dirname(os.path.realpath(__file__))
    combined = os.path.join(base_dir, filename)
    base_dir = os.path.dirname(combined)
    filename = os.path.basename(combined)

    def generate(): return generate_from_file(base_dir, filename)
