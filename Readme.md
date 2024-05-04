## INITIAL SETUP

1. Clone the repository:
    ```bash
    git clone https://github.com/Viveknayak000/fatmug-vendor.git
    ```

2. Navigate to the project directory:
    ```bash
    cd vendor_management_system     
    ```

3. Activate virtualenv:
    ```bash
    ./env/Scripts/Activate 
    ```

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Apply database migrations:
    ```bash
    python manage.py migrate
    ```

6. Run the development server using the following command:
    ```bash
    python manage.py runserver
    ```

---

## Setup instructions and details on using the API endpoints:

I have used Swagger for API Documentation and tested the functionality and reliability of the endpoints.

---

## API Endpoint Details:

### VENDORS:

1. **List/Create Vendors:**

    - URL: `api/vendors/`
    - Method: GET (List Vendors), POST (Create Vendor)
    - Authentication: Token Authentication required

2. **Retrieve/Update Vendor:**

    - URL: `api/vendors/<int:pk>/`
    - Method: GET (Retrieve Vendor), PUT (Update Vendor)
    - Authentication: Token Authentication required

3. **Delete Vendor:**

    - URL: `api/vendors/<int:pk>/`
    - Method: DELETE
    - Authentication: Token Authentication required

### PURCHASE ORDERS:

1. **List/Create Purchase Orders:**

    - URL: `api/purchase_orders/`
    - Method: GET (List Purchase Orders), POST (Create Purchase Order)
    - Authentication: Token Authentication required

2. **Retrieve/Update Purchase Order:**

    - URL: `api/purchase_orders/<int:pk>/`
    - Method: GET (Retrieve Purchase Order), PUT (Update Purchase Order)
    - Authentication: Token Authentication required

3. **Delete Purchase Order:**

    - URL: `api/purchase_orders/<int:pk>/`
    - Method: DELETE
    - Authentication: Token Authentication required.

---

### Additional Endpoints:

- **Acknowledge Purchase Order:**

    - URL: `api/purchase_orders/<int:pk>/Acknowledge/`
    - Method: PUT (Acknowledge Purchase Order)
    - Authentication: Token Authentication required