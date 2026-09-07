CREATE TABLE parts_master(
	part_id VARCHAR(20) PRIMARY KEY,
	part_family VARCHAR(50),
	criticality_class CHAR(1),
	unit_cost DECIMAL(12,2),
	lead_time_days INT,
	supplier_id_primary VARCHAR(20),
	supplier_risk_class VARCHAR(20),
	is_repairable VARCHAR(5)
);

SELECT * FROM parts_master;


CREATE TABLE supply_chain_history (
    date DATE,
    site_id VARCHAR(20),
    part_id VARCHAR(10),
    is_promotion BOOLEAN,
    consumption_qty INT,
    on_hand_qty INT,
    backorder_qty INT,
    blocked_qty INT,
    safety_stock INT,
    demand_type VARCHAR(50),
    forecast_error FLOAT,

    CONSTRAINT fk_supply_part
    FOREIGN KEY (part_id)
    REFERENCES parts_master(part_id)
);


CREATE TABLE purchase_orders (
    po_id VARCHAR(20) PRIMARY KEY,
    supplier_id VARCHAR(10),
    site_id VARCHAR(20),
    part_id VARCHAR(10),
    order_date DATE,
    promised_date DATE,
    receipt_date DATE,
    ordered_qty INT,
    received_qty INT,

    CONSTRAINT fk_po_part
    FOREIGN KEY (part_id)
    REFERENCES parts_master(part_id)
);


CREATE TABLE quality_incidents (
    incident_id VARCHAR(20) PRIMARY KEY,
    incident_date DATE,
    part_id VARCHAR(10),
    supplier_id VARCHAR(10),
    site_id VARCHAR(10),
    defect_severity VARCHAR(20),
    defect_type VARCHAR(100),
    scrap_qty INT,

    CONSTRAINT fk_quality_part
    FOREIGN KEY (part_id)
    REFERENCES parts_master(part_id)
);

SELECT * FROM parts_master LIMIT 5;

ALTER TABLE parts_master
ADD COLUMN shelf_life_days INT;

SELECT column_name
FROM information_schema.columns
WHERE table_name='parts_master';


--check if all parts IDs exists
SELECT COUNT(*)
FROM supply_chain_history s
LEFT JOIN parts_master p
ON s.part_id = p.part_id
WHERE p.part_id IS NULL;

ALTER TABLE purchase_orders
ADD COLUMN delivery_delay_days INT,
ADD COLUMN delivery_status VARCHAR(20);\

UPDATE purchase_orders
SET delivery_delay_days = receipt_date - promised_date;

UPDATE purchase_orders
SET delivery_status =
CASE
    WHEN delivery_delay_days > 0 THEN 'Late'
    ELSE 'On Time'
END;

DROP TABLE quality_incidents;
