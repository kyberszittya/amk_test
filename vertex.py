import typing

from himeko_hypergraph.src.elements.element import HypergraphElement
from himeko_hypergraph.src.exceptions.basic_exceptions import InvalidHypergraphElementException, InvalidParentException, ElementSelfParentException

from collections import deque

class HyperVertex(HypergraphElement):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None):
        """

        :param name: name of vertex
        :param timestamp: timestamp of creation
        :param serial: serial number in a certain domain
        :param guid: unique GUID of element
        :param suid: UID derived from domain inception
        """
        if not (isinstance(parent, HyperVertex) or parent is None):
            raise InvalidParentException("Parent element invalid")
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        # Add current element to parent
        if parent is not None:
            parent.add_element(self)
        self._elements: typing.Dict[bytes, HypergraphElement] = {}
        # Attributes
        self.__named_attr: typing.Dict[str, typing.Any] = {}
        # Indexing
        self.__index_named_elements: typing.Dict[str, HypergraphElement] = {}

    @property
    def attribute_names(self):
        return [c for c in self.__named_attr.keys()]

    def add_element(self, v: HypergraphElement):
        # Ensure that the element is not itself
        if v is self:
            raise ElementSelfParentException("Parent element cannot be itself (composition loop)")
        # Check if element is a hypergraph element anyway
        if not isinstance(v, HypergraphElement):
            raise InvalidHypergraphElementException("Unable to add incompatible element")
        self._elements[v.guid] = v
        self.__index_named_elements[v.name] = v
        # Set element parent (if parent is not already self)
        if v.parent is not self:
            v._parent = self

    def remove_element(self, v: HypergraphElement):
        if not isinstance(v, HypergraphElement):
            raise InvalidHypergraphElementException("Unable to remove incompatible element")
        self._elements.pop(v.guid)

    def update_element(self, v: HypergraphElement):
        if v.name not in self.__index_named_elements:
            self.add_element(v)
        else:
            # Remove existing element
            __tmp = self.__index_named_elements[v.name]
            self._elements.pop(__tmp.guid)
            self.__index_named_elements[v.name] = v
            self.__index_named_elements[v.guid] = v

    def __iadd__(self, other):
        if isinstance(other, typing.Iterable):
            for o in other:
                self.add_element(o)
        else:
            self.add_element(other)
        return self

    def __isub__(self, other):
        self.remove_element(other)
        return self

    def __imul__(self, other):
        """
        Update elements
        :param other:
        :return:
        """
        if isinstance(other, typing.Iterable):
            for o in other:
                self.update_element(o)
        else:
            self.update_element(other)
        return self

    def __len__(self):
        return len(self._elements.values())

    def __setitem__(self, key: str, value):
        if isinstance(key, str):
            self.__named_attr[key] = value

    def __getitem__(self, item):
        if isinstance(item, str):
            if item in self.__named_attr:
                return self.__named_attr[item]
            else:
                raise KeyError
        return None

    def __hash__(self):
        return int.from_bytes(self.guid, "big")

    def get_subelements(self, condition: typing.Callable[[HypergraphElement], bool]):
        visited = set()
        fringe = deque()
        fringe.append(self)
        __res = []
        while len(fringe) != 0:
            __e = fringe.pop()
            if __e not in visited:
                visited.add(__e)
                if condition(__e):
                    __res.append(__e)
                    yield __e
                for _, ch in __e._elements.items():
                    fringe.appendleft(ch)
        return __res





