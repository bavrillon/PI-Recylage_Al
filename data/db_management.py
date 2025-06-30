import sqlite3

DB_PATH = "data.db"

def get_connection() :
    """
    open a connection to the SQlite data.db
    returns:
        SQlite connection object
    """
    return sqlite3.connect(DB_PATH)


def get_alloy_elements():
    """
    retrieves the SI, Fe, CU, Mn, Mg, Zn, Ti columns from the table alloy"
    returns:
        list[dict]
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = (
        "SELECT SI, Fe, CU, Mn, Mg, Zn, Ti FROM alloy"
    )
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = ["SI", "Fe", "Cu", "Mn", "Mg", "Cr", "Zn", "Ti"]
    result = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return result


def get_raw_materials_site(id_site):
    """
    returns:
        list[str]: list of all raw material names.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM raw_material")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_cost_raw_materials(id_site, id_raw_material):
    """
    returns the cost of a raw material in USD for a given site
    returns:
        float : cost of the raw material in USD
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cost_by_t, currency FROM raw_material WHERE name = ?",
        (id_raw_material,)
    )
    row = cursor.fetchone()
    if row is None:
        conn.close()
        raise ValueError("Raw material not found")
    cost, currency = row

    if currency == "USD":
        rate = 1.0
    else:
        cursor.execute(
            "SELECT USD FROM currency WHERE currency_name = ?",
            (currency,)
        )
        rate_row = cursor.fetchone()
        if rate_row is None:
            conn.close()
            raise ValueError("Currency not found")
        rate = float(rate_row[0])
    conn.close()
    return float(cost) / rate