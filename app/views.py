from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required,user_passes_test
from django.forms import inlineformset_factory,CheckboxInput
from django.contrib import messages
import qrcode
from django.core.mail import send_mail
import uuid
from .models import *
from datetime import datetime,timedelta
from .forms import *
import random
import razorpay
from django.core.files import File
from io import BytesIO

def home(r):
    slides=Slider.objects.all()
    cat=MainCategory.objects.all()
    return render(r,'index.html',{"slides":slides,"category":cat})
def search(r,query):
    pd=Product.objects.filter(name__icontains=query)| Product.objects.filter(category__main_category__main_category__icontains=query) | Product.objects.filter(category__sub_category__icontains=query)
    return render(r,'search.html',{"products":pd})

@login_required
def profile(r):
    return render(r,'account/profile.html')
def signin(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username.title(),password=password)
        if user is not None:
            login(request,user)
            if user.is_superuser:
                return redirect('/a')
            else:
                return redirect('home')
        else:
            messages.error(request,"Invalid login credentials")
    
    return render(request,'signin.html')
def register(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        password1=request.POST['password1']
        if password!=password1 :
            messages.error(request,"Passwords not matches")
        elif User.objects.filter(username=username.title()):
            messages.error(request,"Username already exists...!")
        elif User.objects.filter(email=email):
            messages.error(request,"Email already taken...!")
        elif len(password)<8:
            messages.error(request,"Password must be eight characters")
        else:
            User.objects.create_user(username=username.title(),email=email,password=password)
            user=authenticate(username=username.title(),password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
    return render(request,'signup.html')

def signout(request):
    logout(request)
    return redirect('home')

def shop(r):
    cat=MainCategory.objects.all()
    
    # print(product)
    product={}
    for i in cat:
        l=[]
        for j in Category.objects.filter(main_category=i.id):
            p=Product.objects.filter(category_id=j.id)
            if len(p)>0:
                l+=p
        if len(l)>0:
            random.shuffle(l)
            product[i]=l
        
    return render(r,'shop.html',{"products":product})

@login_required
def cart(r):
    items=Cart.objects.filter(user=r.user)
    subtotal=0
    shipping=0
    total=0
    for i in items:
        subtotal+=i.subtotal*i.quantity
        shipping+=i.shipping
        total+=i.total
    return render(r,'cart.html',{"items":items,"shipping":shipping,"subtotal":subtotal,"total":(total)})
@login_required
def addcart(r,q,id):
    p=Product.objects.get(id=id)
    Cart(user=r.user,product=p,quantity=q,subtotal=p.price*q,total=(p.price*q)+50).save()
    return redirect('/cart')
@login_required
def delcart(r,id):
    Cart.objects.get(id=id).delete()
    return redirect('/cart')
@login_required
def updatecart(r,q,id):
    c=Cart.objects.get(id=id)
    c.quantity=q
    c.total=(q*c.product.price)+50
    c.save()
    return redirect('/cart')
#addresses


@login_required
def addaddress(r):
    form=AddressForm()
    
    if r.method=="POST":
        form=AddressForm(r.POST)
        if form.is_valid():
            name=form.cleaned_data["full_name"]
            mobile_no=form.cleaned_data["mobile_no"]
            alternate_no=form.cleaned_data["alternate_no"]
            address=form.cleaned_data["address"]
            pincode=form.cleaned_data["pin_code"]   
            Address(user=r.user,full_name=name,mobile_no=mobile_no,alternate_no=alternate_no,address=address,pin_code=pincode).save()
            url=r.build_absolute_uri()
            url=url.split("?next=")
            if len(url)>1:
                return redirect(url[1])
            else:
                return redirect('/accounts/addresses')
    return render(r,'account/address.html',{"form":form})
@login_required
def editaddress(r,id):
    form=AddressForm(instance=Address.objects.get(id=id))
    if r.method=="POST":
        form=AddressForm(r.POST,instance=Address.objects.get(id=id))
        if form.is_valid():
            form.save()
            return redirect('/accounts/addresses')
    return render(r,'account/address.html',{"form":form})
@login_required
def deladdress(r,id):
    Address.objects.get(id=id).delete()
    return redirect('/accounts/addresses')
@login_required
def addresses(r):
    ad=Address.objects.filter(user=r.user)
    return render(r,'account/addresses.html',{"addresses":ad})


#orders
@login_required
def makeorder(r,id,q):
    ad=Address.objects.filter(user=r.user)
    product=Product.objects.get(id=id)
    client=razorpay.Client(auth=("rzp_test_euB1g3Ioe7wejB","k0phaX9LIQtibmploFiUPjs0"))
    payment=client.order.create({"amount":float(product.price*q*100+5000),'currency':'INR','payment_capture':1})
    if r.method=="POST":
        address=Address.objects.get(id=r.POST['address'])
        ecom=uuid.uuid4()
        if Order.objects.filter(ecommerce_id=ecom):
            ord=Order.objects.get(ecommerce_id=ecom)
            ord.address=address.address,
            ord.full_name=address.full_name,
            ord.mobile_no=address.mobile_no,
            ord.alternate_no=address.alternate_no,
            ord.pin_code=address.pin_code,
            ord.save()
            return redirect(f"/order/payment/{ord.id}")
        else:

            new_order=Order(
                    ecommerce_id=ecom,
                    order_id=payment['id'],
                    delivery_status="Pending",
                    user=r.user,
                    product=product,
                    quantity=q,
                    subtotal=q * product.price,
                    total=(q * product.price) + 50,
                    address=address.address,
                    full_name=address.full_name,
                    mobile_no=address.mobile_no,
                    alternate_no=address.alternate_no,
                    pin_code=address.pin_code,
                    order_date=datetime.today(),
                    delivery_date=datetime.today() + timedelta(days=7)
            )
            new_order.save()
            return redirect(f"/order/payment/{new_order.id}")
    return render(r,'makeorder.html',{"address":ad,"product":product,"quantity":q})
@login_required
def makecart(r):
    ad=Address.objects.filter(user=r.user)
    client=razorpay.Client(auth=("rzp_test_euB1g3Ioe7wejB","k0phaX9LIQtibmploFiUPjs0"))
    carts=Cart.objects.filter(user=r.user)
    total=0
    for i in carts:
        total+=i.total
    payment=client.order.create({"amount":float(total*100),'currency':'INR','payment_capture':1})
    if r.method=="POST":
        address=Address.objects.get(id=r.POST['address'])
        for i in carts:
            Order(ecommerce_id=uuid.uuid4(),order_id=payment['id'],delivery_status="Pending",user=r.user,product=i.product,quantity=i.quantity,subtotal=i.subtotal,total=i.total,address=address.address,
                    full_name=address.full_name,
                    mobile_no=address.mobile_no,
                    alternate_no=address.alternate_no,
                    pin_code=address.pin_code,order_date=datetime.today(),delivery_date=datetime.today()+timedelta(days=7)).save()
        return redirect(f"/cart/payment/{payment['id']}")
    return render(r,'makeorder.html',{"address":ad,"carts":carts})

@login_required
def orderpayment(r,id):
    ord=Order.objects.get(id=id)
    return render(r,'payment.html',{"order":ord})
@login_required
def cartpayment(r,id):
    return render(r,'payment.html',{"order_id":id})

def update_order(id,pay,status):
    ob=Order.objects.get(ecommerce_id=id)
    ob.payment_id=pay
    ob.order_status=True 
    ob.payment_status=status
    data=f'Ordered from eCommerce site\neCommerce id:{ob.ecommerce_id}\n\nOrder details\nOrder id:{ob.order_id}\nDate of order:{ob.order_date}\nDate of delivery:{ob.delivery_date}\nReturn before:{ob.delivery_date+timedelta(days=7)}\n\nUser details\nUsername:{ob.user.username}\nEmail:{ob.user.email}\n\nProduct details\nProduct Id:{ob.product.id}\nName:{ob.product.name}\nPrice:{ob.product.price}\nQuantity:{ob.quantity}\n\nDelivery details\nName:{ob.full_name}\nMobile NO:{ob.mobile_no},{ob.alternate_no}\nAddress:{ob.address}\nPin code:{ob.pin_code}\n\nPayment details\nPayment Id:{ob.payment_id}\nIspaid:{ob.payment_status}\nSubtotal:{ob.subtotal}\nShipping:{ob.shipping}\nTotal amount:{ob.total}'
    if not status:
        ob.delivery_status="Failed"
        data=f'Ordered from eCommerce site\neCommerce id:{ob.ecommerce_id}\n\nOrder details\nOrder id:{ob.order_id}\nDate of order:{ob.order_date}\n\nUser details\nUsername:{ob.user.username}\nEmail:{ob.user.email}\n\nProduct details\nProduct Id:{ob.product.id}\nName:{ob.product.name}\nPrice:{ob.product.price}\nQuantity:{ob.quantity}\n\nDelivery details\nName:{ob.full_name}\nMobile NO:{ob.mobile_no},{ob.alternate_no}\nAddress:{ob.address}\nPin code:{ob.pin_code}\n\nPayment details\nPayment Id:{ob.payment_id}\nIspaid:{ob.payment_status}\nSubtotal:{ob.subtotal}\nShipping:{ob.shipping}\nTotal amount:{ob.total}'
    send_mail("Order details",data,"",[ob.user.email])
    ob.save()
    qr=qrcode.make(data)
    stream=BytesIO()
    qr.save(stream,'PNG')
    ob.qrcode.save('qrcode.png',File(stream))
@login_required
def paysuccess(r,pay,id):
    for i in Order.objects.filter(order_id=id):
        update_order(i.ecommerce_id,pay,True)
    return redirect('/orders')
@login_required
def payfailed(r,pay,id):
    for i in Order.objects.filter(order_id=id):
        update_order(i.ecommerce_id,pay,False)
    return redirect('/orders')
@login_required
def cartsuccess(r,pay,id):
    for i in Order.objects.filter(order_id=id):
        update_order(i.ecommerce_id,pay,True)
    Cart.objects.filter(user=r.user).delete()
    return redirect('/orders')



#orders
@login_required
def orders(r):
    ord=Order.objects.filter(user=r.user).filter(order_status=True)
    return render(r,'orders.html',{"orders":ord})

@login_required
def orderdetails(r,id):
    i=Order.objects.get(ecommerce_id=id)
    returndate=i.delivery_date+timedelta(days=7)
    pending=0
    confirmed=0
    cancelled=0
    shipping=0
    shipped=0
    outfordelivery=0
    delivered=0
    returned=0
    refunded=0
    refundcancel=0
    cancel=0
    refund=0
    if i.delivery_status=="Pending":
        pending=1
    elif i.delivery_status=="Confirmed":
        confirmed=1
    elif i.delivery_status=="Cancelled":
        cancelled=1
    elif i.delivery_status=="Shipping":
        shipping=1
    elif i.delivery_status=="Shipped":
        shipped=1
    elif i.delivery_status=="Out for Delivery":
        outfordelivery=1
    elif i.delivery_status=="Delivered":
        delivered=1
    elif i.delivery_status=="Returned":
        returned=1
    elif i.delivery_status=="Refunded":
        refunded=1
    elif i.delivery_status=="Refund Cancel":
        refundcancel=1
    if pending or confirmed or shipped or shipping or outfordelivery:
        cancel=1
    if delivered and datetime.now().date()<=returndate:
        refund=1
    context={
        "i":i,
        "pending":pending,
        "returndate":returndate,
        "confirmed":confirmed,
        "cancelled":cancelled,
        "shipping":shipping,
        "shipped":shipped,
        "outfordelivery":outfordelivery,
        "returned":returned,
        "refunded":refunded,
        "refundcancel":refundcancel,
        "delivered":delivered,
        "cancel":cancel,
        "refund":refund
    }
    

    return render(r,'orderdetails.html',context)
@login_required
def cancelorder(r,id):
    o=Order.objects.get(id=id)
    o.delivery_status="Cancelled"
    o.save()
    return redirect(f'/order/{o.ecommerce_id}')
@login_required
def returnorder(r,id):
    o=Order.objects.get(id=id)
    o.delivery_status="Returned"
    o.save()
    return redirect(f'/order/{o.ecommerce_id}')

#admin
@user_passes_test(lambda u:u.is_superuser)
def dashboard(r):
    return render(r,'admin/home.html')

#categories
@user_passes_test(lambda u:u.is_superuser)
def categories(r):
    category=Category.objects.order_by("main_category")
    main=MainCategory.objects.all()
    form=MainCategoryForm()
    form1=CategoryForm()
    if r.method=="POST":
        if "cat1" in r.POST:
            form=MainCategoryForm(data=r.POST,files=r.FILES)
            if form.is_valid():
                form.save()
                return redirect("/a/categories")
        if "cat2" in r.POST:
            form1=CategoryForm(data=r.POST)
            if form1.is_valid():
                form1.save()
                return redirect("/a/categories")
    return render(r,'admin/categories.html',{"category":category,"form":form,"form1":form1,"main":main})

def categoryproduct(r,id):
    cat=Category.objects.filter(main_category_id=id)
    products={}
    for i in cat:
        p=Product.objects.filter(category_id=i.id)
        if len(p)>0:
            products[i.sub_category]=p
    print(products)
    return render(r,"pcategory.html",{"products":products})
@user_passes_test(lambda u:u.is_superuser)
def mancategory(r,mode,cate,id):
    form=MainCategoryForm()
    form1=CategoryForm()
    if cate=="m":
        ob=MainCategory.objects.get(id=id)
        if mode=="edit":
            form=MainCategoryForm(instance=ob)
        if mode=="delete":
            ob.delete()
            return redirect("/a/categories")
    if cate=="s":
        ob=Category.objects.get(id=id)
        if mode=="edit":
            form1=CategoryForm(instance=ob)
        if mode=="delete":
            ob.delete()
            return redirect("/a/categories")

    category=Category.objects.order_by("main_category")
    main=MainCategory.objects.all()
    
    if r.method=="POST":
        if "cat1" in r.POST:
            form=MainCategoryForm(data=r.POST,files=r.FILES,instance=ob)
            if form.is_valid():
                form.save()
                return redirect("/a/categories")
        if "cat2" in r.POST:
            form1=CategoryForm(data=r.POST,instance=ob)
            if form1.is_valid():
                form1.save()
                return redirect("/a/categories")
    return render(r,'admin/categories.html',{"category":category,"form":form,"form1":form1,"main":main})

#slider
@user_passes_test(lambda u:u.is_superuser)
def slider(r):
    form=SliderForm()
    slides=Slider.objects.all()
    if r.method=="POST":
        form=SliderForm(data=r.POST,files=r.FILES)
        if form.is_valid():
            form.save()
            return redirect('/a/slider')
    return render(r,"admin/slider.html",{"form":form,"slides":slides})
@user_passes_test(lambda u:u.is_superuser)
def manslider(r,mode,id):
    form=SliderForm()
    ob=Slider.objects.get(id=id)
    if mode=="edit":
        form=SliderForm(instance=ob)
    if mode=="delete":
        ob.delete()
        return redirect("/a/slider")

    slides=Slider.objects.all()
    if r.method=="POST":
        form=SliderForm(data=r.POST,files=r.FILES,instance=ob)
        if form.is_valid():
            form.save()
            return redirect('/a/slider')
    return render(r,"admin/slider.html",{"form":form,"slides":slides})

#products

def product(r,id):
    product=Product.objects.get(id=id)
    cat=product.category.main_category
    
    p=[[]]
    c=0
    for i in Product.objects.all():
        if i.category.main_category==cat:
            if i.id!=id:
                if len(p[c])<4:
                    p[c].append(i)
                else:
                    c+=1
                    p.append([])
                    p[c].append(i)
    main=[p[0]]
    p.pop(0)
    comments=Comment.objects.filter(product_id=id)
    form=CommentForm()
    if r.method=="POST":
        form=CommentForm(r.POST,r.FILES)
        if form.is_valid():

            Comment(user=r.user,product=Product.objects.get(id=id),comment=form.cleaned_data['comment'],image=form.cleaned_data['image'],rating=form.cleaned_data['rating'],subject=form.cleaned_data['subject'],empty="*"*(5-len(form.cleaned_data["rating"])),date=datetime.today()).save()
            return redirect(f'/product/{id}')
    return render(r,"product.html",{"p":product,"products":p,"main":main,"form":form,"comments":comments,"len":len(main[0])})
@user_passes_test(lambda u:u.is_superuser)
def addproduct(request):
    product_form = ProductForm(request.POST or None,request.FILES or None)
    images_formset = inlineformset_factory(Product, ProductImage, fields=('image',), extra=3,can_delete=True)(request.POST or None,request.FILES or None, instance=Product()) 
    for form in images_formset:
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            if isinstance(field.widget, CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
    if request.method == 'POST':
        
        if product_form.is_valid() and images_formset.is_valid():
            p = product_form.save()
            images_formset.instance = p
            images_formset.save()
            return redirect(f'/a/editproduct/{p.id}')
    return render(request, 'admin/addproduct.html', {'product_form': product_form, 'formset': images_formset})
@user_passes_test(lambda u:u.is_superuser)
def editproduct(request, id):
    p=Product.objects.get(id=id)
    product_form = ProductForm(request.POST or None,request.FILES or None,instance=p)
    images_formset = inlineformset_factory(Product, ProductImage, fields=('image',), extra=3,can_delete=True)(data=request.POST or None,files=request.FILES or None, instance=p) 
    for form in images_formset:
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            if isinstance(field.widget, CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
    if request.method == 'POST':
        if request.POST["ratings"]=="12345":
            print(product_form["name"])
        if product_form.is_valid() and images_formset.is_valid():
            product_form.save()
            images_formset.save()
            return redirect(f'/a/editproduct/{id}')
    
    return render(request, 'admin/addproduct.html', {'product_form': product_form, 'formset': images_formset,"pid":id})

@user_passes_test(lambda u:u.is_superuser)
def viewproducts(r):
    product=Product.objects.all()
    return render(r,"admin/viewproducts.html",{"product":product})
@user_passes_test(lambda u:u.is_superuser)
def deleteproduct(r,id):
    product=Product.objects.get(id=id)
    product.delete()
    return redirect("/a/viewproducts")
@user_passes_test(lambda u:u.is_superuser)
def comments(r):
    comments=Comment.objects.order_by("date")
    return render(r,'admin/comments.html',{"comments":comments})
@user_passes_test(lambda u:u.is_superuser)
def delcomment(r,id):
    Comment.objects.get(id=id).delete()
    return redirect('/a/comments')
@user_passes_test(lambda u:u.is_superuser)
def aorders(r):
    order=Order.objects.filter(order_status=True)
    return render(r,'admin/orders.html',{"orders":order})
@user_passes_test(lambda u:u.is_superuser)
def updateorder(r,id):
    order=Order.objects.get(id=id)
    form=OrderForm(instance=order)
    if r.method=="POST":
        form=OrderForm(r.POST,instance=order)
        if form.is_valid():
            form.save()
            update_order(order.ecommerce_id,order.payment_id,order.payment_status)
            return redirect(f'/a/orders')

    return render(r,'admin/updateorder.html',{"form":form,})
