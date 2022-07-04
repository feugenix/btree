# BTree

BTree is a B-tree (https://en.wikipedia.org/wiki/B-tree) implementation in Python

## Usage

```python
from btree import BTree, TreeKeyValue, \
    BTreeValidator, BTreePrinter, BTreeTraversal

# create tree with order 3 (maximum of 5 keys)
tree = BTree(3)

# tree can consume numeric keys (be sure to use unique) and value of any type 
tree.insert(TreeKeyValue(1, 'test_val'))
tree.insert(TreeKeyValue(2, True))
tree.insert(TreeKeyValue(3, 100500))

# tree can be validated
BTreeValidator.validate(tree)

# printed
BTreePrinter.print_tree(tree)

# or traversed
for level, node in BTreeTraversal.traverse_tree(tree):
    print(f'level: {level}, node: {node}')
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
