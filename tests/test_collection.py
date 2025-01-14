from typing import List
import pytest

from exception import InvalidItemType, ItemAlreadyExists
from typed_collection import TypedCollection


class IntCollection(TypedCollection[int]):
    """Dummy typed collection with a generic type of Integer"""

    pass


@pytest.fixture
def int_coll() -> IntCollection:
    """Returns an empty unique collection that accepts only integers"""
    return IntCollection()


@pytest.fixture
def int_coll_non_unique() -> IntCollection:
    """Returns an empty non-unique collection that accepts only integers"""
    return IntCollection(unique=False)


@pytest.fixture
def valid_int_list() -> List[int]:
    """Returns a list of valid integer values."""
    return [1, 2, 3, 4, 5, 26]


@pytest.fixture
def invalid_int_list() -> List:
    """Returns a list of valid integer values and an invalid string value."""
    return [1, 2, 3, "This is a string", 5, 26]


def test_collection_init(valid_int_list):
    """Test initiation of collection with value list."""
    new_coll = IntCollection(valid_int_list)
    assert [itm for itm in new_coll._collection] == valid_int_list


def test_valid_append(int_coll: IntCollection):
    """Test appending a valid value to collection."""
    int_coll.append(26)
    assert int_coll._collection[0] == 26


def test_valid_extend_list(int_coll: IntCollection, valid_int_list):
    """Test extending the collection with a valid list iterable."""
    int_coll.extend(valid_int_list)
    coll_list = [itm for itm in int_coll._collection]
    assert coll_list == valid_int_list


def test_invalid_type_append(int_coll: IntCollection):
    """Test raising of appropriate exception when appending a value of an
    invalid type to collection."""
    with pytest.raises(InvalidItemType):
        int_coll.append("I'm a String")  # type: ignore


def test_invalid_type_extend(int_coll: IntCollection, invalid_int_list):
    """Test raising of appropriate exception when extending collection with a
    list iterable containing a value of invalid type."""
    with pytest.raises(InvalidItemType):
        int_coll.extend(invalid_int_list)


def test_invalid_non_unique_append(int_coll: IntCollection):
    """Test raising of appropriate exception when appending a duplicate valid
    value to a collection that already contains the value."""
    int_coll.append(26)
    with pytest.raises(ItemAlreadyExists):
        int_coll.append(26)


def test_invalid_non_unique_extend(int_coll: IntCollection, valid_int_list):
    """Test raising of appropriate exception when extending a non-unique
    collection with a list which contains duplicate values."""
    int_coll.append(26)
    with pytest.raises(ItemAlreadyExists):
        int_coll.extend(valid_int_list)


def test_invalid_type_extend_warn(int_coll: IntCollection, invalid_int_list):
    """Test extending collection with a list iterable containing a value of
    invalid type while ignoring errors and providing warnings."""
    with pytest.warns(UserWarning):
        int_coll.extend(invalid_int_list, True)


def test_invalid_non_unique_extend_warn(int_coll: IntCollection, valid_int_list):
    """Test extending a non-unique collection with a list which contains
    duplicate values, while ignoring errors and providing warnings."""
    int_coll.append(26)
    with pytest.warns(UserWarning):
        int_coll.extend(valid_int_list, True)


def test_base_class_init_warn():
    """Test instantiating the base class and providing a warning that the
    resulting collection will not enforce strict typing."""
    with pytest.warns(UserWarning):
        TypedCollection()


def test_valid_non_unique_append(int_coll_non_unique: IntCollection):
    """Test appending a valid duplicate value to a non-unique collection."""
    int_coll_non_unique.append(26)
    int_coll_non_unique.append(26)
    assert int_coll_non_unique._collection == [26, 26]
