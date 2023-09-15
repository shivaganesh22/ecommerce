"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from app.views import *

from allauth.account.views import *
from django.conf import settings
from django.conf.urls.static import static
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView

urlpatterns = [
    path('admin/', admin.site.urls),

    #user

    path("accounts/",include("allauth.urls")),
    path('',home,name='home'),
    path('profile',profile),
    path('search/<str:query>',search),
    path('accounts/login/',signin),
    path('accounts/register',register),
    path('logout/',signout), 
    path('shop',shop),
    path('cart',cart),
    path('cart/add/<int:q>/<int:id>',addcart),
    path('cart/del/<int:id>',delcart),
    path('cart/update/<int:q>/<int:id>',updatecart),
    #addresses
    path('accounts/addresses/',addresses),
    path('accounts/address/add/',addaddress),
    path('accounts/address/edit/<int:id>',editaddress),
    path('accounts/address/delete/<int:id>',deladdress),
    #order

    path('orders',orders),
    path('order/<str:id>',orderdetails),
    path('order/<int:id>/<int:q>/',makeorder),
    path('order/cart/',makecart),
    path('order/cancel/<int:id>',cancelorder),
    path('order/return/<int:id>',returnorder),
    path('order/payment/<str:id>/',orderpayment),
    path('cart/payment/<str:id>/',cartpayment),
    
    path('order/payment/success/<str:pay>/<str:id>',paysuccess),
    path('order/payment/failed/<str:pay>/<str:id>',payfailed),
    path('cart/payment/success/<str:pay>/<str:id>',cartsuccess),
 
   
    #admin
    path('a',dashboard),
    #category
    path('categories/<int:id>',categoryproduct),
    path('a/categories',categories),
    path('a/categories/<str:mode>/<str:cate>/<int:id>',mancategory),
    #slider
    path('a/slider',slider),
    path('a/slider/<str:mode>/<int:id>',manslider),
    #products
    path('a/addproduct',addproduct),
    path('product/<int:id>',product),
    path('a/editproduct/<int:id>',editproduct),
    path('a/deleteproduct/<int:id>',deleteproduct),
    path('a/viewproducts',viewproducts),
    #orders
    path('a/orders',aorders),
    path('a/order/update/<int:id>',updateorder),
    #comments
    path('a/comments',comments),
    path('a/comment/delete/<int:id>',delcomment)




]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
