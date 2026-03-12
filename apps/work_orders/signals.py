"""
Work Order Signals

Django signals for status synchronization and automated workflows (Phase 5).
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.work_orders.models import WorkOrder, WorkOrderLine
from apps.inspections.models import InspectionDefect


@receiver(post_save, sender=WorkOrder)
def sync_defect_status_on_work_order_save(sender, instance, created, **kwargs):
    """
    Synchronize defect status and update asset meters when work order is updated.

    Status mapping:
    - WorkOrder COMPLETED → Defect RESOLVED
    - WorkOrder CANCELLED → Defect OPEN

    Meter updates:
    - WorkOrder COMPLETED → Update asset odometer/engine hours
    """
    # Update asset meters if work order is completed
    if instance.status == 'COMPLETED':
        instance.update_asset_meters()

    # Sync defect status
    if instance.source_type != 'INSPECTION_DEFECT':
        return

    if not instance.source_id:
        return

    # Try to get associated defect
    try:
        defect = InspectionDefect.objects.get(id=instance.source_id)
    except InspectionDefect.DoesNotExist:
        # Source might be inspection, not individual defect
        return

    # Update defect status based on work order status
    if instance.status == 'COMPLETED' and defect.status != 'RESOLVED':
        defect.status = 'RESOLVED'
        defect.save()
    elif instance.status == 'CANCELLED' and defect.status == 'WORK_ORDER_CREATED':
        # Work order cancelled, revert defect to open
        defect.status = 'OPEN'
        defect.save()


@receiver(post_delete, sender=WorkOrder)
def sync_defect_status_on_work_order_delete(sender, instance, **kwargs):
    """
    Synchronize defect status when work order is deleted.

    If work order is deleted, revert defect status to OPEN.
    """
    if instance.source_type != 'INSPECTION_DEFECT':
        return

    if not instance.source_id:
        return

    try:
        defect = InspectionDefect.objects.get(id=instance.source_id)

        # Revert defect to open if work order is deleted
        if defect.status == 'WORK_ORDER_CREATED':
            defect.status = 'OPEN'
            defect.save()
    except InspectionDefect.DoesNotExist:
        pass


@receiver(post_save, sender=WorkOrderLine)
def auto_complete_work_order(sender, instance, created, **kwargs):
    """
    Automatically complete work order when all lines are completed.

    This is a convenience feature - work orders can also be manually completed.
    """
    if instance.status != 'COMPLETED':
        return

    work_order = instance.work_order

    # Check if this was the last incomplete line
    incomplete_count = work_order.lines.exclude(status='COMPLETED').count()

    if incomplete_count == 0 and work_order.status != 'COMPLETED':
        # All lines completed, auto-complete work order
        work_order.status = 'COMPLETED'

        if not work_order.completed_at:
            from django.utils import timezone
            work_order.completed_at = timezone.now()

        work_order.save()
