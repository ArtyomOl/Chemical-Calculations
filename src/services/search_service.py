from typing import List, Optional

from domain.models import Element
from infrastructure.repositories import ElementRepository


class SearchNode:
    def __init__(self, kind: str, is_element: bool = False):
        self.kind = kind
        self.children: List[SearchNode] = []
        self.is_element = is_element

    def add_child(self, child: 'SearchNode'):
        self.children.append(child)


class SearchTree:
    def __init__(self):
        self.root = SearchNode('Any')

    def build_from_elements(self, elements: List[Element]):
        for element in elements:
            branches = element.branches + [element.name]
            self._add_branch(branches)

    def _add_branch(self, branch_path: List[str]):
        current = self.root
        
        for i, branch_name in enumerate(branch_path):
            is_leaf = (i == len(branch_path) - 1)
            
            existing = self._find_child(current, branch_name)
            if existing:
                current = existing
            else:
                new_node = SearchNode(branch_name, is_element=is_leaf)
                current.add_child(new_node)
                current = new_node

    def _find_child(self, node: SearchNode, kind: str) -> Optional[SearchNode]:
        for child in node.children:
            if child.kind == kind:
                return child
        return None

    def _find_node(self, node: SearchNode, target: str) -> Optional[SearchNode]:
        if node.kind == target:
            return node
        
        for child in node.children:
            result = self._find_node(child, target)
            if result:
                return result
        
        return None

    def _collect_elements(self, node: SearchNode, result: List[str]):
        if node.is_element:
            result.append(node.kind)
        
        for child in node.children:
            self._collect_elements(child, result)

    def get_elements(self, element_type: str) -> List[str]:
        node = self._find_node(self.root, element_type)
        if not node:
            return []
        
        result = []
        self._collect_elements(node, result)
        return result


class SearchService:
    def __init__(self):
        self.element_repo = ElementRepository()
        self.tree = SearchTree()
        self._build_tree()

    def _build_tree(self):
        elements = self.element_repo.get_all()
        self.tree.build_from_elements(elements)

    def rebuild_tree(self):
        self.tree = SearchTree()
        self._build_tree()

    def get_elements_by_filter(self, filter_string: str) -> List[str]:
        if not filter_string or filter_string.strip() == '':
            filter_string = 'Any'
        
        filters = self._parse_filter(filter_string)
        result = []
        is_negation = False
        
        for f in filters:
            if f.lower() == 'not':
                is_negation = True
            else:
                if is_negation:
                    all_elements = self.tree.get_elements('Any')
                    excluded = self.tree.get_elements(f)
                    result.extend([e for e in all_elements if e not in excluded])
                else:
                    result.extend(self.tree.get_elements(f))
                is_negation = False
        
        return list(set(result))

    def _parse_filter(self, filter_string: str) -> List[str]:
        parts = filter_string.split()
        normalized = []
        
        for part in parts:
            if part.lower() == 'not':
                normalized.append('not')
            else:
                normalized.append(self._normalize_name(part))
        
        return normalized

    def _normalize_name(self, name: str) -> str:
        name = name.lower()
        if not name:
            return name
        
        result = name[0].upper() + name[1:]
        
        hyphen_idx = result.find('-')
        if hyphen_idx != -1 and hyphen_idx < len(result) - 1:
            result = result[:hyphen_idx + 1] + result[hyphen_idx + 1].upper() + result[hyphen_idx + 2:]
        
        return result