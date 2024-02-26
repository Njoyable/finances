import duckdb

# Initialize DuckDB connection
with duckdb.connect(database='expense_tracker.db', read_only=False) as connection:

    # Create categories table
    connection.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER primary key,
        category_name VARCHAR
    )
    """)

    connection.execute("CREATE SEQUENCE IF NOT EXISTS categories_id_seq START 42069 INCREMENT 1 MINVALUE 42069")

    # Create expenses table
    connection.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER primary key,
        name VARCHAR,
        amount FLOAT,
        date DATE,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    """)

    connection.execute("CREATE SEQUENCE IF NOT EXISTS expenses_id_seq START 42069 INCREMENT 1 MINVALUE 42069")

    # Insert some default categories
    connection.execute("INSERT INTO categories VALUES (nextval('categories_id_seq'), 'Food')")
    connection.execute("INSERT INTO categories VALUES (nextval('categories_id_seq'), 'Rent')")
    connection.execute("INSERT INTO categories VALUES (nextval('categories_id_seq'), 'Transportation')")
    connection.execute("INSERT INTO categories VALUES (nextval('categories_id_seq'), 'Entertainment')")
