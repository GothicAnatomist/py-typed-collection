"""
TypedCollection for Single or Multi-Type Collections

This module defines a `TypedCollection` base class that leverages Python's generics
(PEP 646 variadic generics) to provide strict runtime enforcement of one or more
item types. Developers can subclass `TypedCollection` and specify type parameters
(e.g., `TypedCollection[int, str]`) to create specialized collections that accept
only those types.

If no type arguments are provided, the collection defaults to treating its items as
`Any`, effectively disabling type enforcement. This design offers flexibility for
both strict and untyped use cases, while still providing shared functionality like
uniqueness constraints, iteration, and list-like methods.
"""

from abc import ABC
from typing import (
    Any,
    Collection,
    Generator,
    Generic,
    Iterable,
    List,
    Optional,
    Reversible,
    Self,
    Tuple,
    Type,
    TypeVarTuple,
    Unpack,
    cast,
    get_args,
)
from warnings import warn

from exception import InvalidItemType, ItemAlreadyExists


ItemType = TypeVarTuple("ItemType")


class TypedCollection(ABC, Collection, Reversible, Generic[Unpack[ItemType]]):
    """
    Abstract collection class with defined member type(s).

    An abstract collection class where specific member object types are
    permitted to be stored. The required type(s) are defined using the generic
    typing syntax when the subclass inherits this collection.

    Args:
        ABC (ABC): Helper class for creating abstract classes
        Collection (Collection): Inheriting from Collection
        Reversible (Reversible): Inheriting from Reversible
        Generic (ItemType): Generic typing to define which object types are
        valid within the collection using the TypeVarTuple, ItemType.
    """

    _type_args: Tuple[type, ...] = cast("tuple[type, ...]", (Any,))

    def __init__(
        self, coll: Optional[List[object]] = None, unique: bool = True
    ) -> None:
        if coll is None:
            coll = []

        self._collection: List[object] = []
        self._unique: bool = unique

        if self._item_type == (Any,):
            warn(
                "No type arguments were provided for TypedCollection. "
                "Type enforcement is disabled and this collection is effectively untyped (Any). "
                "To enable type checks, declare your subclass with type parameters, e.g. "
                "`class MyCollection(TypedCollection[int, str]): ...`",
                UserWarning,
                stacklevel=2,
            )
        self.extend(coll)

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        orig_bases = getattr(cls, "__orig_bases__", None)
        if orig_bases:
            base = orig_bases[0]
            cls._type_args = get_args(base)

    @property
    def _item_type(self) -> Tuple[Type, ...]:
        return type(self)._type_args

    @property
    def _is_untyped(self):
        return self._item_type == (Any,)

    def __len__(self) -> int:
        return len(self._collection)

    def __iter__(self) -> Generator[Any, None, None]:
        for item in self._collection:
            yield item

    def __reversed__(self) -> Generator[Any, None, None]:
        for item in reversed(self._collection):
            yield item

    def __contains__(self, item: Any) -> bool:
        return item in self._collection

    def __add__(self, other) -> Self:
        new_collection = self.__class__()
        new_collection.extend(self)

        if isinstance(other, self._item_type):
            new_collection.append(other)
            return new_collection

        if isinstance(other, type(self)):
            new_collection.extend(other)
            return new_collection

        raise TypeError(
            "Object passed is not instance of " f"'{self._item_type}' or '{type(self)}'"
        )

    def __radd__(self, other) -> Self:
        return self.__add__(other)

    def append(self, item: Any) -> None:
        """
        Append object to the end of the collection.

        Args:
            item (Union[Unpack[ItemType]]): Object of type defined by generic
            TypeVar tuple.

        Raises:
            InvalidItemType: Type of item not compatible with collection.
            ItemAlreadyExists: Item already exists in collection with unique
            constraint.
        """

        if not self._is_untyped and not isinstance(item, self._item_type):
            raise InvalidItemType(type(item), self._item_type)

        if self._unique and item in self._collection:
            raise ItemAlreadyExists()

        self._collection.append(item)

    def extend(self, collection: Iterable, ignore_error: bool = False) -> None:
        """
        Extend collection by appending elements from the iterable.

        Args:
            collection (Iterable): Iterable containing objects to add to
            collection.
            ignore_error (bool, optional): Boolean to determine whether to
            raise exceptions if an invalid object is found. Defaults to False.

        Raises:
            iit: Exception where object item is of an invalid type
            iae: Exception where object item already exists in collection
            where collection has a unique constraint.
        """
        for item in collection:
            try:
                self.append(item)
            except InvalidItemType as iit:
                if ignore_error:
                    warn(
                        f"Item of type {type(item)} is not valid in this "
                        "collection and was not added.",
                        UserWarning,
                    )
                else:
                    raise iit
            except ItemAlreadyExists as iae:
                if ignore_error:
                    warn(
                        "This collection has a unique constraint and the item"
                        " passed already exists.",
                        UserWarning,
                    )
                else:
                    raise iae
