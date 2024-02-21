from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Update the SQLALCHEMY_DATABASE_URI with your MySQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/book'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = 'book'

    isbn13 = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    availability = db.Column(db.Integer)

    def __init__(self, isbn13, title, price, availability):
        self.isbn13 = isbn13
        self.title = title
        self.price = price
        self.availability = availability

    def json(self):
        return {"isbn13": self.isbn13, "title": self.title, "price": self.price, "availability": self.availability}

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search_term = request.form['search']
        # Adjust the filter to search by title
        results = Product.query.filter(Product.title.like(f'%{search_term}%')).all()
        return render_template('search_results.html', results=results)
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)