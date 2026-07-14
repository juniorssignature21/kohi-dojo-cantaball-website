from django.shortcuts import render
from store import models as store_models

# Create your views here.
def shop(request):
    categories = store_models.Category.objects.all()
    products = store_models.Product.objects.all()
    
    context = {
        'categories': categories,
        'products': products
    }
    
    return render(request, 'store/shop.html', context)

def category_products(request, foo):
    category = store_models.Category.objects.get(slug=foo)
    products = store_models.Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products
    }
    
    return render(request, 'store/category_products.html', context)

def product_detail(request, foo):
    product = store_models.Product.objects.get(slug=foo)
    
    context = {
        'product': product
    }
    
    return render(request, 'store/product_detail.html', context)

