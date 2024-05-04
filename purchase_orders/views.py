from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import PurchaseOrder
from drf_yasg import openapi
from django.utils import timezone
from math import ceil
from .serializers import PurchaseOrderSerializer, PurchaseOrderCreateSerializer
from rest_framework.decorators import action

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    http_method_names = ['get','post','put','delete']

    scroll_param_config = openapi.Parameter('scroll',in_=openapi.IN_QUERY,description='Scroll Param',type=openapi.TYPE_INTEGER,required=True)
    
    def get_serializer_class(self):
        """
        Return different serializers for different actions.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new purchase order with the specified details.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        """
        Enhance the default queryset to prefetch related vendor data.
        """
        return super().get_queryset().select_related('vendor')

    @swagger_auto_schema(
        manual_parameters=[scroll_param_config],
        responses={status.HTTP_200_OK: PurchaseOrderSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """
        Return a list of all purchase orders with infinite scrolling.
        The 'scroll' query parameter indicates the page number.
        """
        scroll = request.query_params.get('scroll')
        if not scroll:
            return Response({"message": "Scroll parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            scroll = int(scroll)
        except ValueError:
            return Response({"message": "Scroll parameter must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        page_size = 20
        start_index = (scroll - 1) * page_size
        end_index = start_index + page_size

        paginated_query = self.get_queryset()[start_index:end_index]
        serializer = self.get_serializer(paginated_query, many=True)
        
        total_count = self.get_queryset().count()
        max_scroll = ceil(total_count / page_size)
        next_scroll = scroll + 1 if scroll < max_scroll else None

        response_data = {
            "instances": serializer.data,
            "max_scroll": max_scroll,
            "next_scroll": next_scroll,
            "total_instance_count": total_count
        }

        return Response(response_data, status=status.HTTP_200_OK)


    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific purchase order by its ID.
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update an existing purchase order.
        """
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a purchase order.
        """
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge_purchase_order(self, request, pk=None):
        """
        Acknowledge a specific purchase order by its ID.
        """
        try:
            po = self.get_object()
            if po.acknowledgment_date is not None:
                return Response({'error': 'Purchase Order already acknowledged.'}, status=status.HTTP_400_BAD_REQUEST)

            po.acknowledgment_date = timezone.now()
            po.save()

            return Response({'status': 'Purchase Order acknowledged successfully.', 'acknowledgment_date': po.acknowledgment_date}, status=status.HTTP_200_OK)

        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)