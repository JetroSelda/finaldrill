from flask import Flask, make_response, jsonify, request
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "northwind"

app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


def data_fetch(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data



@app.route("/customers", methods=["GET"])
def get_customers():
    data = data_fetch("""SELECT * FROM customers""")
    return make_response(jsonify({"customers": data}), 200)


@app.route("/customers/<int:id>", methods=["GET"])
def get_customers_by_id(id):
    data = data_fetch("""SELECT * FROM customers WHERE id = {}""".format(id))
    return make_response(jsonify(data), 200)


@app.route("/customers/<int:id>/orders", methods=["GET"])
def get_orders_by_customer(id):
    data = data_fetch(
        """
        SELECT concat(customers.first_name," ",customers.last_name) as Name, 
        products.product_name, orders.order_date
        FROM customers 
        INNER JOIN orders
        ON customers.id = orders.customer_id 
        INNER JOIN order_details
        ON orders.id = order_details.order_id
        INNER JOIN products 
        ON order_details.product_id = products.id
        WHERE customers.id = {}
    """.format(id))
    
    return make_response(
        jsonify({"customer_id": id, "count": len(data), "orders": data}), 200
    )


@app.route("/customers", methods=["POST"])
def add_customer():
    cur = mysql.connection.cursor()
    info = request.get_json()
    first_name = info["first_name"]
    last_name = info["last_name"]
    cur.execute(
        """ INSERT INTO customers (first_name, last_name) VALUE (%s, %s)""",
        (first_name, last_name),
    )
    mysql.connection.commit()
    print("row(s) affected :{}".format(cur.rowcount))
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "customer added successfully", "rows_affected": rows_affected}
        ),
        201,
    )


@app.route("/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    cur = mysql.connection.cursor()
    info = request.get_json()
    first_name = info["first_name"]
    last_name = info["last_name"]
    cur.execute(
        """ UPDATE customers SET first_name = %s, last_name = %s WHERE id = %s """,
        (first_name, last_name, id),
    )
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "customer updated successfully", "rows_affected": rows_affected}
        ),
        200,
    )


@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    cur = mysql.connection.cursor()
    cur.execute(""" DELETE FROM customers where id = %s """, (id,))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "customer deleted successfully", "rows_affected": rows_affected}
        ),
        200,
    )


@app.route("/customers/format", methods=["GET"])
def get_params():
    fmt = request.args.get("id")
    foo = request.args.get("aaaa")
    return make_response(jsonify({"format": fmt, "foo": foo}), 200)


if __name__ == "__main__":
    app.run(debug=True)
