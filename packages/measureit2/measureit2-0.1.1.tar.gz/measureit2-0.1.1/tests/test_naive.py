from measureit2.dot_product import naive
import pytest

def test_naive_dp():
    a, _ = naive.dp0([1,0,0,1],[0, 0, 1, 1])
    assert a==1

    b, _ = naive.dp1([3,4,3,4],[1, 1, 1, 1])
    assert b==14

if __name__ == '__main__': 
    pytest.main()