from django.db import models
from django.conf import settings
# Create your models here.
from .paystack import PayStack
import secrets

class Category(models.Model):
    title=models.CharField(max_length=25)

    def __str__(self):
        return self.title


class Item(models.Model):
    vendor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete= models.CASCADE,null=True)
    title=models.CharField(max_length=25)
    photo_url=models.ImageField(null=True,blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    delivery_fee=models.FloatField(default=0)
    different_location_fee=models.FloatField(default=0)
    delivery_date=models.CharField(max_length=40,null=True,blank=True)
    price=models.FloatField()

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    vendor=models.ForeignKey(settings.AUTH_USER_MODEL,related_name="vendor",on_delete= models.CASCADE)
    item=models.ForeignKey(Item,on_delete=models.CASCADE,null=True)
    is_ordered=models.BooleanField(default=False)
    is_accepted=models.BooleanField(default=False)
    is_delivered=models.BooleanField(default=False)
    is_removed=models.BooleanField(default=False)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete= models.CASCADE,related_name="user",null=True)
    delivery_location=models.CharField(max_length=40,null=True,blank=True)
    ref=models.CharField(max_length=200,null=True,blank=True)
    total_price=models.IntegerField(default=0)
    quantity=models.IntegerField(default=1)

    def __str__(self):
        return self.item.title

    def get_total_item_price(self):
        if self.vendor.location == self.user.location:
            self.total_price= self.quantity * (self.item.price+ self.item.delivery_fee)

        else:
            self.total_price= self.quantity * (self.item.price + self.item.different_location_fee)

        super().save()


class Order(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete= models.CASCADE)
    items=models.ManyToManyField(OrderItem)
    is_ordered=models.BooleanField(default=False)
    is_delivered=models.BooleanField(default=False)
    start_date=models.DateTimeField(auto_now_add=True)
    ref=models.CharField(max_length=200,null=True,blank=True)
    delivery_location=models.CharField(max_length=40,null=True,blank=True)

    def __str__(self):
        return self.user.fullname

    def get_total(self):
        total=0
        for order_item in self.items.all():
            total+=order_item.get_total_item_price()

        return total

    def set_orderitem_total(self):
        for order_item in self.items.all():
            order_item.get_total_item_price()



class Payment(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete= models.CASCADE)
    amount=models.PositiveIntegerField()
    email=models.EmailField()
    ref=models.CharField(max_length=200)
    verified=models.BooleanField(default=False)
    date_created=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=('-date_created',)

    def __str__(self):
        return str(self.amount)

    def save(self,*args,**kwargs):
        while not self.ref:
            ref=secrets.token_urlsafe(50)
            obj_with_similar_ref=Payment.objects.filter(ref=ref)
            if not obj_with_similar_ref:
                self.ref=ref


        super().save(*args,**kwargs)

    def amount_value(self):
        return self.amount * 100

    def verify_payment(self):
        paystack = PayStack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.verified = True
                self.save()
        if self.verified:
            return True
        return False
