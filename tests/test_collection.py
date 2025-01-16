from typing import List
import pytest

from exception import InvalidItemType, ItemAlreadyExists
from typed_collection import TypedCollection


class IntCollection(TypedCollection[int]):
    """Dummy typed collection with a generic type of Integer"""
    pass


class StrCollection(TypedCollection[str]):
    """Dummy typed collection with a generic type of String"""
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
def valid_int_list_again() -> List[int]:
    """Returns a list of valid integer values (again)."""
    return [6, 8, 10, 12, 13]


@pytest.fixture
def invalid_int_list() -> List:
    """Returns a list of valid integer values and an invalid string value."""
    return [1, 2, 3, "This is a string", 5, 26]


@pytest.fixture
def valid_str_list() -> List[str]:
    """Returns a list of valid string values."""
    return ["Once", "Upon", "a", "midnight", "dreary"]


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

def test_reverse(int_coll: IntCollection, valid_int_list):
    """Test the ability to reverse the collection."""
    int_coll.extend(valid_int_list)
    assert [rev for rev in reversed(int_coll)] == [26, 5, 4, 3, 2, 1]


def test_contains(int_coll: IntCollection, valid_int_list):
    """Test the ability to identify membership in the collection by use of the
        'in' operator"""
    int_coll.extend(valid_int_list)
    assert 26 in int_coll


def test_add_valid_collections(valid_int_list, valid_int_list_again):
    """Test the addition of two valid collections of the same type."""
    coll1 = IntCollection(valid_int_list)
    coll2 = IntCollection(valid_int_list_again)
    combined = coll1 + coll2
    assert [itm for itm in combined] == valid_int_list + valid_int_list_again


def test_add_invalid_collections(valid_int_list, valid_str_list):
    """Test raising of appropriate exception with the addition of two invalid
        collections of the differing types."""
    coll1 = IntCollection(valid_int_list)
    coll2 = StrCollection(valid_str_list)
    with pytest.raises(TypeError):
        combined = coll1 + coll2


def test_add_valid_item_to_collection(int_coll):
    """Test the addition of a valid item to a collection positioned as the left
        operand."""
    int_coll = int_coll + 26
    assert 26 in int_coll


def test_add_invalid_item_to_collection(int_coll):
    """Test the raising of appropriate exception with addition of an invalid
        item to a collection positioned as the left operand."""
    with pytest.raises(TypeError):
        int_coll = int_coll + "Invalid string"


def test_radd_valid_item_to_collection(int_coll):
    """Test the addition of a valid item to a collection positioned as the
        right operand."""
    int_coll = 26 + int_coll
    assert 26 in int_coll


def test_radd_invalid_item_to_collection(int_coll):
    """Test the raising of appropriate exception with addition of an invalid
        item to a collection positioned as the right operand."""
    with pytest.raises(TypeError):
        int_coll = "Invalid string" + int_coll

def test_len_valid_collection(int_coll: IntCollection, valid_int_list):
    int_coll.extend(valid_int_list)
    assert len(int_coll) == len(valid_int_list)

def test_len_empty_collection(int_coll: IntCollection):
    assert len(int_coll) == 0