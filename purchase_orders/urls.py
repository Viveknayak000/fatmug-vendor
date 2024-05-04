from django.urls import path, include
from rest_framework import routers
from .views import PurchaseOrderViewSet

router = routers.DefaultRouter()
router.register("purchase_orders",PurchaseOrderViewSet)

urlpatterns = [
    path('', include(router.urls))
]