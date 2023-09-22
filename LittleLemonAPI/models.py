import decimal
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.title

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):

        self.unit_price = self.menuitem.price
        self.price = decimal.Decimal(self.unit_price) * decimal.Decimal(self.quantity)

        super(Cart, self).save(*args, **kwargs)

    class Meta: 
        unique_together = ('menuitem', 'user')

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='delivery_crew', null=True)
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    date = models.DateField(db_index=True) 

    def update_total(self):
        self.total = 0
        for order_item in self.orderitem_set.all():
            self.total += decimal.Decimal(order_item.price) 

    def save(self, *args, **kwargs):
        
        super(Order, self).save(*args, **kwargs)
        self.update_total()
        super(Order, self).save(*args, **kwargs)

class OrderItem(models.Model):
    order= models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True)

    def get_title(self):
        return self.menuitem.title

    def save(self, *args, **kwargs):

        self.unit_price = self.menuitem.price
        self.price = decimal.Decimal(self.unit_price) * decimal.Decimal(self.quantity)

        self.order.save()

        super(OrderItem, self).save(*args, **kwargs)
   
    class Meta:
        unique_together = ('order', 'menuitem')

