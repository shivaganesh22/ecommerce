from django.db import models
import os
from django.contrib.auth.models import User

# Create your models here.
class MainCategory(models.Model):
    main_category=models.CharField(max_length=30)
    img=models.ImageField(upload_to="category")
    def __str__(s):
        return s.main_category
class Category(models.Model):
    main_category=models.ForeignKey(MainCategory,on_delete=models.CASCADE)
    sub_category=models.CharField(max_length=30)
    def __str__(s):
        return str(s.main_category)+" "+s.sub_category
class Slider(models.Model):
    image=models.ImageField(upload_to="slider")
    redirect_url=models.URLField()
stars=(("1","1"),("12","2"),("123","3"),("1234","4"),("12345","5"))
hs=((0,"0"),(1,"1"))
class Product(models.Model):
    name=models.CharField(max_length=40)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    image=models.ImageField(upload_to="product")
    description=models.TextField()
    ratings=models.CharField(choices=stars,max_length=5)
    halfstars=models.IntegerField(choices=hs)
    
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    def __str__(s):
        return s.name
class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="product")


class Comment(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    subject=models.CharField(max_length=30)
    date=models.DateField()
    comment=models.TextField()
    image=models.ImageField(upload_to='comments',null=True,blank=True)
    rating=models.CharField(choices=(("1","1"),("12","2"),("123","3"),("1234","4"),("12345","5")),max_length=5)
    empty=models.CharField(max_length=5,null=True,blank=True)
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    subtotal=models.DecimalField(max_digits=10,decimal_places=2)
    shipping=models.IntegerField(default=50)
    total=models.DecimalField(max_digits=10,decimal_places=2)
class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=20)
    mobile_no=models.CharField(max_length=10)
    alternate_no=models.CharField(max_length=10)
    address=models.TextField()
    pin_code=models.CharField(max_length=6)

class Order(models.Model):
    payment_id=models.CharField(max_length=100,blank=True)
    order_id=models.CharField(max_length=100)
    ecommerce_id=models.CharField(max_length=100)
    payment_status=models.BooleanField(default=False)
    delivery_status=models.CharField(max_length=20,choices=(("Confirmed","Confirmed"),("Cancelled","Cancelled"),("Shipping","Shipping"),("Shipped","Shipped"),("Out for Delivery","Out for Delivery"),("Delivered","Delivered"),("Returned","Returned"),("Refunded","Refunded"),("Refund Cancel","Refund Cancel")))
    order_status=models.BooleanField(blank=True,default=False)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    subtotal=models.DecimalField(max_digits=10,decimal_places=2)
    shipping=models.IntegerField(default=50)
    total=models.DecimalField(max_digits=10,decimal_places=2)
    full_name=models.CharField(max_length=20)
    mobile_no=models.CharField(max_length=10)
    alternate_no=models.CharField(max_length=10)
    address=models.TextField()
    pin_code=models.CharField(max_length=6)
    order_date=models.DateField(null=True,blank=True)
    delivery_date=models.DateField(null=True,blank=True)
    qrcode=models.ImageField(null=True,blank=True,upload_to='qrcodes')
   

