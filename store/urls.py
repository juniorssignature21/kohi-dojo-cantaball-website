from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.shop, name='shop'),
    path('shop/category/<slug:foo>/', views.category_products, name='category_products'),
    path('shop/product/<slug:foo>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/', views.AddToCart, name='add_to_cart'),
    path('delete-cart-item/', views.delete_cart_item, name='delete_cart_item'),
    path('get-cart-count/', views.get_cart_count, name='get_cart_count'),
    path('checkout/<int:id>/', views.checkout, name='checkout'),
    path('create-order/', views.CreateOrder, name='create_order'),
    path('initialize-payment/<int:order_id>/', views.FlutterWavePayment, name='flutterwave_payment'),
    path('verify-payment/<int:order_id>/', views.PaymentCallback, name='payment_callback'),
    path('orders/', views.orders, name='orders'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('frontdesk/orders/', views.frontdesk_orders, name='frontdesk_orders'),
    path('frontdesk/orders/<int:order_id>/confirm/', views.confirm_order, name='confirm_order'),
    path('frontdesk/search-orders/', views.frontdesk_search_orders, name='frontdesk_search_orders'),
    path('frontdesk/orders/<int:order_id>/delivered/', views.mark_order_delivered, name='mark_order_delivered'),
    path('frontdesk/products/', views.frontdesk_products, name='frontdesk_products'),
    path('frontdesk/products/add/', views.add_product, name='add_product'),
    path('frontdesk/products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
]
