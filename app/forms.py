from .models import *
from django import forms
from django.forms.models import inlineformset_factory

class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields='__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean_sub_category(self):
        sub=self.cleaned_data.get('sub_category')
        main=self.cleaned_data.get('main_category')
        cat=Category.objects.filter(main_category=main,sub_category=sub.title())
        if cat:
            raise forms.ValidationError("Category already exits")
        return sub.title()
    
       
class MainCategoryForm(forms.ModelForm):
    class Meta:
        model=MainCategory
        fields='__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    def clean_main_category(self):
        n=self.cleaned_data.get('main_category')
        cat=MainCategory.objects.filter(main_category=n.title())
        if cat:
            raise forms.ValidationError("Category already exists")
        return n.title()
    
class SliderForm(forms.ModelForm):
    class Meta:
        model=Slider
        fields='__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields='__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    def clean_halfstars(self):
        n=self.cleaned_data.get('halfstars')
        r=self.cleaned_data.get('ratings')
        
        if r=="12345":
            n=0
        return n


class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields=['subject','comment','image','rating']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
import re
class AddressForm(forms.ModelForm):
    class Meta:
        model=Address
        fields=['full_name','mobile_no','alternate_no','address','pin_code']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    def clean_mobile_no(self):
        m=self.cleaned_data.get('mobile_no')
        if re.match(r'^\d{10}$',m):
            return m
        else:
            raise forms.ValidationError("Enter valid number")
    def clean_pin_code(self):
        m=self.cleaned_data.get('pin_code')
        if re.match(r'^\d{6}$',m):
            return m
        else:
            raise forms.ValidationError("Enter valid pin code")
    def clean_alternate_no(self):
        m=self.cleaned_data.get('alternate_no')
        if re.match(r'^\d{10}$',m):
            return m
        else:
            raise forms.ValidationError("Enter valid number")
class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields=['delivery_date','delivery_status']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})