-- c) procedimiento setOrderAmount
CREATE OR REPLACE FUNCTION setOrderAmount() RETURNS void as $$
BEGIN
    UPDATE public.orders
    SET netamount = TOTAL.total
    FROM
        (SELECT orders.orderid, SUM(orderdetail.price) AS total
        FROM public.orders, public.orderdetail
        WHERE orders.orderid = orderdetail.orderid
        GROUP BY orders.orderid) AS TOTAL
    WHERE orders.orderid = TOTAL.orderid
    AND netamount IS NULL;

    UPDATE public.orders
    SET totalamount = ROUND(netamount * (1 + tax/100), 2)
    WHERE totalamount IS NULL;
END;
$$ LANGUAGE plpgsql;