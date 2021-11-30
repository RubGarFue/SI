-- Apartado G

EXPLAIN ANALYZE
SELECT count(*)
FROM orders
WHERE status IS null;

EXPLAIN ANALYZE
SELECT count(*)
FROM orders
WHERE status = 'Shipped';

-- index
CREATE INDEX idx_status
ON orders(status);

EXPLAIN ANALYZE
SELECT count(*)
FROM orders
WHERE status IS null;

EXPLAIN ANALYZE
SELECT count(*)
FROM orders
WHERE status = 'Shipped';

-- statistics
ANALYZE VERBOSE orders;

EXPLAIN ANALYZE
SELECT count(*)
FROM orders
WHERE status IS null;

EXPLAIN ANALYZE
SELECT count(*)
FROM orders
WHERE status = 'Shipped';

-- las otras consultas
EXPLAIN ANALYZE
SELECT count(*)
FROM orders
WHERE status = 'Paid';

EXPLAIN ANALYZE
SELECT count(*)
FROM orders
WHERE status = 'Processed';
