from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin_demo.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Thêm trường password

    def __repr__(self):
        return f'<User {self.username}>'

# Thêm model Product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

# Phân quyền cho admin
class AdminModelView(ModelView):
    def is_accessible(self):
        return session.get('logged_in')
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

admin = Admin(app, name='Quản trị', template_mode='bootstrap3')
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Product, db.session))

# Trang chủ
@app.route('/')
def home():
    return render_template('home.html')

# Đăng nhập đơn giản
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['logged_in'] = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.index'))
        error = 'Sai tài khoản hoặc mật khẩu!'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not username or not email or not password:
            error = 'Vui lòng nhập đầy đủ thông tin.'
        elif User.query.filter_by(username=username).first():
            error = 'Tên đăng nhập đã tồn tại.'
        elif User.query.filter_by(email=email).first():
            error = 'Email đã được sử dụng.'
        else:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            success = 'Đăng ký thành công! Bạn có thể đăng nhập.'
    return render_template('register.html', error=error, success=success)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
