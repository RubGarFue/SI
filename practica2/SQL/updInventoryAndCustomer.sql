-- h) Trigger que actualiza tabla orders cuando se edita el carrito

CREATE OR REPLACE FUNCTION updInventoryAndCustomer() RETURNS TRIGGER as $$
BEGIN  
    -- Update order date
    UPDATE public.orders
    SET orderdate = NOW()::date
    WHERE orderid = NEW.orderid;

    -- Update inventory
    UPDATE public.inventory 
    SET stock = stock - quantity,
    sales = sales + quantity
    FROM public.orderdetail
    WHERE public.inventory.prod_id = public.orderdetail.prod_id;

    -- Out of stock alerts in 'actualiza.sql': alertTrigger

    -- Update loyalty points and customer's balance
    UPDATE public.customers
    SET loyalty = loyalty + ROUND(NEW.totalamount*0.05,0),
    balance = balance - NEW.totalamount
    WHERE customerid = NEW.customerid;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER updInventoryAndCustomerTrigger
AFTER UPDATE
ON public.orders
FOR EACH ROW
WHEN (NEW.status IS DISTINCT FROM OLD.status AND NEW.status IS NOT DISTINCT FROM 'Paid')
EXECUTE PROCEDURE updInventoryAndCustomer();