import pulp
import data.db_management

db = data.db_management.Database("data.db")

composition_elements = db.get_elements() # ['Si','Fe','Cu',...]
nb_elements = len(composition_elements) 

def optimise_co2_with_scrap(id_site, id_alloy, id_scrap):
    co2_raw_materials = db.get_co2_raw_materials()    # List of the co2/t of the raw materials 
    raw_materials = db.get_raw_materials()    # List of the ID of the raw materials
    composition_ids = raw_materials.append(id_scrap)   # List of the ID of the raw materials + the scrap to be mixed
    compostion_alloy_wished = db.get_composition_alloy(id_alloy)   

    # Optimisation pb
    composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
    problem = pulp.LpProblem(name='optimise_co2_with_scrap', sense=LpMinimize)
    problem += pulp.lpSum([composition[i]*co2_raw_materials[j] for (j,i) in enumerate(composition_ids)[:-1]])  # i = ID (raw material only) and j = int
    
    # Constraint sum compositions = 1 :
    #problem += (pulp.lpSum([composition[i] for i in range(len(composition_ids))]) == 1)
    # Constraint of composition of the alloy :
    for k in range(len(composition_ids)) :  
        composition_raw_materials_and_scrap = [db.get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials].append(db.get_composition_scrap(id_scrap)) # Composition in different elements of the raw materials + the scrap
                                                                                                                                                                        #  Ligne = raw material / scrap.  Colonne = Composition in different elements
        problem += pulp.lpSum([composition[i]*composition_raw_materials_and_scrap[j][k] for (j,i) in enumerate(composition_ids)]) == compostion_alloy_wished[k]
                                
    problem.solve()
    #vérifier la cohérence du résultat ?

    optimised_composition = [composition[i].varValue for i in composition_ids]
    return(optimised_composition)

def optimise_co2_without_scrap(id_site, id_alloy):
    co2_raw_materials = db.get_co2_raw_materials()    # List of the co2/t of the raw materials 
    raw_materials = db.get_raw_materials()    # List of the ID of the raw materials
    composition_ids = raw_materials        # List of the ID of the raw materials + the scrap to be mixed
    compostion_alloy_wished = db.get_compositio_alloy(id_alloy)   

    # Optimisation pb
    composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
    problem = pulp.LpProblem(name='optimise_co2_without_scrap', sense=LpMinimize)
    problem += pulp.lpSum([composition[i]*co2_raw_materials[j] for (j,i) in enumerate(composition_ids)])  # i = ID raw material  and j = int
    
    # Constraint sum compositions = 1 :
    #problem += (pulp.lpSum([composition[i] for i in range(len(composition_ids))]) == 1)
    # Constraint of composition of the alloy :
    for k in range(len(composition_ids)) :  
        composition_raw_materials = [db.get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials]  # Composition in different elements of the raw materials 
                                                                                                                                #  Ligne = raw material.  Colonne = Composition in different elements.
        problem += pulp.lpSum([composition[i]*composition_raw_materials[j][k] for (j,i) in enumerate(composition_ids)]) == compostion_alloy_wished[k]
    
    problem.solve()
    #vérifier la cohérence du résultat ?

    optimised_composition = [composition[i].varValue for i in composition_ids]
    return(optimised_composition)


def optimise_cost_with_scrap(id_site, id_alloy, id_scrap):
    cost_raw_materials = db.get_cost_raw_materials(id_site)    # List of the cost of the raw materials 
    cost_raw_materials_and_scrap = cost_raw_materials.append(db.get_cost_scrap(id_site, id_scrap))    # List of the cost of the raw materials + selected scrap
    raw_materials = db.get_raw_materials()    # List of the ID of the raw materials
    composition_ids = raw_materials.append(id_scrap)   # List of the ID of the raw materials + the scrap to be mixed
    compostion_alloy_wished = db.get_composition_alloy(id_alloy)   

    # Optimisation pb
    composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
    problem = pulp.LpProblem(name='optimise_cost_with_scrap', sense=LpMinimize)
    problem += pulp.lpSum([composition[i]*cost_raw_materials_and_scrap[j] for (j,i) in enumerate(composition_ids)])  # i = ID (raw material or scrap) and j = int
    
    # Constraint sum compositions = 1 :
    #problem += (pulp.lpSum([composition[i] for i in range(len(composition_ids))]) == 1)
    # Constraint of composition of the alloy :
    for k in range(len(composition_ids)) :  
        composition_raw_materials_and_scrap = [db.get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials].append(db.get_composition_scrap(id_scrap)) # Composition in different elements of the raw materials + the scrap
                                                                                                                                                                        #  Ligne = raw material / scrap.  Colonne = Composition in different elements
        problem += pulp.lpSum([composition[i]*composition_raw_materials_and_scrap[j][k] for (j,i) in enumerate(composition_ids)]) == compostion_alloy_wished[k]
    
    problem.solve()
    #vérifier la cohérence du résultat ?
    
    optimised_composition = [composition[i].varValue for i in composition_ids]
    return(optimised_composition)


def optimise_cost_without_scrap(id_site, id_alloy):
    cost_raw_materials = db.get_cost_raw_materials(id_site)    # List of the cost of the raw materials 
    raw_materials = db.get_raw_materials()    # List of the ID of the raw materials
    composition_ids = raw_materials        # List of the ID of the raw materials + the scrap to be mixed
    compostion_alloy_wished = db.get_composition_alloy(id_alloy)   

    # Optimisation pb
    composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
    problem = pulp.LpProblem(name='optimise_cost_without_scrap', sense=LpMinimize)
    problem += pulp.lpSum([composition[i]*cost_raw_materials[j] for (j,i) in enumerate(composition_ids)])  # i = ID raw material  and j = int
    
    # Constraint sum compositions = 1 :
    #problem += (pulp.lpSum([composition[i] for i in range(len(composition_ids))]) == 1)
    # Constraint of composition of the alloy :
    for k in range(len(composition_ids)) :  
        composition_raw_materials = [db.get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials]  # Composition in different elements of the raw materials 
                                                                                                                                #  Ligne = raw material.  Colonne = Composition in different elements.
        problem += pulp.lpSum([composition[i]*composition_raw_materials[j][k] for (j,i) in enumerate(composition_ids)]) == compostion_alloy_wished[k]
    
    problem.solve()
    #vérifier la cohérence du résultat ?

    optimised_composition = [composition[i].varValue for i in composition_ids]
    return(optimised_composition)


def optimise_utilisation_scrap(id_site, id_alloy, id_scrap):
    raw_materials = db.get_raw_materials()    # List of the ID of the raw materials
    composition_ids = raw_materials.append(id_scrap)   # List of the ID of the raw materials + the scrap to be mixed
    compostion_alloy_wished = db.get_composition_alloy(id_alloy)   

    # Optimisation pb
    composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
    problem = pulp.LpProblem(name='optimise_utilisation_scrap', sense=LpMaximize)
    problem += composition[len(composition_ids)-1]  # Maximize the proportion of the scrap
    
    # Constraint sum compositions = 1 :
    #problem += (pulp.lpSum([composition[i] for i in range(len(composition_ids))]) == 1)
    # Constraint of composition of the alloy :
    for k in range(len(composition_ids)) :  
        composition_raw_materials_and_scrap = [db.get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials].append(db.get_composition_scrap(id_scrap)) # Composition in different elements of the raw materials + the scrap
                                                                                                                                                                        #  Ligne = raw material / scrap.  Colonne = Composition in different elements
        problem += pulp.lpSum([composition[i]*composition_raw_materials_and_scrap[j][k] for (j,i) in enumerate(composition_ids)]) == compostion_alloy_wished[k]
    
    problem.solve()
    #vérifier la cohérence du résultat ?

    optimised_composition = [composition[i].varValue for i in composition_ids]
    return(optimised_composition)

