from webapp.views import get_pagination_page_array


def test_pagination():
    assert get_pagination_page_array(3, 2, 5) == [1, 2, 3, 4, 5]


def test_pagination_lower_bound_is_caught_and_added_to_top_bound():
    assert get_pagination_page_array(1, 3, 10) == [1, 2, 3, 4, 5, 6, 7]


def test_pagination_upper_bound_is_caught_and_added_to_lower_bound():
    assert get_pagination_page_array(9, 2, 10) == [6, 7, 8, 9, 10]
