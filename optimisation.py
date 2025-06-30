# La db doit fournir le nb d'élément dans la compostion nb_elements

import pulp

composition_elements = ['Si','Fe','Cu']
nb_elements = len(composition_elements) #purs

def optimise_co2(id_site, id_alloy, id_scrap):
    co2_raw_materials_site = get_co2_raw_materials_site(id_site)    # List of the co2/t of the raw materials of the site
    co2_raw_materials_and_scrap = co2_raw_materials_site.append(get_co2_scrap(id_scrap))    # List of the co2/t of the raw materials of the site + selected scrap
    raw_materials_site = get_raw_materials_site(id_site)    # List of the ID of the raw materials of the site
    composition_ids = raw_materials_site.append(id_scrap)   # List of the ID of the raw materials + the scrap to be mixed
    compostion_alloy_wished = get_composition_alloy(id_alloy)   

    # Optimisation pb
    composition = pulp.LpVariable.dicts("calculed composition", composition_ids, cat='Continuous', lowBound=0, upBound=1)
    problem = pulp.LpProblem(name='optimise_co2', sense=LpMinimize)
    problem += pulp.lpSum([composition[i]*co2_raw_materials_and_scrap[j] for (i,j) in enumerate(composition_ids)])  # i = ID (raw material or scrap) and j = int
    for k in nb_elements :  # On parcourt les éléments de la composition, pour respecter la contrainte de l'alliage
        composition_raw_materials_and_scrap = [get_composition_raw_material(id_raw_mat) for id_raw_mat in raw_materials_site].append(get_composition_scrap(id_scrap)) # Composition in different elements of the raw materials + the scrap
                                                                                                                                                                        #  Ligne = raw material / scrap.  Colonne = Composition in different elements
        problem += (lpSum([composition[i]*composition_raw_materials_and_scrap[j][k] for (i,j) in enumerate(composition_ids]) == compostion_alloy_wished[k])
    problem.solve()
    
    optimised_composition = [composition[i].varValue for i in composition_ids]
    return(optimised_composition)

def optimise_cost(id_alloy, scrap?):
    pass

optimise_co2(id_alloy, scrap?)
optimise_raw_material(id_alloy, scrap?)



def get_raw_materials_site(id_site):
    db = sqlite3.connect('data/data.db')
    cursor = db.cursor()
    request = "SELECT id_raw_material FROM raw_materials WHERE site...."
    cursor.execute(request)
    rows = cursor.fetchall()
    # suite...
    conn.close()