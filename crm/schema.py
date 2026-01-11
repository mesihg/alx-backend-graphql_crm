import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from graphene_django.filter import DjangoFilterConnectionField
import re
from decimal import Decimal
from django.utils import timezone
from graphql import GraphQLError

from .models import Customer, Product, Order
from crm.models import Product

# GraphQL types

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

# Base Query
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, root, info):
        return Customer.objects.all()
    
    def resolve_products(self, root, info):
        return Product.objects.all()
    
    def resolve_orders(self, root, info):
        return Order.objects.all()

    
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    # customer = graphene.Field(CustomerType)
    customer = graphene.Field(lambda: CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def validate_phone(phone):
        if not phone:
            return True
        phone_regex = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
        return re.match(phone_regex, phone)

    def mutate(self, info, name, email, phone=None):
        try:
            validate_email(email)
        except DjangoValidationError:
            raise GraphQLError("Invalid email format.")
            # return CreateCustomer(success=False, message="Invalid email format.")
        if Customer.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists.")
            # return CreateCustomer(success=False, message="Email already exists.")
        if phone and not self.validate_phone(phone):
            raise GraphQLError(
                "Invalid phone format. Use +1234567890 or 123-456-7890."
            )
            # return CreateCustomer(success=False, message="Invalid phone format.")
        # customer = Customer(name=name, email=email, phone=phone)
        customer = Customer.objects.create(
            name=name,
            email=email,
            phone=phone
        )
        # customer.save()
        return CreateCustomer(
            customer=customer,
            success=True, 
            message="Customer created successfully."
        )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(graphene.JSONString, required=True)
    created = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
     
    @classmethod
    def mutate(cls, root, info, customers):
        created = []
        errors = []
        with transaction.atomic():
            for idx, data in enumerate(customers):
                name = data.get("name")
                email = data.get("email")
                phone  = data.get("phone")

                try:
                    validate_email(email)
                    if Customer.objects.filter(email=email).exists():
                        raise Exception(f"Email already exists: {email}")
                    if phone and not re.match(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$', phone):
                        raise Exception(f"Invalid phone format: {phone}")
                    customer = Customer.objects.create(
                        name=name,
                        email=email,
                        phone=phone
                    )
                    created.append(customer)
                except Exception as e:
                    errors.append(f"Row {idx+1}: {str(e)}")
        return BulkCreateCustomers(created=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int()
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, name, price, stock=0):
        try:
            price = Decimal(price)
            if price <= 0:
                return CreateProduct(success=False, message ="Price must be positive.")
            if stock is not None and stock < 0:
                return CreateProduct(success=False, message ="Stock cannot be negative.")
            product = Product.objects.create(
                name=name,
                price=price,
                stock=stock
                )
            return CreateProduct(
                product=product,
                success=True,
                message="Product created."
                )
        except Exception as e:
            return CreateProduct(success=False, message=str(e))

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(order=None,message="Invalid customer ID.")
        products = Product.objects.filter(pk__in=product_ids)
        if not products or len(products) != len(product_ids):
            return CreateOrder(order=None, message="One or more invalid product IDs.")
        if not product_ids:
            return CreateOrder(order=None, message="At least one product must be selected.")
        order = Order(
            customer=customer,
            order_date=order_date or timezone.now()
        )
        order.save()
        order.products.set(products)
        total = sum([p.price for p in products], Decimal("0"))
        order.total_amount = Decimal(total)
        order.save()
        return CreateOrder(
            order=order,
            message="Order created."
        )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    
    all_customers = DjangoFilterConnectionField(
        CustomerType, 
        order_by=graphene.List(of_type=graphene.String),filter=graphene.String(),
        search=graphene.String()
    )
    
       
    all_products = DjangoFilterConnectionField(
        ProductType, 
        order_by=graphene.List(of_type=graphene.String),filter=graphene.String(),
        search=graphene.String()
    )
    all_orders = DjangoFilterConnectionField(
        OrderType, 
        order_by=graphene.List(of_type=graphene.String),filter=graphene.String(),
        search=graphene.String()
    )

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # no arguments needed

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []
        for product in low_stock_products:
            product.stock += 10  # simulate restock
            product.save()
            updated_products.append(product)

        return UpdateLowStockProducts(
            success=True,
            message=f"{len(updated_products)} products updated at {timezone.now()}",
            updated_products=updated_products
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
