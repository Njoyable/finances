from flask import Flask, render_template, request, jsonify
from flask_basicauth import BasicAuth
import duckdb
from datetime import datetime
import base64

NEW_ID_CATEGORY = "nextval('categories_id_seq')"
NEW_ID_EXPENSE = "nextval('expenses_id_seq')"

app = Flask(__name__)
basic_auth = BasicAuth(app)


@app.route("/")
@basic_auth.required
def index():
    # Add a new expense
    with duckdb.connect(database="expense_tracker.db", read_only=False) as connection:
        queried_expenses = connection.execute("SELECT * FROM expenses").fetchall()
        categories = connection.execute("SELECT * FROM categories").fetchall()
        id_to_category = {row[0]: row[1] for row in categories}
        category_to_id = {row[1]: row[0] for row in categories}
        expenses = [
            {
                "id": row[0],
                "name": row[1],
                "amount": row[2],
                "date": row[3],
                "category": id_to_category.get(row[4], ""),
            }
            for row in queried_expenses
        ]
        summed_expenses_by_category = dict()
        for category in id_to_category.values():
            result = connection.execute(
                "SELECT SUM(amount) FROM expenses WHERE category_id=?",
                [category_to_id[category]],
            ).fetchone()[0]
            summed_expenses_by_category[category] = result if result else 0
        summed_expenses_by_date = dict()

        # Initialize the dictionary with all categories and "All" as keys for each date
        dates = set([str(expense["date"]) for expense in expenses])
        for category in [*id_to_category.values(), "All"]:
            summed_expenses_by_date[category] = dict()
            for date in dates:
                summed_expenses_by_date[category][date] = 0
        for expense in expenses:
            category = expense["category"]
            date = str(expense["date"])
            amount = expense["amount"]
            summed_expenses_by_date[category][date] += amount
            summed_expenses_by_date["All"][date] += amount
    return render_template(
        "index.html",
        expenses=expenses,
        categories=id_to_category,
        summed_expenses_by_category=summed_expenses_by_category,
        summed_expenses_by_date=summed_expenses_by_date,
    )


@app.route("/expenses", methods=["POST"])
def post_expenses():
    # Add a new expense
    with duckdb.connect(database="expense_tracker.db", read_only=False) as connection:
        data = request.json
        match data:
            case {"name": name, "amount": amount, "date": date, "category": category}:
                # Try to parse date and get category_id
                try:
                    name = str(name)
                    amount = float(amount)
                    category_id = connection.execute(
                        "SELECT id FROM categories WHERE category_name=?", [category]
                    ).fetchone()[0]
                    date = datetime.strptime(date, "%Y-%m-%d").date()
                    connection.execute(
                        f"INSERT INTO expenses VALUES ({NEW_ID_EXPENSE}, ?, ?, ?, ?)",
                        [name, amount, date, category_id],
                    )
                    return jsonify({"message": f"Succesfully added '{name}'"}), 200
                except Exception as e:
                    return jsonify({"message": f"Error: {e}"}), 400
            case error:
                return jsonify({"message": f"Error: {error}"}), 400


@app.route("/expenses/<id>", methods=["DELETE"])
def handle_expenses(id):
    # Delete an expense
    with duckdb.connect(database="expense_tracker.db", read_only=False) as connection:
        result = connection.execute("DELETE FROM expenses WHERE id=?", [id]).df().to_dict()
        if result["Count"][0] == 0:
            return jsonify({"message": f"Error: Expense '{id}' does not exist"}), 400
        else:
            return jsonify({"message": "Expense deleted successfully"})


@app.route("/category/<category>", methods=["POST"])
def add_category(category):
    if category == "":
        return jsonify({"message": "Error: Empty category"}), 400
    # Add a new category
    category = category.strip()
    with duckdb.connect(database="expense_tracker.db", read_only=False) as connection:
        try:
            # Check if category already exists
            result = connection.execute(
                "SELECT * FROM categories WHERE category_name=?", [category]
            ).fetchone()
            if result:
                return (
                    jsonify(
                        {"message": f"Error: Category '{category}' already exists"}
                    ),
                    400,
                )
            connection.execute(
                f"INSERT INTO categories (id, category_name) VALUES ({NEW_ID_CATEGORY}, ?)",
                [category],
            )
            return jsonify({"message": f"Added category '{category}'"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message": f"Error: {e}"}), 400


@app.route("/category/<category>", methods=["DELETE"])
def delete_category(category):
    if category == "":
        return jsonify({"message": "Error: Empty category"}), 400
    # Delete a category
    with duckdb.connect(database="expense_tracker.db", read_only=False) as connection:
        try:
            result = (
                connection.execute(
                    "DELETE FROM categories WHERE category_name=?", [category]
                )
                .df()
                .to_dict()
            )
            if result["Count"][0] == 0:
                return (
                    jsonify(
                        {"message": f"Error: Category '{category}' does not exist"}
                    ),
                    400,
                )
            else:
                return (
                    jsonify(
                        {"message": f"Deleted category {category}", "result": result}
                    ),
                    200,
                )
        except Exception as e:
            return jsonify({"message": f"Error: {e}"}), 400


if __name__ == "__main__":
    # Check if config.py and expense_tracker.db exist
    import os

    if not os.path.exists("config.py"):
        print("config.py not found. Please run init.py first.")
        exit(1)
    if not os.path.exists("expense_tracker.db"):
        print("expense_tracker.db not found. Please run init.py first.")
        exit(1)

    import config

    app.config["BASIC_AUTH_USERNAME"] = base64.b64decode(config.basic_username).decode(
        "utf-8"
    )
    app.config["BASIC_AUTH_PASSWORD"] = base64.b64decode(config.basic_password).decode(
        "utf-8"
    )
    app.run(debug=True)
