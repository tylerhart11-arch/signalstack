-- SignalStack local database bootstrap.
-- Application tables are created by SQLAlchemy on API startup.

CREATE SCHEMA IF NOT EXISTS reference;

COMMENT ON SCHEMA reference IS 'Reserved for future static mapping tables and metadata assets.';
