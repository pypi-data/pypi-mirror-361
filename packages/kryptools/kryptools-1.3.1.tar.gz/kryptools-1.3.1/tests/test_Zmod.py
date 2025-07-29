import pytest
from math import gcd
from kryptools import Zmod, euler_phi


def test_Zmod_ops():
    for n in range(2, 10):
        Z_n = Zmod(n)
        for a in range(n):
            aa = Z_n(a)
            bool(aa) == bool(a)
            for i in range(4):
                assert aa ** i == Z_n(pow(a, i, n))
                if i == 0 or gcd(a, n) == 1:
                    assert aa ** -i == Z_n(pow(a, -i, n))
                else:
                    with pytest.raises(ValueError):
                        aa ** -i
            if gcd(a, n) == 1:
                assert aa ** aa.order() == Z_n(1)
            else:
                with pytest.raises(ValueError):
                    aa.order()
            for b in range(n):
                bb = Z_n(b)
                assert aa + bb == Z_n(a + b)
                assert aa - bb == Z_n(a - b)
                assert aa * bb == Z_n(a * b)
                if gcd(b, n) == 1:
                    assert aa / bb == Z_n(a * pow(b, -1, n))


def test_Zmod_methods():
    Z_5 = Zmod(5)
    assert len(list(Z_5)) == 5
    assert len(list(Z_5.star())) == 4
    assert Z_5.order() == 4
    assert Z_5(3).order() == 4
    assert Z_5(1).is_generator() is False
    assert Z_5(3).is_generator() is True
    assert list(Z_5.generators()) == Z_5([2, 3])
    assert list(Z_5.star()) == Z_5([1, 2, 3, 4])
    assert [Z_5(i).sharp() for i in range(Z_5.n)] == [0, 1, 2, -2, -1]
    assert [abs(Z_5(i)) for i in range(Z_5.n)] == [0, 1, 2, 2, 1]
    assert not Z_5(0)
    assert Z_5(1)
    assert Z_5(2) == Z_5(2)
    assert Z_5(2) != Z_5(3)
    assert Z_5(2) != 2
    assert str(Z_5(3)) == "3"
    Z_5.short = False
    assert str(Z_5(6)) == "1 (mod 5)"

    Z_6 = Zmod(6)
    assert len(list(Z_6)) == 6
    assert len(list(Z_6.star())) == 2
    assert Z_6.order() == 2
    assert Z_6(5).order() == 2
    with pytest.raises(ValueError):
        Z_6(3).order()
    assert Z_6(1).is_generator() is False
    assert Z_6(5).is_generator() is True
    assert list(Z_6.generators()) == Z_6([5])
    assert list(Z_6.star()) == Z_6([1, 5])
    assert Z_6(1)
    assert Z_6(2) == Z_6(2)
    assert Z_6(2) != Z_6(3)
    assert Z_5(2) != Z_6(2)
    assert str(Z_6(3)) == "3"


def test_Zmod_order():
    for n in range(2, 10):
        Z_n = Zmod(n)
        assert Z_n.order() == euler_phi(n)


OEIS_A033948 = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 13, 14, 17, 18, 19, 22, 23, 25, 26, 27,
                29, 31, 34, 37, 38, 41, 43, 46, 47, 49, 50, 53, 54, 58, 59, 61, 62, 67, 71, 73, 74,
                79, 81, 82, 83, 86, 89, 94, 97, 98, 101, 103, 106, 107, 109, 113, 118, 121, 122, 125,
                127, 131, 134, 137, 139]


def test_Zmod_cyclic():
    for n in range(2, OEIS_A033948[-1]+1):
        assert Zmod(n).is_cyclic() == (n in OEIS_A033948)
