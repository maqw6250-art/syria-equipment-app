import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'syria_heavy_equipment_secret_key_2026'

# قراءة متغير البيئة DATABASE_URL من Render للتوصيل مع PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///equipment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ADMIN_PASSWORD = '0551393371'  # كلمة مرور لوحة التحكم

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    equipments = Equipment.query.order_by(Equipment.id.desc()).all()
    formatted_equipments = []
    for eq in equipments:
        clean_phone = ''.join(filter(str.isdigit, eq.phone))
        if clean_phone.startswith('0'):
            clean_phone = '963' + clean_phone[1:]
        
        formatted_equipments.append({
            'id': eq.id,
            'name': eq.name,
            'category': eq.category,
            'image': eq.image if eq.image else 'https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=600&q=80',
            'description': eq.description,
            'phone': eq.phone,
            'clean_phone': clean_phone
        })

    return render_template('index.html', equipments=formatted_equipments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('كلمة المرور غير صحيحة!')
    return render_template('admin.html', login_page=True)

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    equipments = Equipment.query.order_by(Equipment.id.desc()).all()
    return render_template('admin.html', equipments=equipments, login_page=False)

@app.route('/add', methods=['POST'])
def add_equipment():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    new_eq = Equipment(
        name=request.form.get('name'),
        category=request.form.get('category'),
        image=request.form.get('image'),
        description=request.form.get('description'),
        phone=request.form.get('phone')
    )
    db.session.add(new_eq)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
def delete_equipment(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    eq = Equipment.query.get_or_404(id)
    db.session.delete(eq)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)