CREATE TABLE [site] (
  [site_id] INTEGER PRIMARY KEY,
  [site_code] TEXT NOT NULL,
  [name] TEXT UNIQUE NOT NULL,
  [premium_per_t] REAL NOT NULL,
  [currency] TEXT NOT NULL,
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
  FOREIGN KEY ([site_alloys]) REFERENCES [site] ([site_code])
);

CREATE TABLE [raw_material] (
  [alloy_compo_id] INTEGER PRIMARY KEY,
  [alloy_id] INTEGER NOT NULL,
  [compo_id] INTEGER NOT NULL,
  [alloy_compo_type_id] INTEGER NOT NULL,
  FOREIGN KEY ([alloy_id]) REFERENCES [alloy] ([alloy_id]),
  FOREIGN KEY ([compo_id]) REFERENCES [compo] ([compo_id]),
  FOREIGN KEY ([alloy_compo_type_id]) REFERENCES [alloy_compo_type] ([alloy_compo_type_id])
);

CREATE TABLE [category] (
  [category_id] INTEGER PRIMARY KEY,
  [name] TEXT NOT NULL
);

CREATE TABLE [inventory] (
  [inventory_id] INTEGER PRIMARY KEY,
  [category_id] INTEGER NOT NULL,
  [name] TEXT NOT NULL,
  [quantity] float NOT NULL,
  [cost] float NOT NULL,
  [compo_id] INTEGER NOT NULL,
  FOREIGN KEY ([category_id]) REFERENCES [category] ([category_id]),
  FOREIGN KEY ([compo_id]) REFERENCES [compo] ([compo_id])
);

CREATE TABLE [cast] (
  [cast_id] INTEGER PRIMARY KEY,
  [step] INTEGER NOT NULL,
  [alloy_id] INTEGER NOT NULL,
  [quantity] INTEGER NOT NULL,
  [compo_id] INTEGER NOT NULL,
  FOREIGN KEY ([alloy_id]) REFERENCES [alloy] ([alloy_id]),
  FOREIGN KEY ([compo_id]) REFERENCES [compo] ([compo_id])
);

CREATE TABLE [cast_content] (
  [cast_content_id] INTEGER PRIMARY KEY,
  [cast_id] INTEGER NOT NULL,
  [inventory_id] INTEGER NOT NULL,
  [quantity] FLOAT NOT NULL,
  FOREIGN KEY ([cast_id]) REFERENCES [cast] ([cast_id]),
  FOREIGN KEY ([inventory_id]) REFERENCES [inventory] ([inventory_id])
);

CREATE TABLE [inventory_snapshot] (
  [inventory_snapshot_id] INTEGER PRIMARY KEY,
  [before_step] INTEGER NOT NULL
);

CREATE TABLE [inventory_snapshot_content] (
  [inventory_snapshot_content_id] INTEGER PRIMARY KEY,
  [inventory_snapshot_id] INTEGER NOT NULL,
  [inventory_id] INTEGER NOT NULL,
  [quantity] FLOAT NOT NULL,
  FOREIGN KEY ([inventory_snapshot_id]) REFERENCES [inventory_snapshot] ([inventory_snapshot_id]),
  FOREIGN KEY ([inventory_id]) REFERENCES [inventory] ([inventory_id])
);
