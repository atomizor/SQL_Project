import pandas
from database import PagilaDatabase
import warnings

pandas.set_option('display.max_rows', None)
pandas.set_option('display.max_columns', None)
pandas.set_option('display.expand_frame_repr', False)
warnings.filterwarnings("ignore", category=UserWarning)

# Initialize your database connection engine
db = PagilaDatabase()

def get_movie_revenue():
    sql = """
    select film.title,
           film.description,
           film.release_year,
           sum(payment.amount) as revenue$_per_movie
    from rental
    inner join customer on rental.customer_id = customer.customer_id 
    inner join inventory on rental.inventory_id = inventory.inventory_id
    inner join film on inventory.film_id = film.film_id
    inner join staff on staff.staff_id = rental.staff_id
    inner join store on store.store_id = staff.store_id
    inner join payment on rental.rental_id = payment.rental_id
    group by film.film_id, film.title, film.description, film.release_year
    order by revenue$_per_movie desc
    limit 20;
    """
    try:
        conn = db._get_connection() 
        df = pandas.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Execution failed: {e}")
        return None

def get_customer_revenue():
    sql = """
    select customer.customer_id,
           customer.first_name || ' ' || customer.last_name as customer_name,
           sum(payment.amount) as revenue$_per_customer
    from rental
    inner join customer on rental.customer_id = customer.customer_id 
    inner join inventory on rental.inventory_id = inventory.inventory_id
    inner join film on inventory.film_id = film.film_id
    inner join staff on staff.staff_id = rental.staff_id
    inner join store on store.store_id = staff.store_id
    inner join payment on rental.rental_id = payment.rental_id
    group by customer.customer_id, customer.first_name, customer.last_name
    order by revenue$_per_customer desc
    limit 20;
    """
    try:
        conn = db._get_connection() 
        df = pandas.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Execution failed: {e}")
        return None

def get_store_revenue(target_date):
    sql = """
    select staff.store_id,
           count(distinct rental.rental_id) as total_rentals,
           -- Sum the actual payment amount collected rather than static movie configurations
           sum(payment.amount) as revenue_on_target_date
    from rental
    inner join staff on staff.staff_id = rental.staff_id
    inner join payment on rental.rental_id = payment.rental_id
    where date(rental.rental_date) = %s
    group by staff.store_id
    order by staff.store_id;
    """
    try:
        conn = db._get_connection() 
        df = pandas.read_sql_query(sql, conn, params=(target_date,))
        conn.close()
        return df
    except Exception as e:
        print(f"Execution failed: {e}")
        return None

def setup_and_query_view(target_date, end_date=None):
    create_view_sql = """
    create or replace view date_data as
    select customer.customer_id,
           rental_date,
           customer.first_name || ' ' || customer.last_name as customer_name,
           title as film_title,
           rental_rate,        
           store.store_id
    from rental
    inner join customer on rental.customer_id = customer.customer_id 
    inner join inventory on rental.inventory_id = inventory.inventory_id
    inner join film on inventory.film_id = film.film_id
    inner join staff on staff.staff_id = rental.staff_id
    inner join store on store.store_id = staff.store_id;
    """
    
    try:
        if not db.execute_write_query(create_view_sql):
            db.execute_write_query("drop view if exists date_data;")
            db.execute_write_query(create_view_sql)
    except Exception:
        db.execute_write_query("drop view if exists date_data;")
        db.execute_write_query(create_view_sql)

    if end_date:
        select_sql = """
        select * from date_data 
        -- FIXED: Casting rental_date to a clean DATE type includes the start and end dates completely
        where date(rental_date) between to_date(%s, 'yyyy-mm-dd') 
                                   and to_date(%s, 'yyyy-mm-dd') 
        order by store_id;
        """
        params = (str(target_date), str(end_date))
    else:
        select_sql = "select * from date_data where date(rental_date) = %s order by store_id;"
        params = (target_date,)

    try:
        conn = db._get_connection() 
        df = pandas.read_sql_query(select_sql, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"Execution failed: {e}")
        return None

def get_unreturned_rentals():
    sql = """
    select rental_id,
           film.title,
           rental_date,
           rental_duration,
           first_name || ' ' || customer.last_name as full_name,
           email,
           address.phone,
           substring(address || coalesce(' ' || address2, '') || ' ' || district || ' ' || city.city || ' ' || postal_code || ' ' || country.country from 1 for 58) as address
    from rental
    inner join customer on customer.customer_id = rental.customer_id
    inner join inventory on rental.inventory_id = inventory.inventory_id
    inner join film on inventory.film_id = film.film_id
    inner join address on address.address_id = customer.address_id
    inner join city on address.city_id = city.city_id
    inner join country on city.country_id = country.country_id
    where rental.return_date is null;
    """
    try:
        conn = db._get_connection() 
        df = pandas.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Execution failed: {e}")
        return None