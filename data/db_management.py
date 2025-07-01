import sqlite3
import os

class Database:
    def __init__(self, file_name="data.db"):
        self.file_name = file_name
        self.elements = self.get_elements()

    def _connect(self):
        return sqlite3.connect(self.file_name)

    def get_connection(self):
        """
        returns:
        SQLite connection object
        """
        return sqlite3.connect(self.file_name)

    def get_elements(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(composition)")
        columns_info = cursor.fetchall()
        exclude = {"composition_id"}
        elements = [col[1] for col in columns_info if col[1] not in exclude]
        conn.close()
        return elements

    def get_raw_materials(self):
        """
        Returns the list of all raw material IDs.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT raw_material_id FROM raw_material")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    
    def get_co2_raw_material(self, id_raw_material):
        """
        Returns:
        float: CO2 emissions per ton of raw material.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT t_CO2_per_t FROM raw_material WHERE raw_material_id = ?",
            (id_raw_material,)
        )
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise ValueError("Raw material not found")
        return float(row[0])
    
    def get_co2_raw_materials(self):
        """
        returns:
            list[float]: list of CO2 emissions per ton for all raw materials (without column title).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT t_CO2_per_t FROM raw_material")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def get_co2_scrap(self, id_scrap):
        """
        returns:
            float: CO2 emissions per ton of external scrap.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT t_co2_per_t FROM scrap WHERE scrap_id = ?",
            (id_scrap,)
        )
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise ValueError("Scrap not found")
        return float(row[0])
    

    def get_composition_alloy(self, id_alloy):
        """
        returns:
            list[float]: list of proportions of each element in the alloy in the order of self.elements.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT composition_id FROM alloy WHERE alloy_id = ?", (id_alloy,))
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Alloy not found")
        composition_id = row[0]

        elements = self.get_elements()  
        query = f"SELECT {', '.join(elements)} FROM composition WHERE composition_id = ?"
        cursor.execute(query, (composition_id,))
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise ValueError("Composition not found")
        return list(row)
    
    def get_composition_scrap(self, id_scrap):
        """
        returns:
            list[float]: list of proportions of each element in the scrap in the order of self.elements.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT composition_id FROM alloy WHERE alloy_id = ?", (id_scrap,))
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Alloy not found")
        composition_id = row[0]
        
        elements = self.get_elements()  
        query = f"SELECT {', '.join(elements)} FROM composition WHERE composition_id = ?"
        cursor.execute(query, (composition_id,))
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise ValueError("Composition not found")
        return list(row)
    
    def get_composition_raw_material(self, id_raw_material):
        """
        returns:
            list[float]: list of proportions of each element in the scrap in the order of self.elements.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT composition_id FROM alloy WHERE alloy_id = ?", (id_raw_material,))
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Alloy not found")
        composition_id = row[0]
        
        elements = self.get_elements()  
        query = f"SELECT {', '.join(elements)} FROM composition WHERE composition_id = ?"
        cursor.execute(query, (composition_id,))
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise ValueError("Composition not found")
        return list(row)
    

    def get_cost_raw_material(self, id_site, id_raw_material):
        """
        Returns the cost of a raw material in USD for a given site.
            float: Cost in USD.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT rm.cost_per_t, rm.currency, rm.premium, s.premium_per_t
            FROM raw_material rm
            JOIN site s ON s.site_id = ?
            WHERE rm.raw_material_id = ?
            """,
            (id_site, id_raw_material)
        )
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Raw material or site not found")
        cost, currency, premium, premium_per_t = row

        total_cost = cost + (premium * premium_per_t)

        if currency == "USD":
            rate = 1.0
        else:
            cursor.execute(
                "SELECT USD FROM currency WHERE name = ?",
                (currency,)
            )
            rate_row = cursor.fetchone()
            if rate_row is None:
                conn.close()
                raise ValueError("Currency not found")
            rate = float(rate_row[0])
        conn.close()
        return float(total_cost) / rate
    
    def get_cost_raw_materials(self, id_site):
        """
        returns:
            list[float]: list of costs in USD for all raw materials for a given site.
        """
        raw_material_ids = self.get_raw_materials()  
        costs = []
        for id_raw_material in raw_material_ids:
            cost = self.get_cost_raw_material(id_site, id_raw_material)
            costs.append(cost)
        return costs

    
    def get_cost_scrap(self, id_site, id_scrap):
        """
        returns the cost of a scrap in USD for a given site.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT scrap_purchasing_cost_per_t, shape_type_id, currency FROM scrap WHERE scrap_id = ?",
            (id_scrap,)
        )
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Scrap not found")
        cost, shape_type_id, currency = row

        cursor.execute(
        "SELECT recycling_cost_per_t FROM recycling_costs WHERE site = ? AND shape_type_id = ?",
            (id_site, shape_type_id)
        )

        recycling_row = cursor.fetchone()
        if recycling_row is None:
            conn.close()
            raise ValueError("Recycling cost not found for this site and shape type")
        recycling_cost = recycling_row[0]
        total_cost = cost + recycling_cost

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
        return float(total_cost) / rate
    
