import pandas
import warnings
from database import PagilaDatabase

warnings.filterwarnings("ignore", category=UserWarning)
db = PagilaDatabase()

# =====================================================================
# CUSTOMER & FILM RETRIEVAL TOOLS
# =====================================================================

def search_customers(search_term):
    """Searches for existing customers case-insensitively using upper() and returns initcap()."""
    sql = """
    select customer_id,
           store_id,
           initcap(customer.first_name || ' ' || customer.last_name) as customer_name,
           customer.email,
           address_id
    from customer
    where customer_id::text = %s
       or upper(customer.first_name || ' ' || customer.last_name) like upper(%s)
       or upper(email) like upper(%s);
    """
    like_term = f"%{search_term}%"
    try:
        conn = db._get_connection()
        df = pandas.read_sql_query(sql, conn, params=(search_term, like_term, like_term))
        conn.close()
        return df
    except Exception as e:
        print(f"Execution failed: {e}")
        return None

def add_new_customer(store_id, first_name, last_name, address_id):
    """Inserts a new customer record and returns the newly generated customer_id."""
    sql = """
    insert into customer (store_id, first_name, last_name, address_id, activebool)
    values (%s, %s, %s, %s, true)
    returning customer_id;
    """
    try:
        with db._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (store_id, first_name, last_name, address_id))
                customer_id = cursor.fetchone()
                conn.commit()
                return customer_id
    except Exception as e:
        print(f"Execution failed: {e}")
        return None

def search_movies(search_term):
    """Finds movies case-insensitively and displays titles/actors in Title Case format."""
    sql = """
    select film.film_id,
           initcap(film.title) as title,
           film.description,
           film.release_year,
           film.rental_duration,
           film.rental_rate,
           film.length,
           film.replacement_cost,
           film.rating,
           initcap(actor.first_name || ' ' || actor.last_name) as actor_name
    from film
    inner join film_actor on film.film_id = film_actor.film_id
    inner join actor on actor.actor_id = film_actor.actor_id
    where film.film_id::text = %s
       or upper(film.title) like upper(%s)
       or upper(actor.first_name || ' ' || actor.last_name) like upper(%s);
    """
    like_term = f"%{search_term}%"
    try:
        conn = db._get_connection()
        df = pandas.read_sql_query(sql, conn, params=(search_term, like_term, like_term))
        conn.close()
        return df
    except Exception as e:
        print(f"Execution failed: {e}")
        return None

def get_available_inventory(film_id, store_id):
    """Extracts physical DVD inventory copies that are currently ON THE SHELF (not checked out)."""
    sql = """
    select inventory.inventory_id,
           initcap(film.title) as title,
           inventory.store_id
    from inventory
    inner join film on inventory.film_id = film.film_id
    where inventory.film_id = %s
      and inventory.store_id = %s
      -- BUSINESS RULE LOCK: Exclude any copy that is currently rented out and unreturned
      and inventory.inventory_id not in (
          select inventory_id 
          from rental 
          where return_date is null
      );
    """
    try:
        conn = db._get_connection()
        df = pandas.read_sql_query(sql, conn, params=(film_id, store_id))
        conn.close()
        return df
    except Exception as e:
        print(f"Execution failed: {e}")
        return None

# =====================================================================
# WRITE / COMMIT CORE TRANSACTION DRIVERS
# =====================================================================

def process_rental_and_payment(inventory_id, customer_id, staff_id, amount):
    """Creates an active rental transaction row and logs its corresponding currency payment."""
    rental_sql = """
    insert into rental (rental_date, inventory_id, customer_id, staff_id, return_date)
    values (now(), %s, %s, %s, null)
    returning rental_id;
    """
    payment_sql = """
    insert into payment (customer_id, staff_id, rental_id, amount, payment_date)
    values (%s, %s, %s, %s, now())
    returning payment_id;
    """
    try:
        with db._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(rental_sql, (inventory_id, customer_id, staff_id))
                rental_id = cursor.fetchone()
                
                cursor.execute(payment_sql, (customer_id, staff_id, rental_id, amount))
                payment_id = cursor.fetchone()
                
                conn.commit()
                return rental_id, payment_id
    except Exception as e:
        print(f"Execution failed: {e}")
        return None, None

def process_return_by_ids(customer_id, inventory_id):
    """Updates an open rental record with a timestamp by target customer and DVD copy number identifiers."""
    sql = """
    update rental
    set return_date = now()
    where customer_id = %s
      and inventory_id = %s
      and return_date is null;
    """
    try:
        with db._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (customer_id, inventory_id))
                conn.commit()
                return cursor.rowcount > 0
    except Exception as e:
        print(f"Execution failed: {e}")
        return False

def delete_customer_cascade(customer_id):
    """Deletes a customer safely by cascading removal across dependent rental and payment rows."""
    sql = """
    with clear_payments as (
        delete from payment where customer_id = %s
    ),
    clear_rentals as (
        delete from rental where customer_id = %s
    )
    delete from customer 
    where customer_id = %s;
    """
    try:
        with db._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (customer_id, customer_id, customer_id))
                conn.commit()
                return cursor.rowcount > 0
    except Exception as e:
        print(f"Execution failed: {e}")
        return False

def get_customer_active_rentals(customer_id):
    """Fetches all open, unreturned rentals for a specific customer."""
    sql = """
    select rental.rental_id,
           rental.rental_date,
           initcap(film.title) as film_title,
           rental.inventory_id
    from rental
    inner join inventory on rental.inventory_id = inventory.inventory_id
    inner join film on inventory.film_id = film.film_id
    where rental.customer_id = %s
      and rental.return_date is null;
    """
    try:
        conn = db._get_connection()
        df = pandas.read_sql_query(sql, conn, params=(customer_id,))
        conn.close()
        return df
    except Exception as e:
        print(f"Execution failed: {e}")
        return None

def process_return_by_rental_id(rental_id):
    """Updates a specific open rental record using its unique rental_id identifier."""
    sql = """
    update rental
    set return_date = now()
    where rental_id = %s
      and return_date is null;
    """
    try:
        with db._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (rental_id,))
                conn.commit()
                return cursor.rowcount > 0
    except Exception as e:
        print(f"Execution failed: {e}")
        return False