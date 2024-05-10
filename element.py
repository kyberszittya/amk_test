import abc
import typing

from himeko_hypergraph.src.exceptions.basic_exceptions import InvalidParentException


class HypergraphMetaElement(abc.ABC):

    def __init__(self, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None):
        """

        :param timestamp: timestamp of creation
        :param guid: GUID of element (most likely a hash) on creation must be unique
        :param serial: serial number in certain domain (e.g. when inserted into an edge or as part of a vertex)
        """
        self.__timestamp = timestamp
        self.__guid = guid
        self.__serial = serial
        if not (parent is None or isinstance(parent, HypergraphMetaElement)):
            raise InvalidParentException("Invalid parent element to hypergraph element")
        self.__parent = parent
        self.__suid = suid
        self.__label = label

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def guid(self):
        return self.__guid

    @property
    def serial(self):
        return self.__serial

    @property
    def suid(self):
        return self.__suid

    @property
    def parent(self):
        return self.__parent

    @property
    def label(self):
        return self.__label


class HypergraphElement(HypergraphMetaElement):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HypergraphMetaElement] = None) -> None:
        """

        :param name: Name of element
        :param timestamp: timestamp of creation
        :param serial: serial number in certain domain
        :param guid: GUID of element (most likely a hash)
        :param suid: UID derived from domain inception
        """
        super().__init__(timestamp, serial, guid, suid, label, parent)
        self.__name = name


    @property
    def name(self):
        return self.__name


