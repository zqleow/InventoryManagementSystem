# InventoryManagementSystem

The purpose of this assessment is to create an inventory management system with functions for creating, reading, and updating item records. These functions will utilize an API gateway to receive and return responses via the API gateway. The framework that I have chosen to work with is FastAPI, a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints. 

As FastAPI doesn’t contain any built-in development server, we need Uvicorn.The main thing we need to run a FastAPI application in a remote server machine is an ASGI server program like Uvicorn. The APIs implemented are designed with MySQL as the database. Logging has also been implemented to track and debug issues that may occur which is especially critical for a backend system.

## Installation

The dependencies of the program are already documented in requirements.txt. Please install the dependencies by executing pip install requirements.txt.

```sh
pip install -r requirements.txt
```

### Setting up MySQL Database

Run the following command in the directory where Dockerfile is located (main directory):

```sh
docker build -t db-mysql-image . --load  && docker run -d --name db-mysql-container -p 127.0.0.1:3306:3306 db-mysql-image
```

This command runs a detached (-d) Docker container from the Docker image. It maps port 3306 of the container to port 3306 on localhost (127.0.0.1:3306:3306).

By specifying 127.0.0.1 before the port numbers, the container's port is only accessible from the localhost interface. This means that connections to port 3306 on your localhost will be forwarded to port 3306 on the Docker container.

Now that Docker container should be running on localhost, and we can connect to it using localhost and port 3306.

We can now use the MySQL CLI or any SQL client of your preference to connect to the database. The credentials to login to the database can be found in the Dockerfile.

```sh
MYSQL_USER=db_app_user 
MYSQL_PASSWORD=admin_user 
```

### Running the Application

After the dependencies of the program are installed, to run the FastAPI application, use the following command:

```sh
uvicorn app:app
```

This will start the FastAPI application and automatically reload it when changes are made to the code.

You can then access the API at `http://localhost:8000` (Please use this command: uvicorn app:app --port 8000 if the app does not run on port 8000) in your web browser or using tools like cURL or Postman.

### Running Unit Tests

To run the unit tests written in pytest, use the following command from the main directory:

```sh
python -m pytest unit_test/ -vv -s
```

### API Endpoints

#### 1. Create Item

-   **Method**: POST
-   **URL**: `/items/`
-   **Description**: This endpoint allows users to create a new item in the database.
-   **Request Body**:
    -   `item` (dictionary): Details of the item to be created. (Refer to Task 1 in assessment)
-   **Response**:
    -   Return the server-assigned ID (UUID) for the newly created item.
-   **Response Codes**:
    -   200: Item created successfully.
    -   500: Internal server error or database error.

#### 2. Query Items Within Date Range

-   **Method**: GET
-   **URL**: `/items/`
-   **Description**: This endpoint retrieves items from the database that fall within the specified date range.
-   **Query Parameters**:
    -   `date_range` (DateRangeInput): Specifies the start and end dates of the date range. (Refer to Task 2 in assessment)
-   **Response**:
    -   List of items with details. The response include an additional field indicating the total price of all the items.
-   **Response Codes**:
    -   200: Items retrieved successfully.
    -   500: Internal server error or database error.

#### 3. Query Items By Category

-   **Method**: GET
-   **URL**: `/items-by-category/`
-   **Description**: This endpoint retrieves items from the database based on the specified category.
-   **Query Parameters**:
    -   `category` (str): Specifies the category of items to retrieve. If set to "all", retrieves items from all categories.
-   **Response**:
    -   Return items by category along with the total price included.
-   **Response Codes**:
    -   200: Items retrieved successfully.
    -   500: Internal server error or database error.
-   **Response Codes**:
    -   200: Item created successfully.
    -   500: Internal server error or database error.
