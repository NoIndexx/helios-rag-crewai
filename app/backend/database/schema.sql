PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS commodities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  slug TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_commodities_name ON commodities(name);

CREATE TABLE IF NOT EXISTS countries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  code TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_countries_code ON countries(code);

-- Link 1
CREATE TABLE IF NOT EXISTS climate_risk_by_country (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  redis_key TEXT,
  commodity_id INTEGER NOT NULL,
  country_id INTEGER NOT NULL,
  year INTEGER NOT NULL,
  hist_avg_wapr REAL,
  this_year_avg_wapr REAL,
  current_season INTEGER,
  most_recent_season INTEGER,
  upcoming_season INTEGER,
  just_ended_season INTEGER,
  UNIQUE(commodity_id, country_id, year),
  FOREIGN KEY (commodity_id) REFERENCES commodities(id),
  FOREIGN KEY (country_id) REFERENCES countries(id)
);

-- Link 2
CREATE TABLE IF NOT EXISTS risk_compared_hist_box (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  redis_key TEXT,
  commodity_id INTEGER NOT NULL,
  country_id INTEGER NOT NULL,
  hist_risk_score REAL,
  this_year_risk_score REAL,
  avg_risk_score_diff REAL,
  upcoming_year_risk_score REAL,
  risk_level TEXT,
  current_season INTEGER,
  just_ended_season INTEGER,
  upcoming_season INTEGER,
  UNIQUE(commodity_id, country_id),
  FOREIGN KEY (commodity_id) REFERENCES commodities(id),
  FOREIGN KEY (country_id) REFERENCES countries(id)
);

-- Link 3
CREATE TABLE IF NOT EXISTS risk_current_vs_hist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  redis_key TEXT,
  commodity_id INTEGER NOT NULL,
  country_id INTEGER NOT NULL,
  hist_wapr REAL,
  this_year_wapr REAL,
  std_upper REAL,
  std_lower REAL,
  date_on TEXT NOT NULL,
  season_status TEXT,
  UNIQUE(commodity_id, country_id, date_on),
  FOREIGN KEY (commodity_id) REFERENCES commodities(id),
  FOREIGN KEY (country_id) REFERENCES countries(id)
);

-- Link 4
CREATE TABLE IF NOT EXISTS risk_global_avg_max (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  redis_key TEXT,
  commodity_id INTEGER NOT NULL,
  country_id INTEGER NOT NULL,
  hist_max_wapr REAL,
  hist_avg_wapr REAL,
  year INTEGER NOT NULL,
  current_season INTEGER,
  past_season INTEGER,
  upcoming_season INTEGER,
  UNIQUE(commodity_id, country_id, year),
  FOREIGN KEY (commodity_id) REFERENCES commodities(id),
  FOREIGN KEY (country_id) REFERENCES countries(id)
);

-- Link 5
CREATE TABLE IF NOT EXISTS most_similar_year (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  redis_key TEXT,
  commodity_id INTEGER NOT NULL,
  country_id INTEGER NOT NULL,
  most_similar_growing_season_year INTEGER,
  hist_avg_wapr_of_most_similar_year REAL,
  risk_category TEXT,
  star_rating INTEGER,
  total_production REAL,
  total_area_harvested REAL,
  current_season INTEGER,
  upcoming_season INTEGER,
  just_ended_season INTEGER,
  this_growing_season_year INTEGER,
  total_yield REAL,
  total_yield_unit TEXT,
  yield_rating TEXT,
  total_production_unit TEXT,
  total_area_harvested_unit TEXT,
  UNIQUE(commodity_id, country_id, this_growing_season_year),
  FOREIGN KEY (commodity_id) REFERENCES commodities(id),
  FOREIGN KEY (country_id) REFERENCES countries(id)
);

-- Optional raw ingest log
CREATE TABLE IF NOT EXISTS raw_ingest (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  endpoint_name TEXT NOT NULL,
  redis_key TEXT,
  payload TEXT NOT NULL,
  ingested_at TEXT NOT NULL
);


