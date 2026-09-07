--supplier quality analysis
SELECT
    supplier_id,
    COUNT(incident_id) AS total_incidents,
    SUM(scrap_qty) AS total_scrap,
    ROUND(AVG(scrap_qty),2) AS avg_scrap
FROM quality_incidents
GROUP BY supplier_id
ORDER BY total_incidents DESC;

--part quality analysis
SELECT
    q.part_id,
    q.supplier_id,
    p.part_family,
    p.criticality_class,
    p.unit_cost,
    p.lead_time_days,
    COUNT(q.incident_id) AS quality_incidents,
    SUM(q.scrap_qty) AS total_scrap,
    ROUND(AVG(q.scrap_qty),2) AS avg_scrap
FROM quality_incidents q
JOIN parts_master p
ON q.part_id = p.part_id
GROUP BY
    q.part_id,
    q.supplier_id,
    p.part_family,
    p.criticality_class,
    p.unit_cost,
    p.lead_time_days
ORDER BY quality_incidents DESC
LIMIT 20;

SELECT
    supplier_id,
    COUNT(po_id) AS total_orders,
    ROUND(AVG(delivery_delay_days),2) AS avg_delay_days,

    ROUND(
        SUM(
            CASE 
                WHEN delivery_status = 'Late' 
                THEN 1 
                ELSE 0 
            END
        )::numeric 
        / COUNT(po_id),
        3
    ) AS late_delivery_rate,

    ROUND(
        SUM(received_qty)::numeric /
        SUM(ordered_qty),
        3
    ) AS fill_rate

FROM purchase_orders

GROUP BY supplier_id

ORDER BY late_delivery_rate DESC;