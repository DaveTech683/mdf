# cart/cart.py

from decimal import Decimal

from customers.models import Product


class Cart:
    SESSION_KEY = 'session_key'

    def __init__(self, request):
        self.session = request.session

        cart = self.session.get(self.SESSION_KEY)

        # If cart does not exist or is corrupted, reset it safely
        if not isinstance(cart, dict):
            cart = {}
            self.session[self.SESSION_KEY] = cart
            self.session.modified = True

        # Clean corrupted session data
        cleaned = {}

        for key, value in cart.items():
            key = str(key)

            if not key.isdigit():
                continue

            try:
                quantity = int(value)
            except (TypeError, ValueError):
                continue

            if quantity > 0:
                cleaned[key] = quantity

        if cleaned != cart:
            self.session[self.SESSION_KEY] = cleaned
            self.session.modified = True

        self.cart = self.session[self.SESSION_KEY]

    # ---- mutation -------------------------------------------------

    def add(self, product, quantity=1):
        product_id = str(product.product_id)

        if not product_id.isdigit():
            return False

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return False

        if quantity < 1:
            return False

        current_quantity = self.get_quantity(product_id)
        self.cart[product_id] = current_quantity + quantity

        self.session.modified = True
        return True

    def update(self, product_id, quantity):
        product_id = str(product_id)

        if not product_id.isdigit():
            return False

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return False

        if product_id not in self.cart:
            return False

        if quantity < 1:
            del self.cart[product_id]
        else:
            self.cart[product_id] = quantity

        self.session.modified = True
        return True

    def delete(self, product_id):
        product_id = str(product_id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True
            return True

        return False

    def clear(self):
        if self.SESSION_KEY in self.session:
            del self.session[self.SESSION_KEY]
            self.session.modified = True

    # ---- read helpers -------------------------------------------------

    def __len__(self):
        total_quantity = 0

        for quantity in self.cart.values():
            try:
                total_quantity += int(quantity)
            except (TypeError, ValueError):
                continue

        return total_quantity

    def distinct_count(self):
        return len(self.cart)

    def get_quantity(self, product_id):
        try:
            return int(self.cart.get(str(product_id), 0))
        except (TypeError, ValueError):
            return 0

    @property
    def get_prods(self):
        product_ids = [key for key in self.cart.keys() if str(key).isdigit()]
        return Product.objects.filter(product_id__in=product_ids)

    @property
    def get_quants(self):
        return self.cart

    def get_items(self):
        product_ids = [key for key in self.cart.keys() if str(key).isdigit()]

        products = {
            str(product.product_id): product
            for product in Product.objects.filter(product_id__in=product_ids)
        }

        items = []

        for product_id, quantity in self.cart.items():
            product_id = str(product_id)

            if not product_id.isdigit():
                continue

            product = products.get(product_id)

            if not product:
                continue

            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                continue

            if quantity < 1:
                continue

            unit_price = product.sale_price if product.is_sale else product.price
            subtotal = unit_price * quantity

            items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': subtotal,
            })

        return items

    def cart_total(self):
        total = Decimal('0.00')

        for item in self.get_items():
            total += item['subtotal']

        return total