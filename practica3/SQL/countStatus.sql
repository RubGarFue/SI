-- Apartado G

SELECT count(*)
FROM orders
WHERE status IS null;

SELECT count(*)
FROM orders
WHERE status = 'Shipped';

CREATE INDEX idx_status
ON orders(status);

ANALYZE VERBOSE orders;