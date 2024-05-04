from django.db import models
from vendors.models import *
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save,pre_delete,post_delete
from django.dispatch import receiver
from django.db.models import Avg, F, ExpressionWrapper, fields
from django.db import transaction
from django.utils import timezone

class PurchaseOrder(models.Model):
    PURCHASE_STATUS = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    QUALITY_RATING_CHOICES = [
        (1.0, "1 - Poor"),
        (2.0, "2 - Below Average"),
        (3.0, "3 - Average"),
        (4.0, "4 - Good"),
        (5.0, "5 - Excellent"),
    ]
    po_number = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=50, choices=PURCHASE_STATUS, default='Pending')
    quality_rating = models.FloatField(choices=QUALITY_RATING_CHOICES, null=True, blank=True)
    issue_date = models.DateTimeField()
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.delivery_date <= self.order_date:
            raise ValidationError("Delivery date must be after order date.")

    def __str__(self):
        return self.po_number

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()


@receiver(post_save, sender=PurchaseOrder)
def update_vendor_metrics(sender, instance, created, **kwargs):
    vendor = instance.vendor

    completed_pos = PurchaseOrder.objects.filter(
        vendor=vendor, status='Completed')
    total_completed_pos = completed_pos.count()

    # on-time delivery rate calculation in percentage

    on_time_delivery_rate = completed_pos.filter(vendor=vendor, delivery_date__lte=timezone.now(
    )).count()/total_completed_pos * 100 if total_completed_pos > 0 else 0.0

    # average quality rating calculation(1 to 5 rating)

    total_rating = PurchaseOrder.objects.filter(vendor=vendor, quality_rating__isnull=False).aggregate(
        avg_quality_rating=Avg('quality_rating', default=0.0))

    average_quality_rating = total_rating.get('avg_quality_rating', 0.0)

    # response time calculation in minutes

    acknowledged_pos = completed_pos.filter(
        vendor=vendor, acknowledgment_date__isnull=False)

    response_time = acknowledged_pos.filter(vendor=vendor).aggregate(avg_response_time=Avg(ExpressionWrapper(
        F("acknowledgment_date") - F("issue_date"),
        output_field=fields.DurationField())))

    average_response_time = response_time.get('avg_response_time', 0.0)

    # fulfillment rate calculation in percentage

    issued_pos_count = PurchaseOrder.objects.filter(vendor=vendor).count()
    fulfillment_rate = total_completed_pos / \
        issued_pos_count*100 if issued_pos_count else 0.0

    # Update Vendor model
    vendor.on_time_delivery_rate = on_time_delivery_rate
    vendor.quality_rating_avg = average_quality_rating
    vendor.average_response_time = round(average_response_time.total_seconds() /
                                         60 if average_response_time else 0.0, 2)
    vendor.fulfillment_rate = fulfillment_rate

    vendor.save()

    # Update Performance model
    # transaction.atomic guarantees either the success of all operations or the complete rollback in case of any failure.
    with transaction.atomic():
        update_historical_performance = HistoricalPerformance.objects.create(
            vendor=vendor,
            date=timezone.now(),
            on_time_delivery_rate=on_time_delivery_rate,
            quality_rating_avg=average_quality_rating,
            average_response_time=round(average_response_time.total_seconds() /
                                        60 if average_response_time else 0.0, 2),
            fulfillment_rate=fulfillment_rate,

        )