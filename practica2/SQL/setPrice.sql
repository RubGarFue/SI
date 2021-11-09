-- b) consulta setPrice
-- el precio que tenemos que poner es el precio original, así que la fórmula es:
-- precio_original = precio_actual / 1.02^(fecha_actual - fecha_entonces)
UPDATE public.orderdetail
SET price = ROUND(CAST(products.price / POW(1.02, DATE_PART('year', NOW()::date) - DATE_PART('year', orders.orderdate::date)) AS NUMERIC), 2)
FROM public.orders, public.products
WHERE orderdetail.orderid = orders.orderid AND orderdetail.prod_id = products.prod_id;