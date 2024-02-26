from flask import Flask, render_template, request, jsonify
import duckdb
from datetime import datetime

NEW_ID_CATEGORY = "nextval('categories_id_seq')"
NEW_ID_EXPENSE  = "nextval('expenses_id_seq')"

app = Flask(__name__)
@app.route("/")
def index():
    # Add a new expense
    with duckdb.connect(database='expense_tracker.db', read_only=False) as connection:
        queried_expenses = connection.execute("SELECT * FROM expenses").fetchall()
        categories = connection.execute("SELECT * FROM categories").fetchall()
        categories_dict = {row[0]: row[1] for row in categories}
        expenses = [{"id": row[0], "name": row[1], "amount": row[2], "date": row[3], "category": categories_dict.get(row[4], "")} for row in queried_expenses]
    return render_template("index.html", expenses=expenses, categories=categories_dict)

@app.route("/expenses", methods=["POST"])
def post_expenses():
    # Add a new expense
    with duckdb.connect(database='expense_tracker.db', read_only=False) as connection:
        data = request.json
        match data:
            case {"name": name, "amount": amount, "date": date, "category": category}:
                # Try to parse date and get category_id
                try:
                    name = str(name)
                    amount = float(amount)
                    category_id = connection.execute("SELECT id FROM categories WHERE category_name=?", [category]).fetchone()[0]
                    date = datetime.strptime(date, "%Y-%m-%d").date()
                    connection.execute(f"INSERT INTO expenses VALUES ({NEW_ID_EXPENSE}, ?, ?, ?, ?)", [name, amount, date, category_id])
                    return jsonify({"message": f"Succesfully added '{name}'"}), 200
                except Exception as e:
                    return jsonify({"message": f"Error: {e}"}), 400
            case error:
                return jsonify({"message": f"Error: {error}"}), 400

    
@app.route("/expenses/<id>", methods=["DELETE"])
def handle_expenses(id):
    # Delete an expense
    with duckdb.connect(database='expense_tracker.db', read_only=False) as connection:
        connection.execute("DELETE FROM expenses WHERE id=?", [id])
        return jsonify({"message": "Expense deleted successfully"})


@app.route("/category/<category>", methods=["POST"])
def add_category(category):
    if category == "":
        return jsonify({"message": "Error: Empty category"}), 400
    # Add a new category
    category = category.strip()
    with duckdb.connect(database='expense_tracker.db', read_only=False) as connection:
        try:
            # Check if category already exists
            result = connection.execute("SELECT * FROM categories WHERE category_name=?", [category]).fetchone()
            if result:
                return jsonify({"message": f"Error: Category '{category}' already exists"}), 400
            connection.execute(f"INSERT INTO categories (id, category_name) VALUES ({NEW_ID_CATEGORY}, ?)", [category])
            return jsonify({"message": f"Added category '{category}'"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message": f"Error: {e}"}), 400
    

@app.route("/category/<category>", methods=["DELETE"])
def delete_category(category):
    if category == "":
        return jsonify({"message": "Error: Empty category"}), 400
    # Delete a category
    with duckdb.connect(database='expense_tracker.db', read_only=False) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM categories WHERE category_name=?", [category])
            deleted_rows = cursor.rowcount
            cursor.commit()
            message = f"Deleted category {category}"
            return jsonify({"message": message}), 200
        except Exception as e:
            print(e)
            return jsonify({"message": f"Error: {e}"}), 400

if __name__ == "__main__":
    app.run(debug=True)
