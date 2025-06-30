CREATE TABLE [site] (
  [site_id] INTEGER PRIMARY KEY,
  [site_code] TEXT NOT NULL,
  [name] TEXT UNIQUE NOT NULL,
  [premium_per_t] REAL NOT NULL,
  [currency] TEXT NOT NULL,
  FOREIGN KEY ([currency]) REFERENCES [currency] ([currency_name])
);

CREATE TABLE [alloy] (
  [alloy_id] INTEGER PRIMARY KEY,
  [site_alloys] TEXT NOT NULL,
  [alloy] TEXT UNIQUE NOT NULL,
  [Si] REAL NOT NULL,
  [Fe] REAL NOT NULL,
  [Cu] REAL NOT NULL,
  [Mn] REAL NOT NULL,
  [Mg] REAL NOT NULL,
  [Cr] REAL NOT NULL,
  [Zn] REAL NOT NULL,
  [Ti] REAL NOT NULL,
  FOREIGN KEY ([Si]) REFERENCES [raw_material]([Si]),
  FOREIGN KEY ([Fe]) REFERENCES [raw_material]([Fe]),
  FOREIGN KEY ([Cu]) REFERENCES [raw_material]([Cu]),
  FOREIGN KEY ([Mn]) REFERENCES [raw_material]([Mn]),
  FOREIGN KEY ([Mg]) REFERENCES [raw_material]([Mg]),
  FOREIGN KEY ([Cr]) REFERENCES [raw_material]([Cr]),
  FOREIGN KEY ([Zn]) REFERENCES [raw_material]([Zn]),
  FOREIGN KEY ([Ti]) REFERENCES [raw_material]([Ti]),
  FOREIGN KEY ([site_alloys]) REFERENCES [site] ([site_code])
);

CREATE TABLE [raw_material] (
  [raw_material_id] INTEGER PRIMARY KEY,
  [Si] REAL NOT NULL,
  [Fe] REAL NOT NULL,
  [Cu] REAL NOT NULL,
  [Mn] REAL NOT NULL,
  [Mg] REAL NOT NULL,
  [Cr] REAL NOT NULL,
  [Zn] REAL NOT NULL,
  [Ti] REAL NOT NULL,
  [cost_by_t] REAL NOT NULL,
  [premium] BOOLEAN NOT NULL,
  [currency] TEXT NOT NULL,
  [t_CO2/t] REAL NOT NULL,
  FOREIGN KEY ([currency]) REFERENCES [currency] ([currency_name])
);

CREATE TABLE [recycling_costs] (
  [recycling_costs_id] INTEGER PRIMARY KEY,
  [site] TEXT NOT NULL,
  [shape_name] TEXT NOT NULL,
  [recycling_cost_per_t] REAL NOT NULL,
  FOREIGN KEY ([site]) REFERENCES [site] ([site_code])
);

CREATE TABLE [currency] (
  [currency_id] INTEGER PRIMARY KEY,
  [currency_name] TEXT UNIQUE NOT NULL
  [USD] REAL NOT NULL,
);
CREATE TABLE [external_scrap] (
  [external_scrap_id] INTEGER PRIMARY KEY,
  [scrap_name] TEXT NOT NULL,
  [Si] REAL NOT NULL,
  [Fe] REAL NOT NULL,
  [Cu] REAL NOT NULL,
  [Mn] REAL NOT NULL,
  [Mg] REAL NOT NULL,
  [Cr] REAL NOT NULL,
  [Zn] REAL NOT NULL,
  [Ti] REAL NOT NULL,
  [shape] TEXT NOT NULL,
  [scrap_purchasing_cost_per_t] REAL NOT NULL,
  [transportation_cost_per_t] REAL NOT NULL,
  [currency] TEXT NOT NULL,
  FOREIGN KEY ([currency]) REFERENCES [currency] ([currency_name])
  FOREIGN KEY ([Si]) REFERENCES [raw_material]([Si]),
  FOREIGN KEY ([Fe]) REFERENCES [raw_material]([Fe]),
  FOREIGN KEY ([Cu]) REFERENCES [raw_material]([Cu]),
  FOREIGN KEY ([Mn]) REFERENCES [raw_material]([Mn]),
  FOREIGN KEY ([Mg]) REFERENCES [raw_material]([Mg]),
  FOREIGN KEY ([Cr]) REFERENCES [raw_material]([Cr]),
  FOREIGN KEY ([Zn]) REFERENCES [raw_material]([Zn]),
  FOREIGN KEY ([Ti]) REFERENCES [raw_material]([Ti]),

);

