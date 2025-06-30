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
        pass

    def get_raw_materials(self):
        """
        returns the list of all raw material names.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT alloy_id FROM raw_material")
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
            "SELECT t_CO2_per_t FROM raw_material WHERE raw_material_id = {id_raw_material}",
            (id_raw_material,)
        )
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise ValueError("Raw material not found")
        return float(row[0])
    
    def get_co2_raw_materials():
        pass

    def get_co2_scrap(self, id_scrap):
        """
        returns:
            float: CO2 emissions per ton of external scrap.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT t_CO2_per_t FROM external_scrap WHERE external_scrap_id = {id_scrap}",
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
            list[float]: list of proportions of each element in the alloy, in the order of self.elements.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        ## elements = self.get_alloy_elements() 'Al, Fe, Si' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        query = f"SELECT {elements} FROM alloy WHERE alloy_id = {id_alloy}"
        cursor.execute(query, (id_alloy,))
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise ValueError("Alloy not found")
        return list(row)
    
    def get_composition_scrap(self, id_scrap):
        """
        returns:
            list[float]: list of proportions of each element in the scrap in the order of self.elements.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        ## elements = self.get_alloy_elements() 'Al, Fe, Si' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        query = f"SELECT {elements} FROM external_scrap WHERE external_scrap_id = {id_scrap} "
        cursor.execute(query, (id_scrap,))
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise ValueError("Scrap not found")
        return list(row)
    
    def get_composition_raw_material(self, id_raw_material):
        """
        returns:
            list[float]: list of proportions of each element in the raw material in the order of self.elements.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        ## elements = self.get_alloy_elements() 'Al, Fe, Si' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        query = f"SELECT {elements} FROM raw_material WHERE raw_material_id = {id_raw_material}"
        cursor.execute(query, (id_raw_material,))
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise ValueError("Raw material not found")
        return list(row)
    
    def get_cost_scrap(self, id_scrap):
        pass

    def get_cost_raw_materials(self, id_raw_material):
        pass


    #def get_cost_raw_materials(self, id_raw_material):
        """
        returns the cost of a raw material in USD.
            float: Cost in USD.
        """
        conn = self.get_connection()
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
    
    


    

    








