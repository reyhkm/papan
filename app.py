from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///papan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Model untuk Papan Inspirasi
class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    public = db.Column(db.Boolean, default=True)
    items = db.relationship('Item', backref='board', lazy=True)

# Model untuk Item Inspirasi
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500))
    image_url = db.Column(db.String(200))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)

# Membuat tabel-tabel jika belum ada
with app.app_context():
    db.create_all()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    public_boards = Board.query.filter_by(public=True).all()
    return render_template('home.html', boards=public_boards)

@app.route('/board/<int:board_id>')
def view_board(board_id):
    board = Board.query.get_or_404(board_id)
    if board.public:
        return render_template('view_board.html', board=board)
    else:
        return "Papan ini tidak dapat diakses.", 403

@app.route('/create', methods=['GET', 'POST'])
def create_board():
    if request.method == 'POST':
        board_name = request.form['name']
        board_description = request.form['description']
        new_board = Board(name=board_name, description=board_description)
        db.session.add(new_board)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create.html')

@app.route('/board/<int:board_id>/add_item', methods=['POST'])
def add_item(board_id):
    board = Board.query.get_or_404(board_id)
    title = request.form['title']
    content = request.form['content']

    # Proses upload gambar (opsional)
    if 'image' in request.files:
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_url = url_for('uploaded_file', filename=filename)
        else:
            image_url = None
    else:
        image_url = None

    new_item = Item(title=title, content=content, image_url=image_url, board_id=board_id)
    db.session.add(new_item)
    db.session.commit()

    return redirect(url_for('view_board', board_id=board_id))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
