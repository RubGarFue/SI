-- g) Trigger que actualiza tabla orders cuando se edita el carrito

CREATE OR REPLACE FUNCTION updOrders() RETURNS TRIGGER as $$
BEGIN 
    IF TG_OP = 'UPDATE' THEN
        UPDATE public.orders
        SET netamount = netamount + NEW.price * (NEW.quantity - OLD.quantity),
        orderdate = NOW()::date
        WHERE orderid = NEW.orderid;
        UPDATE public.orders
        SET totalamount = ROUND(netamount * (1+ tax/100), 2)
        WHERE orderid = NEW.orderid;
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        UPDATE public.orders
        SET netamount = netamount + NEW.price * NEW.quantity,
        orderdate = NOW()::date
        WHERE orderid = NEW.orderid;
        UPDATE public.orders
        SET totalamount = ROUND(netamount * (1+ tax/100), 2)
        WHERE orderid = NEW.orderid;
        RETURN NEW;
    ELSE -- DELETE
        UPDATE public.orders
        SET netamount = netamount - OLD.price * OLD.quantity
        WHERE orderid = OLD.orderid;
        UPDATE public.orders
        SET totalamount = ROUND(netamount * (1+ tax/100), 2)
        WHERE orderid = OLD.orderid;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER updOrderTrigger
AFTER INSERT 
OR UPDATE
OR DELETE
ON public.orderdetail
FOR EACH ROW
EXECUTE PROCEDURE updOrders();