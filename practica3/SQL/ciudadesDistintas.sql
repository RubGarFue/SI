CREATE INDEX idx_year
ON orders(orderdate);
		  
CREATE INDEX idx_date ON orders (EXTRACT (year FROM orderdate), EXTRACT(month FROM orderdate));

EXPLAIN ANALYZE
SELECT COUNT(DISTINCT city)
FROM customers
INNER JOIN orders
ON orders.customerid = customers.customerid
WHERE creditcardtype = 'VISA'
AND orderdate = TO_DATE('201604', 'YYYYMM');

EXPLAIN ANALYZE
SELECT COUNT(DISTINCT city)
FROM customers
INNER JOIN orders
ON orders.customerid = customers.customerid
WHERE creditcardtype = 'VISA'
AND EXTRACT (year FROM orderdate ) = 2016
AND EXTRACT (MONTH FROM orderdate ) = 4;