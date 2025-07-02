import sqlite3
from os import path
import pulp

class Database:
    def __init__(self, file_name="data.db"):
        self.file_name = path.join(path.dirname(__file__), file_name)
        self.elements = self.get_elements()
        self.nb_elements = len(self.elements)

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

    def get_composition_alloy(self, id_alloy):
        """
        returns:
            list[float]: list of proportions of each element in the thing in the order of self.elements.
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
    
    def get_composition_raw_material(self, id_raw_material):
        """
        returns:
            list[float]: list of proportions of each element in the raw material in the order of self.elements.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT composition_id FROM raw_material WHERE raw_material_id = ?", (id_raw_material,))
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Raw material not found")
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
        cursor.execute("SELECT composition_id FROM scrap WHERE scrap_id = ?", (id_scrap,))
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Scrap not found")
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
            SELECT raw_material.cost_per_t, raw_material.currency, raw_material.premium, site.premium_per_t
            FROM raw_material, site
            WHERE site.site_code = ? AND raw_material.raw_material_id = ?
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
        "SELECT recycling_cost_per_t FROM recycling_cost WHERE site_code = ? AND shape_type_id = ?",
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
    


    #####################################################################
    # OPTIMISATION
    #####################################################################

    def optimise_co2_with_scrap(self, id_site, id_alloy, id_scrap):
        co2_raw_materials = self.get_co2_raw_materials()    # List of the co2/t of the raw materials 
        raw_materials = self.get_raw_materials()    # List of the ID of the raw materials
        composition_ids = raw_materials + [id_scrap]   # List of the ID of the raw materials + the scrap to be mixed
        compostion_alloy_wished = self.get_composition_alloy(id_alloy)   

        # Optimisation pb
        composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
        problem = pulp.LpProblem(name='optimise_co2_with_scrap', sense=pulp.LpMinimize)
        problem += pulp.lpSum([composition[i]*co2_raw_materials[j] for (j,i) in enumerate(composition_ids[:-1])])  # i = ID (raw material only) and j = int
    
        # Constraint sum compositions = 1 :
        problem += (pulp.lpSum([composition[i] for i in composition_ids]) == 1)
        # Constraint of composition of the alloy :
        for k in range(self.nb_elements) :  
            composition_raw_materials_and_scrap = [self.get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials] + [self.get_composition_scrap(id_scrap)] # Composition in different elements of the raw materials + the scrap
                                                                                                                                                                        #  Ligne = raw material / scrap.  Colonne = Composition in different elements
            problem += pulp.lpSum([composition[i]*composition_raw_materials_and_scrap[j][k] for (j,i) in enumerate(composition_ids)]) == compostion_alloy_wished[k]
                                
        problem.solve()
        #vérifier la cohérence du résultat ?

        optimised_composition = [composition[i].varValue for i in composition_ids]
        return(optimised_composition)
    
    def optimise_co2_without_scrap(self, id_site, id_alloy):
        co2_raw_materials = self.get_co2_raw_materials()    # List of the co2/t of the raw materials 
        raw_materials = self.get_raw_materials()    # List of the ID of the raw materials
        composition_ids = raw_materials        # List of the ID of the raw materials + the scrap to be mixed
        compostion_alloy_wished = self.get_composition_alloy(id_alloy)   

        # Optimisation pb
        composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
        problem = pulp.LpProblem(name='optimise_co2_without_scrap', sense=pulp.LpMinimize)
        problem += pulp.lpSum([composition[i]*co2_raw_materials[j] for (j,i) in enumerate(composition_ids)])  # i = ID raw material  and j = int
    
        # Constraint sum compositions = 1 :
        problem += (pulp.lpSum([composition[i] for i in composition_ids]) == 1)
        # Constraint of composition of the alloy :
        for k in range(self.nb_elements) :  
            composition_raw_materials = [self.get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials]  # Composition in different elements of the raw materials 
                                                                                                                                #  Ligne = raw material.  Colonne = Composition in different elements.
            problem += pulp.lpSum([composition[i]*composition_raw_materials[j][k] for (j,i) in enumerate(composition_ids)]) == compostion_alloy_wished[k]
    
        problem.solve()
        #vérifier la cohérence du résultat ?

        optimised_composition = [composition[i].varValue for i in composition_ids]
        return(optimised_composition)
    
    def optimise_cost_with_scrap(self, id_site, id_alloy, id_scrap):
        cost_raw_materials = self.get_cost_raw_materials(id_site)    # List of the cost of the raw materials 
        cost_raw_materials_and_scrap = cost_raw_materials + [self.get_cost_scrap(id_site, id_scrap)]    # List of the cost of the raw materials + selected scrap
        raw_materials = self.get_raw_materials()    # List of the ID of the raw materials
        composition_ids = raw_materials + [id_scrap]   # List of the ID of the raw materials + the scrap to be mixed
        compostion_alloy_wished = self.get_composition_alloy(id_alloy)   

        # Optimisation pb
        composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
        problem = pulp.LpProblem(name='optimise_cost_with_scrap', sense=pulp.LpMinimize)
        problem += pulp.lpSum([composition[i]*cost_raw_materials_and_scrap[j] for (j,i) in enumerate(composition_ids)])  # i = ID (raw material or scrap) and j = int
    
        # Constraint sum compositions = 1 :
        problem += (pulp.lpSum([composition[i] for i in composition_ids]) == 1)
        # Constraint of composition of the alloy :
        for k in range(self.nb_elements) :  
            composition_raw_materials_and_scrap = [self.get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials] + [self.get_composition_scrap(id_scrap)] # Composition in different elements of the raw materials + the scrap
                                                                                                                                                                        #  Ligne = raw material / scrap.  Colonne = Composition in different elements
            problem += pulp.lpSum([composition[i]*composition_raw_materials_and_scrap[j][k] for (j,i) in enumerate(composition_ids)]) == compostion_alloy_wished[k]
    
        problem.solve()
        #vérifier la cohérence du résultat ?
    
        optimised_composition = [composition[i].varValue for i in composition_ids]
        return(optimised_composition)
    
    def optimise_cost_without_scrap(self, id_site, id_alloy):
        cost_raw_materials = self.get_cost_raw_materials(id_site)    # List of the cost of the raw materials 
        raw_materials = self.get_raw_materials()    # List of the ID of the raw materials
        composition_ids = raw_materials        # List of the ID of the raw materials + the scrap to be mixed
        compostion_alloy_wished = self.get_composition_alloy(id_alloy)   

        # Optimisation pb
        composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
        problem = pulp.LpProblem(name='optimise_cost_without_scrap', sense=pulp.LpMinimize)
        problem += pulp.lpSum([composition[i]*cost_raw_materials[j] for (j,i) in enumerate(composition_ids)])  # i = ID raw material  and j = int
    
        # Constraint sum compositions = 1 :
        problem += (pulp.lpSum([composition[i] for i in composition_ids]) == 1)
        # Constraint of composition of the alloy :
        for k in range(self.nb_elements) :  
            composition_raw_materials = [self.get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials]  # Composition in different elements of the raw materials 
                                                                                                                                #  Ligne = raw material.  Colonne = Composition in different elements.
            problem += pulp.lpSum([composition[i]*composition_raw_materials[j][k] for (j,i) in enumerate(composition_ids)]) == compostion_alloy_wished[k]
    
        problem.solve()
        #vérifier la cohérence du résultat ?

        optimised_composition = [composition[i].varValue for i in composition_ids]
        return(optimised_composition)
    
    def optimise_utilisation_scrap(self, id_site, id_alloy, id_scrap):
        raw_materials = self.get_raw_materials()    # List of the ID of the raw materials
        composition_ids = raw_materials + [id_scrap]   # List of the ID of the raw materials + the scrap to be mixed
        compostion_alloy_wished = self.get_composition_alloy(id_alloy)   

        # Optimisation pb
        composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
        problem = pulp.LpProblem(name='optimise_utilisation_scrap', sense=pulp.LpMaximize)
        problem += composition[len(composition_ids)-1]  # Maximize the proportion of the scrap
    
        # Constraint sum compositions = 1 :
        problem += (pulp.lpSum([composition[i] for i in composition_ids]) == 1)
        # Constraint of composition of the alloy :
        for k in range(self.nb_elements) :  
            composition_raw_materials_and_scrap = [self.get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials] + [self.get_composition_scrap(id_scrap)] # Composition in different elements of the raw materials + the scrap
                                                                                                                                                                        #  Ligne = raw material / scrap.  Colonne = Composition in different elements
            problem += pulp.lpSum([composition[i]*composition_raw_materials_and_scrap[j][k] for (j,i) in enumerate(composition_ids)]) == compostion_alloy_wished[k]
    
        problem.solve()
        #vérifier la cohérence du résultat ?

        optimised_composition = [composition[i].varValue for i in composition_ids]
        return(optimised_composition)
