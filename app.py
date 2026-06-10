from flask import Flask, render_template, request, redirect, session
from models import db, User, Event, Registration
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club.db'

db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect('/dashboard')
        else:
            error = 'Invalid email or password'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    from models import User
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', name=user.name, role=user.role)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
@app.route('/events', methods=['GET', 'POST'])
def events():
    if 'user_id' not in session:
        return redirect('/login')
    error = None
    success = None
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        capacity = request.form['capacity']
        new_event = Event(title=title, date=date, capacity=int(capacity), club_id=1)
        db.session.add(new_event)
        db.session.commit()
        success = 'Event created successfully!'
    all_events = Event.query.all()
    return render_template('events.html', events=all_events, role=session['role'], error=error, success=success)

@app.route('/register/<int:event_id>')
def register_event(event_id):
    if 'user_id' not in session:
        return redirect('/login')
    event = Event.query.get(event_id)
    existing = Registration.query.filter_by(user_id=session['user_id'], event_id=event_id).first()
    if existing:
        return redirect('/events')
    registrations = Registration.query.filter_by(event_id=event_id).count()
    if registrations >= event.capacity:
        return redirect('/events')
    new_reg = Registration(user_id=session['user_id'], event_id=event_id)
    db.session.add(new_reg)
    db.session.commit()
    return redirect('/events')


if __name__ == '__main__':
    app.run(debug=True)