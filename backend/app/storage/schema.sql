CREATE TABLE IF NOT EXISTS watermarks (
    watermark_id TEXT PRIMARY KEY,
    image_hash   TEXT NOT NULL,
    owner_id     TEXT NOT NULL,
    strength     INTEGER NOT NULL,
    total_bits   INTEGER NOT NULL,
    created_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_watermarks_image_hash
    ON watermarks (image_hash);

CREATE INDEX IF NOT EXISTS idx_watermarks_owner_id
    ON watermarks (owner_id);
