# paytechuz

[![PyPI version](https://badge.fury.io/py/paytechuz.svg)](https://badge.fury.io/py/paytechuz)
[![Python Versions](https://img.shields.io/pypi/pyversions/paytechuz.svg)](https://pypi.org/project/paytechuz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PayTechUZ is a unified payment library for integrating with popular payment systems in Uzbekistan. It provides a simple and consistent interface for working with Payme and Click payment gateways.

## Features

- 🔄 **API**: Consistent interface for multiple payment providers
- 🛡️ **Secure**: Built-in security features for payment processing
- 🔌 **Framework Integration**: Native support for Django and FastAPI
- 🌐 **Webhook Handling**: Easy-to-use webhook handlers for payment notifications
- 📊 **Transaction Management**: Automatic transaction tracking and management
- 🧩 **Extensible**: Easy to add new payment providers
## Installation

### Basic Installation

```bash
pip install paytechuz
```

### Framework-Specific Installation

```bash
# For Django
pip install paytechuz[django]

# For FastAPI
pip install paytechuz[fastapi]
```

## Quick Start

### Generate Payment Links

```python
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway

# Initialize Payme gateway
payme = PaymeGateway(
    payme_id="your_payme_id",
    payme_key="your_payme_key",
    is_test_mode=True  # Set to False in production environment
)

# Initialize Click gateway
click = ClickGateway(
    service_id="your_service_id",
    merchant_id="your_merchant_id",
    merchant_user_id="your_merchant_user_id",
    secret_key="your_secret_key",
    is_test_mode=True  # Set to False in production environment
)

# Generate payment links
payme_link = payme.create_payment(
    id="order_123",
    amount=150000,  # amount in UZS
    return_url="https://example.com/return"
)

click_link = click.create_payment(
    id="order_123",
    amount=150000,  # amount in UZS
    description="Test payment",
    return_url="https://example.com/return"
)
```

### Django Integration

1. Create Order model:

```python
# models.py
from django.db import models
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('delivered', 'Delivered'),
    )

    product_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} - {self.product_name} ({self.amount})"
```

2. Add to `INSTALLED_APPS` and configure settings:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'paytechuz.integrations.django',
]

PAYME_ID = 'your_payme_merchant_id'
PAYME_KEY = 'your_payme_merchant_key'
PAYME_ACCOUNT_MODEL = 'your_app.models.Order'  # For example: 'orders.models.Order'
PAYME_ACCOUNT_FIELD = 'id'
PAYME_AMOUNT_FIELD = 'amount'  # Field for storing payment amount
PAYME_ONE_TIME_PAYMENT = True  # Allow only one payment per account

CLICK_SERVICE_ID = 'your_click_service_id'
CLICK_MERCHANT_ID = 'your_click_merchant_id'
CLICK_SECRET_KEY = 'your_click_secret_key'
CLICK_ACCOUNT_MODEL = 'your_app.models.Order'
CLICK_COMMISSION_PERCENT = 0.0
```

3. Create webhook handlers:

```python
# views.py
from paytechuz.integrations.django.views import BasePaymeWebhookView, BaseClickWebhookView
from .models import Order

class PaymeWebhookView(BasePaymeWebhookView):
    def successfully_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'paid'
        order.save()

    def cancelled_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'cancelled'
        order.save()

class ClickWebhookView(BaseClickWebhookView):
    def successfully_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'paid'
        order.save()

    def cancelled_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'cancelled'
        order.save()
```

4. Add webhook URLs to `urls.py`:

```python
# urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import PaymeWebhookView, ClickWebhookView

urlpatterns = [
    # ...
    path('payments/webhook/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('payments/webhook/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
]
```

### FastAPI Integration

1. Set up database models:

```python
from datetime import datetime, timezone

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime

from paytechuz.integrations.fastapi import Base as PaymentsBase
from paytechuz.integrations.fastapi.models import run_migrations


# Create database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./payments.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create base declarative class
Base = declarative_base()

# Create Order model
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    amount = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Create payment tables using run_migrations
run_migrations(engine)

# Create Order table
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

2. Create webhook handlers:

```python
from fastapi import FastAPI, Request, Depends

from sqlalchemy.orm import Session

from paytechuz.integrations.fastapi import PaymeWebhookHandler, ClickWebhookHandler


app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CustomPaymeWebhookHandler(PaymeWebhookHandler):
    def successfully_payment(self, params, transaction):
        # Handle successful payment
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        order.status = "paid"
        self.db.commit()

    def cancelled_payment(self, params, transaction):
        # Handle cancelled payment
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        order.status = "cancelled"
        self.db.commit()

class CustomClickWebhookHandler(ClickWebhookHandler):
    def successfully_payment(self, params, transaction):
        # Handle successful payment
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        order.status = "paid"
        self.db.commit()

    def cancelled_payment(self, params, transaction):
        # Handle cancelled payment
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        order.status = "cancelled"
        self.db.commit()

@app.post("/payments/payme/webhook")
async def payme_webhook(request: Request, db: Session = Depends(get_db)):
    handler = CustomPaymeWebhookHandler(
        db=db,
        payme_id="your_merchant_id",
        payme_key="your_merchant_key",
        account_model=Order,
        account_field='id',
        amount_field='amount'
    )
    return await handler.handle_webhook(request)

@app.post("/payments/click/webhook")
async def click_webhook(request: Request, db: Session = Depends(get_db)):
    handler = CustomClickWebhookHandler(
        db=db,
        service_id="your_service_id",
        merchant_id="your_merchant_id",
        secret_key="your_secret_key",
        account_model=Order
    )
    return await handler.handle_webhook(request)
```

## Documentation

Detailed documentation is available in multiple languages:

- 📖 [English Documentation](src/docs/en/index.md)
- 📖 [O'zbek tilidagi hujjatlar](src/docs/index.md)

### Framework-Specific Documentation

- [Django Integration Guide](src/docs/en/django_integration.md) | [Django integratsiyasi bo'yicha qo'llanma](src/docs/django_integration.md)
- [FastAPI Integration Guide](src/docs/en/fastapi_integration.md) | [FastAPI integratsiyasi bo'yicha qo'llanma](src/docs/fastapi_integration.md)

## Supported Payment Systems

- **Payme** - [Official Website](https://payme.uz)
- **Click** - [Official Website](https://click.uz)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
