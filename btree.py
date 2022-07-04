import enum
from typing import Tuple, List, Any, Generator

TreeKey = int


class MergeDirection(enum.Enum):
    PREV = 1,
    NEXT = 2,


class TreeKeyValue:
    __slots__ = ['key', 'value']

    def __init__(self, key: TreeKey, value: Any):
        self.key = key
        self.value = value

    def __repr__(self):
        return f'<{self.key}>'


class BTreeNode:
    def __init__(self, leaf: bool = False) -> None:
        self.leaf = leaf
        self.keys = []  # type: List[TreeKeyValue]
        self.children = []  # type: List[BTreeNode]

    def __repr__(self):
        return f'<BTreeNode keys={self.keys}, children number: {len(self.children)}, leaf: {self.leaf}>'

    @property
    def keys_number(self) -> int:
        return len(self.keys)

    def append_new_key_value(self, new_value: TreeKeyValue) -> None:
        # Firstly add new value to the end of keys
        self.keys.append(new_value)
        # Then push new value to the right index in keys list
        for i in reversed(range(len(self.keys) - 1)):
            if self.keys[i].key > self.keys[i + 1].key:
                self.keys[i], self.keys[i + 1] = self.keys[i + 1], self.keys[i]

    def get_key_range_index(self, searching_key: TreeKey) -> int:
        i = 0
        keys = self.keys

        while i < len(keys) and searching_key > keys[i].key:
            i += 1

        return i

    def remove_key_by_index(self, removing_key: TreeKey, index: int) -> None:
        if index < self.keys_number and self.keys[index].key == removing_key:
            self.keys.pop(index)


class BTree:
    __slots__ = ['root', 'min_degree', 'max_keys_number']

    def __init__(self, min_degree: int) -> None:
        self.root = BTreeNode(True)  # when tree is just created root is an only node, and it's a leaf
        self.min_degree = min_degree
        self.max_keys_number = 2 * self.min_degree - 1

    def insert(self, new_value: TreeKeyValue) -> None:
        if self.search_and_insert_into_non_full_node(self.root, new_value):
            return

        # If we can't find node to insert value than we need to split root and start looking again
        self._split_root()
        self.search_and_insert_into_non_full_node(self.root, new_value)

    def _split_root(self) -> None:
        old_root = self.root
        # new root node can't be leaf node by definition
        new_root = BTreeNode()
        self.root = new_root
        new_root.children.append(old_root)
        self._split_child(new_root, 0)

    def _try_insert_into_leaf_node(self, node: BTreeNode, new_value: TreeKeyValue) -> bool:
        # check if we can insert new value at all
        if node.keys_number >= self.max_keys_number:
            return False

        node.append_new_key_value(new_value)
        return True

    def search_and_insert_into_non_full_node(self, node: BTreeNode, new_value: TreeKeyValue) -> bool:
        if node.leaf:
            return self._try_insert_into_leaf_node(node, new_value)

        key_index = node.get_key_range_index(new_value.key)

        if not self.search_and_insert_into_non_full_node(node.children[key_index], new_value):
            if node.keys_number >= self.max_keys_number:
                return False

            if node.children[key_index].keys_number >= self.max_keys_number:
                self._split_child(node, key_index)
                if new_value.key > node.keys[key_index].key:
                    key_index += 1

            return self.search_and_insert_into_non_full_node(node.children[key_index], new_value)

        return True

    # Split selected child node
    def _split_child(self, parent_node: BTreeNode, child_index: int) -> None:
        min_degree = self.min_degree

        existing_child_node = parent_node.children[child_index]
        new_child_node = BTreeNode(existing_child_node.leaf)

        parent_node.children.insert(child_index + 1, new_child_node)
        # take key in a middle (for a full node min_degree - 1 is equivalent for len(node.keys) / 2)
        parent_node.keys.insert(child_index, existing_child_node.keys[min_degree - 1])
        # splitting all keys among new and existing child nodes except one key (middle one)
        new_child_node.keys = existing_child_node.keys[min_degree:]
        existing_child_node.keys = existing_child_node.keys[:min_degree - 1]

        if not existing_child_node.leaf:
            # however we split all children (even one in the middle)
            new_child_node.children = existing_child_node.children[min_degree:]
            existing_child_node.children = existing_child_node.children[:min_degree]

    def delete(self, removing_key: TreeKey) -> None:
        self._delete_from_subtree(self.root, removing_key)

    # Delete a node
    def _delete_from_subtree(self, node: BTreeNode, removing_key: TreeKey) -> None:
        min_degree = self.min_degree

        if removing_key == 6:
            print(f'node = {node}')
        key_index = node.get_key_range_index(removing_key)
        if removing_key == 6:
            print(f'key_index = {key_index}')

        if node.leaf:
            node.remove_key_by_index(removing_key, key_index)
            return

        if key_index < node.keys_number and node.keys[key_index].key == removing_key:
            self.delete_internal_node(node, removing_key, key_index)
            return

        if node.children[key_index].keys_number >= min_degree:
            self._delete_from_subtree(node.children[key_index], removing_key)
            return

        # TODO: refactor
        if key_index != 0 and key_index + 2 < len(node.children):
            if node.children[key_index - 1].keys_number >= min_degree:
                self.delete_sibling(node, key_index, MergeDirection.PREV)
            elif node.children[key_index + 1].keys_number >= min_degree:
                self.delete_sibling(node, key_index, MergeDirection.NEXT)
            else:
                self.delete_merge(node, key_index, MergeDirection.NEXT)
        elif key_index == 0:
            if node.children[key_index + 1].keys_number >= min_degree:
                self.delete_sibling(node, key_index, MergeDirection.NEXT)
            else:
                self.delete_merge(node, key_index, MergeDirection.NEXT)
        elif key_index + 1 == len(node.children):
            if node.children[key_index - 1].keys_number >= min_degree:
                self.delete_sibling(node, key_index, MergeDirection.PREV)
            else:
                self.delete_merge(node, key_index, MergeDirection.PREV)

        if key_index < len(node.children):
            self._delete_from_subtree(node.children[key_index], removing_key)

    # Delete internal node
    def delete_internal_node(self, node: BTreeNode, removing_key: TreeKey, key_index: int) -> None:
        min_degree = self.min_degree

        if node.leaf:
            node.remove_key_by_index(removing_key, key_index)
            return

        if node.children[key_index].keys_number >= min_degree:
            node.keys[key_index] = self.delete_predecessor(node.children[key_index])
            return

        if node.children[key_index + 1].keys_number >= min_degree:
            node.keys[key_index] = self.delete_successor(node.children[key_index + 1])
            return

        self.delete_merge(node, key_index, MergeDirection.NEXT)
        self.delete_internal_node(node.children[key_index], removing_key, self.min_degree - 1)

    # Delete the predecessor
    def delete_predecessor(self, node: BTreeNode) -> TreeKeyValue:
        if node.leaf:
            return node.keys.pop()

        n = node.keys_number - 1
        if node.children[n].keys_number >= self.min_degree:
            self.delete_sibling(node, n + 1, MergeDirection.PREV)
        else:
            self.delete_merge(node, n, MergeDirection.NEXT)

        return self.delete_predecessor(node.children[n])

    # Delete the successor
    def delete_successor(self, node: BTreeNode) -> TreeKeyValue:
        if node.leaf:
            return node.keys.pop(0)

        if node.children[1].keys_number >= self.min_degree:
            self.delete_sibling(node, 0, MergeDirection.NEXT)
        else:
            self.delete_merge(node, 0, MergeDirection.NEXT)

        return self.delete_successor(node.children[0])

    @staticmethod
    def _delete_next_child_node(parent_node: BTreeNode, child_index: int, next_child_index: int):
        child_to_merge = parent_node.children[child_index]
        child_to_remove = parent_node.children[next_child_index]

        child_to_merge.append_new_key_value(parent_node.keys[child_index])
        # child_to_merge.keys.append(parent_node.keys[child_index])

        for k in range(child_to_remove.keys_number):
            child_to_merge.append_new_key_value(child_to_remove.keys[k])
            # child_to_merge.keys.append(child_to_remove.keys[k])
            if not child_to_remove.leaf:
                child_to_merge.children.append(child_to_remove.children[k])

        if not child_to_remove.leaf:
            child_to_merge.children.append(child_to_remove.children.pop())

        parent_node.keys.pop(child_index)
        parent_node.children.pop(next_child_index)

    # Delete resolution
    def delete_merge(self, node: BTreeNode, child_index: int, direction: MergeDirection) -> None:
        next_child_index = child_index + 1 if direction == MergeDirection.NEXT else child_index - 1
        next_child_node = node.children[next_child_index]

        if next_child_index > child_index:
            self._delete_next_child_node(node, child_index, next_child_index)
        else:
            self._delete_next_child_node(node, next_child_index, child_index)

        # TODO: Move to separate method
        if node == self.root and node.keys_number == 0:
            self.root = next_child_node

    # Delete the sibling (left or right) and append first or last sibling's key and child to a current node
    @staticmethod
    def delete_sibling(node: BTreeNode, current_node_index: int, direction: MergeDirection) -> None:
        child = node.children[current_node_index]
        next_child_index = current_node_index + 1 if direction == MergeDirection.NEXT else current_node_index - 1
        next_child = node.children[next_child_index]

        # TODO: Refactor
        if current_node_index < 0:
            child.append_new_key_value(node.keys[current_node_index])
            # child.keys.append(node.keys[current_node_index])
            node.keys[current_node_index] = next_child.keys.pop(0)
            if not next_child.leaf:
                child.children.append(next_child.children.pop(0))
        else:
            child.keys.insert(0, node.keys[current_node_index - 1])
            node.keys[current_node_index - 1] = next_child.keys.pop()
            if not next_child.leaf:
                child.children.insert(0, next_child.children.pop())

    # Search key in the tree
    def search_key(self,
                   searching_key: TreeKey,
                   level: int = 0,
                   start_node: BTreeNode | None = None
                   ) -> Tuple[TreeKeyValue, int, int] | None:
        if start_node is None:
            start_node = self.root

        key_index = start_node.get_key_range_index(searching_key)

        if key_index < start_node.keys_number and searching_key == start_node.keys[key_index].key:
            return start_node.keys[key_index], level, key_index
        elif start_node.leaf:
            return None
        else:
            return self.search_key(searching_key, level + 1, start_node.children[key_index])


class BTreeTraversal:
    @staticmethod
    def traverse_node(node: BTreeNode, level: int) -> Generator[Tuple[int, BTreeNode], None, None]:
        yield level, node

        for child in node.children:
            yield from BTreeTraversal.traverse_node(child, level + 1)

    @staticmethod
    def traverse_tree_keys(tree: BTree) -> Generator[Tuple[int, int, TreeKeyValue], None, None]:
        for level, node in BTreeTraversal.traverse_tree(tree):
            for index, key in enumerate(node.keys):
                yield level, index, key

    @staticmethod
    def traverse_tree(tree: BTree) -> Generator[Tuple[int, BTreeNode], None, None]:
        yield from BTreeTraversal.traverse_node(tree.root, 0)


class BTreeValidator:
    @staticmethod
    def validate(tree: BTree) -> None:
        leafs_height = -1
        for level, node in BTreeTraversal.traverse_tree(tree):
            node_keys = [key_value.key for key_value in node.keys]
            assert sorted(node_keys) == node_keys, f'Keys {node_keys} are not sorted properly'

            if node.leaf:
                if leafs_height == -1:
                    leafs_height = level
                else:
                    assert leafs_height == level, 'Tree has different height in subtrees.'

                continue

            assert len(node.children) >= 2, f'Too few children on node {node}'
            if node != tree.root:  # root can have two and more children regardless of anything
                assert len(node.children) > tree.max_keys_number / 2, f'node {node} has to few children.'

            assert len(node.keys) <= tree.max_keys_number, \
                f'Too many keys on node {node}: expected number of keys: {tree.max_keys_number}, actual: {len(node.keys)}'

            assert len(node.keys) < len(node.children), f'There are more keys than children on node {node}'

        return


class BTreePrinter:
    @staticmethod
    def _print_node_tree(node: BTreeNode, level: int = 0) -> None:
        # TODO: Print with format
        print(f'Level  {level}   {len(node.keys)}:', end=' ')
        for key in node.keys:
            print(key, end=' ')
        print()

        for child in node.children:
            BTreePrinter._print_node_tree(child, level + 1)

    @staticmethod
    def print_tree(tree: BTree):
        BTreePrinter._print_node_tree(tree.root)
