from inventory_management import views
from django.urls import path
from .views import VendorInventoryAPIView, SaleView, SaleItemView, QRCodeScannerView

#from .views import create_sale

# Initialize the router

urlpatterns = [
   # Endpoint for products
   path('products/', views.getProducts, name="getProducts"),
   path('sales/', SaleView.as_view(), name='create-sale'),  # Handles POST to create a sale
   path('sale-items/', SaleItemView.as_view(), name='create-sale-item'),   
   path('api/qr-scan/', QRCodeScannerView.as_view(), name='qr_code_scanner'),
   # Endpoint for inventory list
   path('inventory/', views.inventory_list, name='inventory-list'),
   # Endpoint for vendor and inventory API
   path('products-inventory/', VendorInventoryAPIView.as_view(), name='VendorInventoryAPIView'),
   # Endpoint for specific inventory item
   path('inventory/<int:pk>/', views.inventory_detail, name='inventory-detail'),
   
]
