# alx-backend-graphql_crm

A Django-based CRM backend with GraphQL API using graphene-django and django-filter.

## Features

- Customer, Product, and Order models
- GraphQL endpoint with queries and mutations
- Bulk and nested mutations
- Filtering and ordering with django-filter
- Seed script for demo data

## Setup

1. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

2. Run migrations:

   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```

3. (Optional) Seed the database:

   ```sh
   python seed_db.py
   ```

4. Start the server:

   ```sh
   python manage.py runserver
   ```

5. Access GraphQL at: [http://localhost:8000/graphql](http://localhost:8000/graphql)

## Example GraphQL Mutations

```ql
mutation {
  createCustomer(input: { name: "Alice", email: "alice@example.com", phone: "+1234567890" }) {
    customer { id name email phone }
    message
  }
}
```

## Filtering Example

```ql
query {
  allCustomers(filter: { nameIcontains: "Ali" }) {
    edges { node { id name email } }
  }
}
```

**Project structure:**

- `alx_backend_graphql_crm/` - Django settings only
- `crm/` - Main app (models, schema, filters)
- `graphql_crm/` - Main schema
- `manage.py`, `seed_db.py`, `README.md` - Project root
