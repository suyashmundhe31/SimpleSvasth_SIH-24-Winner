from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
from rest_framework import viewsets
import cv2
import numpy as np
from .models import Inventory
from .serializers import InventorySerializer
from .models import Sales, Inventory, SalesItem, Vendors
from .serializers import VendorSerializer, InventorySerializer, SalesSerializer,SalesItemSerializer, Inqr


#this is how to create a api for the page
@api_view(['GET', 'POST'])
def getProducts(request):
    if request.method == 'GET':
        products = Vendors.objects.all()
        serializer = VendorSerializer(products, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
#Inventory
@api_view(['GET', 'POST'])
def inventory_list(request):
    if request.method == 'GET':
        inventories = Inventory.objects.all()
        serializer = InventorySerializer(inventories, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = InventorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def inventory_detail(request, pk):
    try:
        inventory = Inventory.objects.get(pk=pk)
    except Inventory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InventorySerializer(inventory)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = InventorySerializer(inventory, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        inventory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#this works without the api which you can also do

#Vendor Page Edit.js
class VendorInventoryAPIView(APIView):
    def post(self, request):
        vendor_data = request.data.get('Vendors')
        inventory_data = request.data.get('Inventory')

        if not vendor_data or not inventory_data:
            return Response({"error": "Missing Vendors or Inventory data"}, status=status.HTTP_400_BAD_REQUEST)

        # Create vendor
        vendor_serializer = VendorSerializer(data=vendor_data)
        if vendor_serializer.is_valid():
            vendor = vendor_serializer.save()
        else:
            return Response(vendor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create inventory items
        inventory_errors = []
        for item in inventory_data.get('surgical', []) + inventory_data.get('medicinal', []):
            item['Inv_vendor'] = vendor.name  # Use the vendor's name as the string identifier
            inventory_serializer = InventorySerializer(data=item)
            if inventory_serializer.is_valid():
                inventory_serializer.save()
            else:
                inventory_errors.append(inventory_serializer.errors)

        if inventory_errors:
            return Response({'inventory_errors': inventory_errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Data saved successfully"}, status=status.HTTP_201_CREATED)

#Sales Page
@api_view(['GET', 'POST'])
def sales_list(request):
    if request.method == 'GET':
        sales = Sales.objects.all()
        serializer = SalesSerializer(sales, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SalesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SaleView(APIView):
    def post(self, request):
        sale_serializer = SalesSerializer(data=request.data)
        if sale_serializer.is_valid():
            sale = sale_serializer.save()
            return Response({"id": sale.id}, status=status.HTTP_201_CREATED)
        return Response(sale_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        sales = Sales.objects.all()  # Fetch all sales from database
        sale_serializer = SalesSerializer(sales, many=True)  # Serialize all sales
        return Response(sale_serializer.data, status=status.HTTP_200_OK)


class SaleItemView(APIView):
    def post(self, request):
        sale_item_serializer = SalesItemSerializer(data=request.data)
        if sale_item_serializer.is_valid():
            try:
                sale_item_serializer.save()
                return Response(sale_item_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(sale_item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        sale_items = SalesItem.objects.all()  # Fetch all sale items from database
        sale_item_serializer = SalesItemSerializer(sale_items, many=True)  # Serialize the data
        return Response(sale_item_serializer.data, status=status.HTTP_200_OK)
    
class QRCodeScannerView(APIView):
    def post(self, request):
        # Receive image from frontend
        image = request.FILES.get('image')
        
        if not image:
            return Response({'error': 'No image uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Read image using OpenCV
        nparr = np.frombuffer(image.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Initialize QR Code detector
        qr_detector = cv2.QRCodeDetector()
        
        # Detect and decode QR Code
        data, bbox, _ = qr_detector.detectAndDecode(img)
        
        if not data:
            return Response({'error': 'No QR Code detected'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Assume QR code contains batch_number
            inventory_item = Inventory.objects.get(batch_number=data)
            
            # Check if item is available
            if inventory_item.Inv_quantity > 0:
                # Deduct one item from inventory
                inventory_item.Inv_quantity -= 1
                inventory_item.save()
                
                # Serialize and return updated item
                serializer = Inqr(inventory_item)
                return Response({
                    'message': 'Item deducted successfully', 
                    'item': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Item out of stock'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except Inventory.DoesNotExist:
            return Response({
                'error': 'No inventory item found with this batch number'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



