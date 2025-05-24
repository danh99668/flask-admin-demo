import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Chào mừng đến trang chủ quản trị' in rv.data

def test_register_and_login(client):
    # Đăng ký tài khoản mới
    rv = client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpass'
    }, follow_redirects=True)
    assert b'Đăng ký thành công' in rv.data

    # Đăng nhập với tài khoản vừa đăng ký
    rv = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert b'Quản trị' in rv.data or b'User' in rv.data or b'Product' in rv.data

def test_login_fail(client):
    rv = client.post('/login', data={
        'username': 'saiuser',
        'password': 'saimatkhau'
    }, follow_redirects=True)
    assert b'Sai tài khoản hoặc mật khẩu' in rv.data
