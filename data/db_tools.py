import sqlite3
from os import path
import pulp
from typing import List, Any, Optional


class Database:
    def __init__(self, file_name: str = "data.db"):
        """
        Initalize the DataBase object and load elements.
        """
        self.file_name = path.join(path.dirname(__file__), file_name)
        self.elements = self.get_elements()
        self.nb_elements = len(self.elements)

    # =============================================================================
    # Connection management and data retrieval
    # =============================================================================

    def get_connection(self) -> sqlite3.Connection:
        """
        Create and return a SQLite connection object.
        """
        return sqlite3.connect(self.file_name)

    def get_elements(self) -> List[str]:
        """
        Get the list of element names from the composition table.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(composition)")
        columns_info = cursor.fetchall()
        exclude = {"composition_id"}
        elements = [col[1] for col in columns_info if col[1] not in exclude]
        conn.close()
        return elements

    def get_raw_materials_id(self) -> List[str]:
        """
        Returns the list of all raw material IDs.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT raw_material_id FROM raw_material")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def get_composition_alloy(self, id_alloy: int) -> List[float]:
        """
        Get the list of proportions of each element in the alloy, in the order of self.elements.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT composition_id FROM alloy WHERE alloy_id = ?", (id_alloy,)
        )
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

    def get_composition_raw_material(
        self, id_raw_material: int
    ) -> List[float]:
        """
        Get the list of proportions of each element in the raw material in the order of self.elements.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT composition_id FROM raw_material WHERE raw_material_id = ?",
            (id_raw_material,),
        )
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

    def get_composition_scrap(self, id_scrap: int) -> List[float]:
        """
        Get the list of proportions of each element in the scrap in the order of self.elements.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT composition_id FROM scrap WHERE scrap_id = ?", (id_scrap,)
        )
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

    def get_raw_materials_name(self):
        """
        Get the list of all raw material names.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM raw_material")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    # ======================================================================
    # Cost and Emissions Calculations
    # ======================================================================

    def get_co2_raw_material(self, id_raw_material: int) -> float:
        """
        Get CO2 emissions per ton of a raw material.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT t_CO2_per_t FROM raw_material WHERE raw_material_id = ?",
            (id_raw_material,),
        )
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise ValueError("Raw material not found")
        return float(row[0])

    def get_co2_raw_materials(self) -> List[float]:
        """
        Get the list of CO2 emissions per ton for all raw materials.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT t_CO2_per_t FROM raw_material")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def get_cost_raw_material(
        self, id_site: str, id_raw_material: int
    ) -> float:
        """
        Get the cost of a raw material in USD for a given site.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT raw_material.cost_per_t, raw_material.currency, raw_material.premium, site.premium_per_t
            FROM raw_material, site
            WHERE site.site_code = ? AND raw_material.raw_material_id = ?
            """,
            (id_site, id_raw_material),
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
                "SELECT USD FROM currency WHERE name = ?", (currency,)
            )
            rate_row = cursor.fetchone()
            if rate_row is None:
                conn.close()
                raise ValueError("Currency not found")
            rate = float(rate_row[0])
        conn.close()
        return float(total_cost) / rate

    def get_cost_raw_materials(self, id_site: str) -> List[float]:
        """
        Get the list of costs in USD for all raw materials for a given site.
        """
        raw_material_ids = self.get_raw_materials_id()
        costs = []
        for id_raw_material in raw_material_ids:
            cost = self.get_cost_raw_material(id_site, id_raw_material)
            costs.append(cost)
        return costs

    def get_cost_scrap(self, id_site: str, id_scrap: str) -> float:
        """
        Get the cost of a scrap in USD for a given site.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT scrap_purchasing_cost_per_t, shape_type_id, currency FROM scrap WHERE scrap_id = ?",
            (id_scrap,),
        )
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Scrap not found")
        cost, shape_type_id, currency = row

        cursor.execute(
            "SELECT recycling_cost_per_t FROM recycling_cost WHERE site_code = ? AND shape_type_id = ?",
            (id_site, shape_type_id),
        )

        recycling_row = cursor.fetchone()
        if recycling_row is None:
            conn.close()
            raise ValueError(
                "Recycling cost not found for this site and shape type"
            )
        recycling_cost = recycling_row[0]
        total_cost = cost + recycling_cost

        if currency == "USD":
            rate = 1.0
        else:
            cursor.execute(
                "SELECT USD FROM currency WHERE name = ?", (currency,)
            )
            rate_row = cursor.fetchone()
            if rate_row is None:
                conn.close()
                raise ValueError("Currency not found")
            rate = float(rate_row[0])
        conn.close()
        return float(total_cost) / rate

    def get_total_co2(self, composition: List[float]) -> list[float]:
        """
        Calculate CO2 contribution for each raw material and the total.
        """
        raw_materials = self.get_raw_materials_id()
        # If scrap fraction is included, drop the last element
        if len(composition) != len(raw_materials):
            composition = composition[:-1]

        co2_values = []
        total_co2 = 0.0
        for i, amount in enumerate(composition):
            raw_material_id = raw_materials[i]
            co2 = self.get_co2_raw_material(raw_material_id)
            co2_amount = amount * co2
            co2_values.append(co2_amount)
            total_co2 += co2_amount

        co2_values.append(total_co2)
        return co2_values

    def get_total_cost(
        self,
        composition: list[float],
        site_code: str,
        id_scrap: Optional[int] = None,
    ) -> List[float]:
        """
        Calculate cost contribution for each raw material and optional scrap,
        returning individual contributions plus total cost.
        """
        raw_materials = self.get_raw_materials_id()

        cost_values = []
        total_cost = 0.0

        if id_scrap != None:
            composition_bis = composition[:-1]
        else:
            composition_bis = composition
        for i, amount in enumerate(composition_bis):
            raw_material_id = raw_materials[i]
            cost = self.get_cost_raw_material(site_code, raw_material_id)
            cost_amount = amount * cost
            cost_values.append(cost_amount)
            total_cost += cost_amount

        if id_scrap != None:
            cost_values.append(
                self.get_cost_scrap(site_code, id_scrap) * composition[-1]
            )
            total_cost += cost_values[-1]

        cost_values.append(total_cost)
        return cost_values

    # ======================================================================
    #                           OPTIMISATION
    # ======================================================================

    def optimise_co2_with_scrap(
        self, id_site: str, id_alloy: str, id_scrap: str
    ) -> list:
        """
        Minimize CO2 emissions for a given alloy and site using raw materials
        and one scrap. Returns the optimal composition.
        """
        raw_materials = (
            self.get_raw_materials_id()
        )  # List of the ID of the raw materials
        composition_ids = raw_materials + [
            id_scrap
        ]  # List of the ID of the raw materials + the scrap to be mixed
        composition_alloy_wished = self.get_composition_alloy(id_alloy)

        # Optimisation pb
        composition = pulp.LpVariable.dicts(
            "calculed composition",
            composition_ids,
            cat="Continuous",
            lowBound=0,
            upBound=1,
        )
        problem = pulp.LpProblem(
            name="optimise_co2_with_scrap", sense=pulp.LpMinimize
        )
        problem += pulp.lpSum(
            [
                composition[id] * self.get_co2_raw_material(id)
                for id in raw_materials
            ]
        )  # i = ID (raw material only) and j = int

        # Constraint sum compositions = 1 :
        problem += pulp.lpSum([composition[i] for i in composition_ids]) == 1
        # Constraint of composition of the alloy :
        for k in range(self.nb_elements):
            problem += (
                pulp.lpSum(
                    [
                        composition[id]
                        * self.get_composition_raw_material(id)[k]
                        for id in raw_materials
                    ]
                )
                + composition[id_scrap]
                * self.get_composition_scrap(id_scrap)[k]
                == composition_alloy_wished[k]
            )
        problem.writeLP("resultat-optim.lp")
        problem.solve()
        if pulp.LpStatus[problem.status] != "Optimal":
            raise ValueError(
                f"Composition optimization failed. Reason = {pulp.LpStatus[problem.status]}"
            )

        optimised_composition = [
            composition[i].varValue for i in composition_ids
        ]
        return optimised_composition

    def optimise_co2_without_scrap(self, id_site: str, id_alloy: str) -> list:
        """
        Minimize CO2 emissions for a given alloy and site using only raw
        materials. Returns the optimal composition.
        """
        raw_materials = (
            self.get_raw_materials_id()
        )  # List of the ID of the raw materials
        composition_ids = raw_materials  # List of the ID of the raw materials + the scrap to be mixed
        composition_alloy_wished = self.get_composition_alloy(id_alloy)

        # Optimisation pb
        composition = pulp.LpVariable.dicts(
            "calculed composition",
            composition_ids,
            cat="Continuous",
            lowBound=0,
            upBound=1,
        )
        problem = pulp.LpProblem(
            name="optimise_co2_without_scrap", sense=pulp.LpMinimize
        )
        problem += pulp.lpSum(
            [
                composition[id] * self.get_co2_raw_material(id)
                for id in raw_materials
            ]
        )  # i = ID raw material  and j = int

        # Constraint sum compositions = 1 :
        problem += pulp.lpSum([composition[i] for i in composition_ids]) == 1
        # Constraint of composition of the alloy :
        for k in range(self.nb_elements):
            problem += (
                pulp.lpSum(
                    [
                        composition[id]
                        * self.get_composition_raw_material(id)[k]
                        for id in raw_materials
                    ]
                )
                == composition_alloy_wished[k]
            )

        problem.solve()
        if pulp.LpStatus[problem.status] != "Optimal":
            raise ValueError(
                f"Composition optimization failed. Reason = {pulp.LpStatus[problem.status]}"
            )

        optimised_composition = [
            composition[i].varValue for i in composition_ids
        ]
        return optimised_composition

    def optimise_cost_with_scrap(
        self, id_site: str, id_alloy: str, id_scrap: str
    ) -> list:
        """
        Minimize cost for a given alloy and site using raw materials and one
        scrap. Returns the optimal composition.
        """
        raw_materials = (
            self.get_raw_materials_id()
        )  # List of the ID of the raw materials
        composition_ids = raw_materials + [
            id_scrap
        ]  # List of the ID of the raw materials + the scrap to be mixed
        composition_alloy_wished = self.get_composition_alloy(id_alloy)

        # Optimisation pb
        composition = pulp.LpVariable.dicts(
            "calculed composition",
            composition_ids,
            cat="Continuous",
            lowBound=0,
            upBound=1,
        )
        problem = pulp.LpProblem(
            name="optimise_cost_with_scrap", sense=pulp.LpMinimize
        )
        problem += pulp.lpSum(
            [
                composition[id] * self.get_cost_raw_material(id_site, id)
                for id in raw_materials
            ]
        ) + composition[id_scrap] * self.get_cost_scrap(
            id_site, id_scrap
        )  # i = ID (raw material or scrap) and j = int

        # Constraint sum compositions = 1 :
        problem += pulp.lpSum([composition[i] for i in composition_ids]) == 1
        # Constraint of composition of the alloy :
        for k in range(self.nb_elements):
            problem += (
                pulp.lpSum(
                    [
                        composition[id]
                        * self.get_composition_raw_material(id)[k]
                        for id in raw_materials
                    ]
                )
                + composition[id_scrap]
                * self.get_composition_scrap(id_scrap)[k]
                == composition_alloy_wished[k]
            )

        problem.solve()
        if pulp.LpStatus[problem.status] != "Optimal":
            raise ValueError(
                f"Composition optimization failed. Reason = {pulp.LpStatus[problem.status]}"
            )

        optimised_composition = [
            composition[i].varValue for i in composition_ids
        ]
        return optimised_composition

    def optimise_cost_without_scrap(self, id_site: str, id_alloy: str) -> list:
        """
        Minimize cost for a given alloy and site using only raw materials.
        Returns the optimal composition.
        """
        cost_raw_materials = self.get_cost_raw_materials(
            id_site
        )  # List of the cost of the raw materials
        raw_materials = (
            self.get_raw_materials_id()
        )  # List of the ID of the raw materials
        composition_ids = raw_materials  # List of the ID of the raw materials + the scrap to be mixed
        composition_alloy_wished = self.get_composition_alloy(id_alloy)

        # Optimisation pb
        composition = pulp.LpVariable.dicts(
            "calculed composition",
            composition_ids,
            cat="Continuous",
            lowBound=0,
            upBound=1,
        )
        problem = pulp.LpProblem(
            name="optimise_cost_without_scrap", sense=pulp.LpMinimize
        )
        problem += pulp.lpSum(
            [
                composition[i] * cost_raw_materials[j]
                for (j, i) in enumerate(composition_ids)
            ]
        )  # i = ID raw material  and j = int

        # Constraint sum compositions = 1 :
        problem += pulp.lpSum([composition[i] for i in composition_ids]) == 1
        # Constraint of composition of the alloy :
        for k in range(self.nb_elements):
            problem += (
                pulp.lpSum(
                    [
                        composition[id]
                        * self.get_composition_raw_material(id)[k]
                        for id in raw_materials
                    ]
                )
                == composition_alloy_wished[k]
            )

        problem.solve()
        if pulp.LpStatus[problem.status] != "Optimal":
            raise ValueError(
                f"Composition optimization failed. Reason = {pulp.LpStatus[problem.status]}"
            )

        optimised_composition = [
            composition[i].varValue for i in composition_ids
        ]
        return optimised_composition

    def optimise_utilisation_scrap(
        self, id_site: str, id_alloy: str, id_scrap: str
    ) -> list:
        """
        Maximize the use of a given scrap for a given alloy and site while
        respecting the alloy composition. Returns the optimal composition.
        """
        raw_materials = (
            self.get_raw_materials_id()
        )  # List of the ID of the raw materials
        composition_ids = raw_materials + [
            id_scrap
        ]  # List of the ID of the raw materials + the scrap to be mixed
        composition_alloy_wished = self.get_composition_alloy(id_alloy)

        # Optimisation pb
        composition = pulp.LpVariable.dicts(
            "calculed composition",
            composition_ids,
            cat="Continuous",
            lowBound=0,
            upBound=1,
        )
        problem = pulp.LpProblem(
            name="optimise_utilisation_scrap", sense=pulp.LpMaximize
        )
        problem += composition[
            id_scrap
        ]  # Maximize the proportion of the scrap

        # Constraint sum compositions = 1 :
        problem += pulp.lpSum([composition[i] for i in composition_ids]) == 1
        # Constraint of composition of the alloy :
        for k in range(self.nb_elements):
            problem += (
                pulp.lpSum(
                    [
                        composition[id]
                        * self.get_composition_raw_material(id)[k]
                        for id in raw_materials
                    ]
                )
                + composition[id_scrap]
                * self.get_composition_scrap(id_scrap)[k]
            ) == composition_alloy_wished[k]

        problem.solve()
        if pulp.LpStatus[problem.status] != "Optimal":
            raise ValueError(
                f"Composition optimization failed. Reason = {pulp.LpStatus[problem.status]}"
            )

        optimised_composition = [
            composition[i].varValue for i in composition_ids
        ]
        print(composition_alloy_wished)
        return optimised_composition
