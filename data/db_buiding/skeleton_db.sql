
CREATE TABLE [currency] (
  [name] TEXT PRIMARY KEY,
  [USD] REAL NOT NULL
);

CREATE TABLE [site] (
  [site_code] TEXT PRIMARY KEY,
  [name] TEXT UNIQUE NOT NULL,  
  [premium_per_t] REAL NOT NULL,
  [currency] TEXT NOT NULL,
  FOREIGN KEY ([currency]) REFERENCES [currency] ([name])
);

CREATE TABLE [composition] (
  [composition_id] TEXT PRIMARY KEY,
  [Si] REAL NOT NULL,
  [Fe] REAL NOT NULL,
  [Cu] REAL NOT NULL,
  [Mn] REAL NOT NULL,
  [Mg] REAL NOT NULL,
  [Cr] REAL NOT NULL,
  [Zn] REAL NOT NULL,
  [Ti] REAL NOT NULL
);

CREATE TABLE [alloy] (
  [alloy_id] TEXT PRIMARY KEY,
  [site] INTEGER NOT NULL,
  [name] TEXT UNIQUE NOT NULL,
  [composition_id] INTEGER NOT NULL,
  FOREIGN KEY ([site]) REFERENCES [site] ([code]),
  FOREIGN KEY ([composition_id]) REFERENCES [composition] ([composition_id])
);

CREATE TABLE [raw_material] (
  [raw_material_id] TEST PRIMARY KEY,
  [name] TEXT NOT NULL,
  [composition_id] INTEGER NOT NULL,
  [cost_per_t] REAL NOT NULL,
  [premium] BOOLEAN NOT NULL,
  [currency] TEXT NOT NULL,
  [t_CO2_per_t] REAL NOT NULL,
  FOREIGN KEY ([currency]) REFERENCES [currency] ([name]),
  FOREIGN KEY ([composition_id]) REFERENCES [composition] ([composition_id])
);

CREATE TABLE [recycling_cost] (
  [recycling_cost_id] INTEGER PRIMARY KEY,
  [site] TEXT NOT NULL,
  [shape_type_id] INTEGER,
  [shape_name] TEXT NOT NULL,
  [recycling_cost_per_t] REAL NOT NULL,
  FOREIGN KEY ([site]) REFERENCES [site] ([code])
);

CREATE TABLE [scrap] (
  [scrap_id] TEXT PRIMARY KEY,
  [name] TEXT NOT NULL,
  [composition_id] TEXT NOT NULL,
  [shape_type_id] INTEGER,
  [scrap_purchasing_cost_per_t] REAL,
  [transportation_cost_per_t] REAL,
  [currency] INTEGER NOT NULL,
  FOREIGN KEY ([composition_id]) REFERENCES [composition] ([composition_id]),
  FOREIGN KEY ([shape_type_id]) REFERENCES [shape_type] ([shape_type_id]),
  FOREIGN KEY ([currency]) REFERENCES [currency] ([name])
);

CREATE TABLE [shape_type] (
  [shape_type_id] INTEGER PRIMARY KEY,
  [name] TEXT NOT NULL UNIQUE
);