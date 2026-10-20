from datetime import datetime
import queries
import transactions  # Imports your operational workflows cleanly

def get_user_date():
    """Date input funtion used by filter by date functions."""
    while True:
        print("\nFormat Example: 2022-02-14 or 2022-05-26 or 2022-08-24")
        user_input = input("Enter a date (YYYY-MM-DD) [or '0' to cancel]: ").strip()
        if user_input.lower() == '0':
            return None
        try:
            return datetime.strptime(user_input, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid format. Please write it exactly as YYYY-MM-DD.")

def render_dataframe(df):
    """Prints the pandas dataframe cleanly directly to the terminal."""
    print("\n", df.to_string(index=False))

def run_new_transaction_wizard():
    """WIZARD LOOP: Guides the clerk from customer routing to final film allocation checkout."""
    print("\n-----------------------------------------")
    print("      NEW MOVIE RENTAL WIZARD            ")
    print("-----------------------------------------")
    print("Enter customer detail:")
    print("1. Existing Customer")
    print("2. New Customer")
    cust_choice = input("Select customer status (1 or 2) [or '0' to Cancel]: ").strip()
    
    if cust_choice == "0":
        print("Action canceled. Returning to main menu.")
        return

    chosen_customer_id = None
    chosen_store_id = None
    
    # --- PHASE 1: SORT CUSTOMER CONTROLS ---
    if cust_choice == "1":
        search_term = input("\nSearch customer (Enter Name, Email, or ID) [or '0' to Cancel]: ").strip()
        if search_term == "0":
            print("Action canceled. Returning to main menu.")
            return
            
        df_cust = transactions.search_customers(search_term)
        if df_cust is not None and not df_cust.empty:
            render_dataframe(df_cust)
            chosen_customer_id = input("\nFrom the lookup above, enter the exact Customer ID [or '0' to Cancel]: ").strip()
            if chosen_customer_id == "0":
                print("Action canceled. Returning to main menu.")
                return
                
            # AUTOMATION RULE: Extract store_id from the selected customer's DataFrame row
            try:
                matched_row = df_cust[df_cust['customer_id'].astype(str) == chosen_customer_id]
                if not matched_row.empty:
                    chosen_store_id = str(matched_row.iloc[0]['store_id'])
                    print(f">Auto-Selected Home Store: Store {chosen_store_id} based on customer profile records.")
                else:
                    print(">Error: Entered Customer ID does not match lookup records.")
                    return
            except Exception as e:
                print(f">Error linking profile store mapping: {e}")
                return
        else:
            print("No matching existing customers found.")
            return

    elif cust_choice == "2":
        print("\n--- Registering New Customer Profile ---")
        chosen_store_id = input("Enter store ID (1 for Lethbridge, 2 for Woodridge) [or '0' to Cancel]: ").strip()
        if chosen_store_id == "0":
            print("Action canceled. Returning to main menu.")
            return
            
        fname = input("First Name [or '0' to Cancel]: ").strip()
        if fname == "0":
            print("Action canceled. Returning to main menu.")
            return
            
        lname = input("Last Name [or '0' to Cancel]: ").strip()
        if lname == "0":
            print("Action canceled. Returning to main menu.")
            return
        
        # AUTOMATION RULE: Dynamically sets address ID mapping to match the designated store anchor
        if chosen_store_id == "1":
            addr = "1"
        elif chosen_store_id == "2":
            addr = "2"
        else:
            addr = "1"
        
        chosen_customer_id = transactions.add_new_customer(chosen_store_id, fname, lname, addr)
        if chosen_customer_id:
            print(f"Profile verified! Customer established with ID: {chosen_customer_id}")
        else:
            print("Failed to register customer profile.")
            return
    else:
        print("Invalid menu entry.")
        return

    # --- PHASE 2: MOVIE SEARCH WING ---
    print("\n-----------------------------------------")
    print("         STEP 2: MOVIE SEARCH            ")
    print("-----------------------------------------")
    movie_term = input("Search movie (Enter Film ID, Title, or Actor Name) [or '0' to Cancel]: ").strip()
    if movie_term == "0":
        print("Action canceled. Returning to main menu.")
        return
        
    df_movies = transactions.search_movies(movie_term)
    if df_movies is not None and not df_movies.empty:
        render_dataframe(df_movies)
        chosen_film_id = input("\nEnter chosen Film ID from lookup records [or '0' to Cancel]: ").strip()
        if chosen_film_id == "0":
            print("Action canceled. Returning to main menu.")
            return
    else:
        print("No matching films found in inventory listings.")
        return

    # --- PHASE 3: EXTRACT INVENTORY COPIES ---
    print("\n-----------------------------------------")
    print("       STEP 3: ALLOCATING DVD UNIT       ")
    print("-----------------------------------------")
    df_inv = transactions.get_available_inventory(chosen_film_id, chosen_store_id)
    if df_inv is not None and not df_inv.empty:
        render_dataframe(df_inv)
        chosen_inventory_id = input("\nSelect an explicit available Inventory ID copy to lease [or '0' to Cancel]: ").strip()
        if chosen_inventory_id == "0":
            print("Action canceled. Returning to main menu.")
            return
    else:
        print("Sorry, this film currently has no available stock copies left at this store hub.")
        return

    # --- PHASE 4: FINAL CHECKOUT TRANSACTION WRITE ---
    print("\n-----------------------------------------")
    print("          STEP 4: FINAL CHECKOUT         ")
    print("-----------------------------------------")
    
    # Automated Staff Allocation Rule based on chosen_store_id selection
    if chosen_store_id == "1":
        staff_id = "1"
    elif chosen_store_id == "2":
        staff_id = "2"
    else:
        staff_id = "1"
        
    rate = input("Enter final transaction payment amount (e.g. 4.99) [or '0' to Cancel]: ").strip()
    if rate == "0":
        print("Action canceled. Returning to main menu.")
        return
    
    rid, pid = transactions.process_rental_and_payment(chosen_inventory_id, chosen_customer_id, staff_id, rate)
    if rid and pid:
        print(f"\nTRANSACTION COMPLETE!")
        print(f"Rental logged securely under Asset ID: {rid}")
        print(f"Payment invoice registered under ID: {pid}")
    else:
        print("Critical Checkout Error: Transaction write sequence aborted.")

def display_menu():
    while True:
        print("\n-----------------------------------------")
        print("   PAGILA DVD ANALYTICS MENU (PANDAS)    ")
        print("-----------------------------------------")
        print("1. Top 20 Movies by Revenue")
        print("2. Top 20 Spending Customers")
        print("3. Daily Store Revenue Metrics")
        print("4. Initialize & Query 'date_data' View")
        print("5. Check Active Outstanding Rentals")
        print("6. Process a New Transaction (Wizard)")
        print("7. Process a Movie Return")
        print("8. Delete a Customer Account")
        print("0. Exit Dashboard")
        print("-----------------------------------------")
        
        choice = input("Select an option (0-8): ").strip()
        
        if choice == "1":
            print("\nRunning: Top 20 Movies by Total Revenue...")
            df = queries.get_movie_revenue()
            if df is not None:
                render_dataframe(df)
                
        elif choice == "2":
            print("\nRunning: Top 20 High-Spending Customers...")
            df = queries.get_customer_revenue()
            if df is not None:
                render_dataframe(df)
                
        elif choice == "3":
            print("\nRunning: Daily Store Revenue Data...")
            print("\nTarget Date -")
            target_date = get_user_date()
            if target_date:
                df = queries.get_store_revenue(target_date)
                if df is not None:
                    render_dataframe(df)
                    
        elif choice == "4":
            print("\nRunning: Creating and Filtering database view...")
            print("View Filter Options:")
            print("1. Search by exact single date")
            print("2. Search between a range of two dates")
            filter_choice = input("Select filtering method (1 or 2) [or '0' to Cancel]: ").strip()

            if filter_choice == "0":
                print("Action canceled. Returning to main menu.")
                continue

            if filter_choice == "1":
                print("\nExact Date -")
                target_date = get_user_date()
                if target_date:
                    df = queries.setup_and_query_view(target_date)
                    if df is not None:
                        render_dataframe(df)

            elif filter_choice == "2":
                print("\nStart Date -")
                start_date = get_user_date()
                if start_date is None:
                    print("Action canceled. Returning to main menu.")
                    continue
                
                print("\nEnd Date -")
                end_date = get_user_date()    
                if end_date is None:
                    print("Action canceled. Returning to main menu.")
                    continue
                
                df = queries.setup_and_query_view(start_date, end_date)
                if df is not None:
                    render_dataframe(df)
                    
        elif choice == "5":
            print("\nRunning: Active Unreturned Rental Data...")
            df = queries.get_unreturned_rentals()
            if df is not None:
                render_dataframe(df)

        elif choice == "6":
            run_new_transaction_wizard()

        elif choice == "7":
            print("\n--- Movie Return Wizard ---")
            search_term = input("Search for customer returning a movie (Enter Name, Email, or ID) [or '0' to Cancel]: ").strip()
            if search_term == "0":
                print("Action canceled. Returning to main menu.")
                continue
                
            df_search = transactions.search_customers(search_term)
            if df_search is not None and not df_search.empty:
                render_dataframe(df_search)
                
                cid = input("\nFrom the lookup above, enter the exact Customer ID [or '0' to Cancel]: ").strip()
                if cid == "0":
                    print("Action canceled. Returning to main menu.")
                    continue
                
                df_verify = transactions.search_customers(cid)
                if df_verify is not None and not df_verify.empty:
                    db_name = df_verify.loc[0, 'customer_name']
                    print(f"\nChecking active outstanding issues for: {db_name}")
                    
                    df_rentals = transactions.get_customer_active_rentals(cid)
                    if df_rentals is not None and not df_rentals.empty:
                        render_dataframe(df_rentals)
                        
                        rid = input("\nEnter the Rental ID being returned from the list above [or '0' to Cancel]: ").strip()
                        if rid == "0":
                            print("Action canceled. Returning to main menu.")
                            continue
                        
                        if transactions.process_return_by_rental_id(rid):
                            print(f">Success! Rental ID {rid} closed. Movie marked ready for stock.")
                        else:
                            print(f">Error: Could not close Rental ID {rid}. Please verify the selection.")
                    else:
                        print(f"> {db_name} currently has no active, unreturned movies out on lease.")
                else:
                    print(">Failure: Entered Customer ID does not match database lookup indexes.")
            else:
                print("> Failure: No matching customer profiles found for that search query.")

        elif choice == "8":
            print("\n--- Account Cascade Deletion Wizard ---")
            search_term = input("Search for customer to delete (Enter Name, Email, or ID) [or '0' to Cancel]: ").strip()
            if search_term == "0":
                print("Action canceled. Returning to main menu.")
                continue
                
            df_search = transactions.search_customers(search_term)
            if df_search is not None and not df_search.empty:
                render_dataframe(df_search)
                
                cid = input("\nFrom the lookup above, enter the exact Customer ID to drop [or '0' to Cancel]: ").strip()
                if cid == "0":
                    print("Action canceled. Returning to main menu.")
                    continue
                
                df_verify = transactions.search_customers(cid)
                if df_verify is not None and not df_verify.empty:
                    db_name = df_verify.loc[0, 'customer_name']
                    
                    confirm = input(f"Are you sure you want to delete customer {db_name} and all transaction history? (Y/N): ").strip()
                    if confirm.lower() == 'y':
                        if transactions.delete_customer_cascade(cid):
                            print("Account and dependent transaction logs permanently dropped safely.")
                        else:
                            print("Customer ID not found or could not be removed.")
                    else:
                        print("Deletion aborted. Returning to main menu.")
                else:
                    print("> Failure: Entered Customer ID does not match database lookup indexes.")
            else:
                print("> Failure: No matching customer profiles found for that search query.")
                
        elif choice == "0":
            print("\nClosing connection interface. Goodbye!")
            break
        else:
            print("Invalid entry. Try again.")

if __name__ == "__main__":
    display_menu()