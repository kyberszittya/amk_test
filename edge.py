import hashlib
import typing
from enum import Enum

from himeko_hypergraph.src.elements.element import HypergraphElement, HypergraphMetaElement

from himeko_hypergraph.src.elements.vertex import HyperVertex
from himeko_hypergraph.src.exceptions.basic_exceptions import InvalidHypergraphElementException, \
    InvalidRelationDirection


class EnumRelationDirection(Enum):
    UNDEFINED = 0
    IN = 1
    OUT = 2

    def __str__(self):
        match(self):
            case EnumRelationDirection.UNDEFINED:
                return "--"
            case EnumRelationDirection.IN:
                return "<-"
            case EnumRelationDirection.OUT:
                return "->"
            case _:
                raise InvalidRelationDirection("Invalid direction is provided during relation creation")


class HypergraphRelation(HypergraphMetaElement):

    def __init__(self, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, value,
                 parent: HypergraphElement, target: HypergraphElement, direction: EnumRelationDirection):
        super().__init__(timestamp, serial, guid, suid, label, parent)
        self.__value = value
        self.__target = target
        self.__dir = direction

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, v):
        self.__value = v

    @property
    def direction(self):
        return self.__dir

    @direction.setter
    def direction(self, dir: EnumRelationDirection):
        self.__dir = dir

    @property
    def target(self):
        return self.__target

    def is_out(self):
        return self.__dir == EnumRelationDirection.UNDEFINED or self.__dir == EnumRelationDirection.OUT

    def is_in(self):
        return self.__dir == EnumRelationDirection.UNDEFINED or self.__dir == EnumRelationDirection.IN

    # Overload functions
    def __iadd__(self, other):
        self.__value += other

    def __isub__(self, other):
        self.__value -= other

    def __itruediv__(self, other):
        self.__value /= other

    def __imul__(self, other):
        self.__value *= other



def relation_label_default(e0: HypergraphElement, v0: HyperVertex, r: EnumRelationDirection):
    return f"{e0.label}{str(r)}{v0.label}"


def relation_name_default(e0: HypergraphElement, v0: HyperVertex, r: EnumRelationDirection):
    return f"{e0.name}{str(r)}{v0.label}"


class HyperEdge(HypergraphElement):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HyperVertex]) -> None:
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        self.__relations: typing.Dict[bytes, HypergraphRelation] = {}
        # Vertex associations
        self.__associations: typing[bytes, HypergraphRelation] = {}
        # Counts
        self.__cnt_in_relations = 0
        self.__cnt_out_relations = 0

    def __create_default_relation_guid(self, label: str) -> bytes:
        return hashlib.sha384(label.encode('utf-8')).digest()

    def associate_vertex(self, r: typing.Tuple[HyperVertex, EnumRelationDirection, float|typing.Iterable]):
        v, d, _val = r
        if not isinstance(v, HypergraphElement):
            raise InvalidHypergraphElementException("Unable to add incompatible element to graph")
        __lbl = relation_label_default(self, v, d)
        guid = self.__create_default_relation_guid(__lbl)
        # TODO: SUID revamp
        suid = guid
        n_assoc = len(self.__associations.keys())
        rel = HypergraphRelation(self.timestamp, n_assoc, guid, suid, __lbl, _val, self, v, d)
        self.__associations[guid] = rel
        # Increment relation number
        match d:
            case EnumRelationDirection.IN:
                self.__cnt_in_relations += 1
            case EnumRelationDirection.OUT:
                self.__cnt_out_relations += 1
            case EnumRelationDirection.UNDEFINED:
                self.__cnt_out_relations += 1
                self.__cnt_in_relations += 1



    def unassociate_vertex(self, v: HyperVertex):
        # TODO: unnassociation
        if not isinstance(v, HypergraphElement):
            raise InvalidHypergraphElementException("Unable to remove incompatible element from graph")

    def associate_edge(self, r: typing.Tuple[typing.Any, EnumRelationDirection, float|typing.Iterable]):
        e, d = r
        if not isinstance(e, HyperEdge):
            raise InvalidHypergraphElementException("Unable to associate edge with incompatible element")

    def element_in_edge(self, v: HypergraphElement) -> bool:
        if not isinstance(v, HypergraphElement):
            raise InvalidHypergraphElementException("Unable to check containment of incompatible element")
        return True

    def all_relations(self) -> typing.Generator[HypergraphRelation, None, None]:
        for x in self.__associations.values():
            yield x
        for x in self.__relations.values():
            yield x

    def out_relations(self) -> typing.Generator[HypergraphRelation, None, None]:
        for x in filter(lambda relx: relx.is_out(), self.all_relations()):
            yield x

    def in_relations(self) -> typing.Generator[HypergraphRelation, None, None]:
        for x in filter(lambda relx: relx.is_in(), self.all_relations()):
            yield x

    def out_vertices(self):
        return map(lambda x: x.target, self.out_relations())

    def in_vertices(self):
        return map(lambda x: x.target, self.in_relations())

    def __iter__(self):
        return self.all_relations()

    # Overload operations

    def __iadd__(self, other):
        self.associate_vertex(other)
        return self

    def __isub__(self, other):
        self.unassociate_vertex(other)
        return self

    def __contains__(self, item):
        if isinstance(item, HypergraphElement):
            return self.element_in_edge(item)

    def __len__(self):
        return len(self.__relations.keys()) + len(self.__associations.keys())

    # Count properties

    @property
    def cnt_in_relations(self):
        return self.__cnt_in_relations

    @property
    def cnt_out_relations(self):
        return self.__cnt_out_relations


class ExecutableHyperEdge(HyperEdge):

    def __call__(self, *args, **kwargs):
        return self.operate(*args, **kwargs)

    def operate(self, *args, **kwargs):
        raise NotImplementedError


class ExecutableHyperVertex(HyperVertex):

    def __call__(self, *args, **kwargs):
        return self.operate(*args, **kwargs)

    def operate(self, *args, **kwargs):
        raise NotImplementedError
