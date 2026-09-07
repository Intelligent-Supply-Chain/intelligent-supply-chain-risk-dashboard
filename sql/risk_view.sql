CREATE VIEW supplier_risk_view AS

SELECT
    po.supplier_id,

    COUNT(po.po_id) AS total_orders,

    ROUND(AVG(po.delivery_delay_days),2) AS avg_delay_days,

    ROUND(
        SUM(
            CASE 
                WHEN po.delivery_status='Late'
                THEN 1
                ELSE 0
            END
        )::numeric / COUNT(po.po_id),
        3
    ) AS late_delivery_rate,


    ROUND(
        SUM(po.received_qty)::numeric /
        SUM(po.ordered_qty),
        3
    ) AS fill_rate,


    COALESCE(qi.total_incidents,0) AS quality_incidents,

    COALESCE(qi.total_scrap,0) AS total_scrap


FROM purchase_orders po


LEFT JOIN
(
    SELECT
        supplier_id,
        COUNT(incident_id) AS total_incidents,
        SUM(scrap_qty) AS total_scrap

    FROM quality_incidents

    GROUP BY supplier_id

) qi

ON po.supplier_id = qi.supplier_id


GROUP BY
po.supplier_id,
qi.total_incidents,
qi.total_scrap;

SELECT *
FROM supplier_risk_view
ORDER BY quality_incidents DESC;

CREATE VIEW part_risk_view AS

SELECT

    pm.part_id,
    pm.part_family,
    pm.criticality_class,
    pm.unit_cost,
    pm.lead_time_days,
    pm.supplier_id_primary,


    -- Demand Features

    ROUND(AVG(sh.consumption_qty),2) AS avg_demand,

    ROUND(STDDEV(sh.consumption_qty),2) AS demand_std,

    SUM(sh.consumption_qty) AS total_demand,


    -- Inventory Features

    ROUND(AVG(sh.on_hand_qty),2) AS avg_inventory,

    ROUND(AVG(sh.backorder_qty),2) AS avg_backorder,

    SUM(sh.backorder_qty) AS total_backorder,


    -- Supplier Features

    sr.avg_delay_days,

    sr.late_delivery_rate,

    sr.fill_rate,


    -- Quality Features

    sr.quality_incidents,

    sr.total_scrap


FROM parts_master pm


LEFT JOIN supply_chain_history sh

ON pm.part_id = sh.part_id


LEFT JOIN supplier_risk_view sr

ON pm.supplier_id_primary = sr.supplier_id


GROUP BY

    pm.part_id,
    pm.part_family,
    pm.criticality_class,
    pm.unit_cost,
    pm.lead_time_days,
    pm.supplier_id_primary,

    sr.avg_delay_days,
    sr.late_delivery_rate,
    sr.fill_rate,
    sr.quality_incidents,
    sr.total_scrap

SELECT *
FROM part_risk_view
LIMIT 10;

CREATE VIEW combined_risk_view AS

SELECT

    pr.part_id,
    pr.part_family,
    pr.criticality_class,
    pr.unit_cost,
    pr.lead_time_days,

    pr.supplier_id_primary AS supplier_id,


    -- Part Risk Components

    pr.avg_demand,
    pr.total_backorder,
    pr.quality_incidents,


    -- Supplier Risk Components

    sr.total_orders,
    sr.avg_delay_days,
    sr.late_delivery_rate,
    sr.fill_rate,


    -- Combined Risk Calculation

    ROUND(

        (
            (
            COALESCE(pr.total_backorder,0)::numeric
            /
            NULLIF(MAX(pr.total_backorder) OVER(),0)
            )

            *0.35


            +

            (
            COALESCE(sr.late_delivery_rate,0)
            )

            *0.35


            +

            (
            COALESCE(sr.quality_incidents,0)::numeric
            /
            NULLIF(MAX(sr.quality_incidents) OVER(),0)
            )

            *0.30


        )

    ,3)

    AS combined_risk_score


FROM part_risk_view pr


LEFT JOIN supplier_risk_view sr

ON pr.supplier_id_primary = sr.supplier_id;

SELECT *
FROM combined_risk_view
ORDER BY combined_risk_score DESC
LIMIT 20;

--FINAL risk view
CREATE VIEW final_risk_view AS

SELECT
    *,
    
    CASE

        WHEN combined_risk_score >= 0.75
        THEN 'Immediate Action'

        WHEN combined_risk_score >= 0.50
        THEN 'High Priority'

        WHEN combined_risk_score >= 0.25
        THEN 'Monitor'

        ELSE 'Normal'

    END AS risk_category


FROM combined_risk_view;

SELECT
    part_id,
    supplier_id,
    combined_risk_score,
    risk_category

FROM final_risk_view

ORDER BY combined_risk_score DESC

LIMIT 20;