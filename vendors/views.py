from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from django.db.models import Q
from .models import Vendor
from rest_framework.response import Response
from .serializers import VendorSerializer
from math import ceil
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    http_method_names = ['get','post','put','delete']

    scroll_param_config = openapi.Parameter(
        'scroll', in_=openapi.IN_QUERY,
        description='Scroll parameter for pagination, starting from 1',
        type=openapi.TYPE_INTEGER,
        required=True
    )

    def get_object(self):
        """
        Overrides the default method to retrieve an object by either its id or vendor_code.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        lookup_value = self.kwargs.get('pk')
        
        if lookup_value.isdigit():
            obj = queryset.filter(Q(id=lookup_value)).first()
        else:
            obj = queryset.filter(Q(vendor_code=lookup_value)).first()

        if obj is None:
            raise NotFound('A vendor with the given ID/vendor_code does not exist.')

        return obj


    @swagger_auto_schema(operation_summary="List all vendors",manual_parameters=[scroll_param_config],responses={status.HTTP_200_OK: VendorSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        """
        Return a list of all vendors, allowing pagination via infinite scrolling.
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

        paginated_vendors = self.get_queryset()[start_index:end_index]
        total_count = self.get_queryset().count()
        max_scroll = ceil(total_count / page_size)
        next_scroll = scroll + 1 if scroll < max_scroll else None

        serializer = self.get_serializer(paginated_vendors, many=True)
        response_data = {
            "instances": serializer.data,
            "max_scroll": max_scroll,
            "next_scroll": next_scroll,
            "total_instance_count": total_count
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific vendor's details",
        operation_description="Retrieves a single vendor by ID or vendor_code. The 'id' in the path can be an integer ID or a string vendor_code.",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_PATH, description="A unique integer value identifying this vendor or a string value as the vendor_code.",
                type=openapi.TYPE_STRING, required=True
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Create a new vendor")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a vendor's details",
        operation_description="Updates or partially updates an existing vendor by ID or vendor_code. Use PATCH for partial updates and PUT for full updates.",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_PATH, description="A unique integer value identifying this vendor or a string value as the vendor_code.",
                type=openapi.TYPE_STRING, required=True
            )
        ],
        responses={200: VendorSerializer}
    )
    def update(self, request, *args, **kwargs):
        """
        Overrides update method to handle both PUT and PATCH requests.
        PUT will expect all fields to be provided for a full update, while PATCH will only update fields that are provided.
        """
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a vendor",
        operation_description="Deletes a vendor by ID or vendor_code. The 'id' in the path can be an integer ID or a string vendor_code.",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_PATH, description="A unique integer value identifying this vendor or a string value as the vendor_code.",
                type=openapi.TYPE_STRING, required=True
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    

class VendorPerformanceView(APIView):
    def get(self, request, vendor_id):
        try:
            vendor = Vendor.objects.get(pk=vendor_id)
            data = {
                'on_time_delivery_rate': vendor.on_time_delivery_rate,
                'quality_rating_avg': vendor.quality_rating_avg,
                'average_response_time': vendor.average_response_time,
                'fulfillment_rate': vendor.fulfillment_rate
            }
            return Response(data)
        except Vendor.DoesNotExist:
            return Response({'error': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
