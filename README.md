# finances
This project is a simple web application for managing expenses. It's built using Python's Flask.

## Getting Started

Follow these steps to get the project up and running on your local machine:

1. Clone this repository:
    ```bash
    git clone https://github.com/Njoyable/finances your_name
    ```

2. Navigate to the project directory:

    ```bash
    cd your_name
    ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```
4. Initialize the environment:

    ```bash
    python init.py
    ```

4. Start the server:

    ```bash
    python app.py
    ```

5. Open your web browser and navigate to `http://localhost:5000`.

## Routes

Here's a list of all routes served by the application and what they do:

- `GET /`: This is the home page of the application.
- `POST /category/:name`: This route adds a new category with the given name.
- `DELETE /category/:name`: This route deletes the category with the given name.
- `POST /expense`: This route adds a new expense with given category, name, amount and date
- `DELETE /expense/:id`: Thhis route deletes the expense with the given id


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.