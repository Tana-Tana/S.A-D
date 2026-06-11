"""
Django management command: export_behavior_csv

Xuat bang user_behavior_events ra file CSV (user_id, product_id, action, timestamp)
de huan luyen lai cac model trong ai-service.
"""
import csv

from django.core.management.base import BaseCommand

from products.models import UserBehaviorEvent


class Command(BaseCommand):
    help = "Xuat user_behavior_events ra file CSV (user_id, product_id, action, timestamp)"

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default='/app/data_export.csv')

    def handle(self, *args, **options):
        output = options['output']
        qs = UserBehaviorEvent.objects.all().order_by('user_id', 'created_at')

        count = 0
        with open(output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'product_id', 'action', 'timestamp'])
            for ev in qs.iterator():
                writer.writerow([ev.user_id, ev.product_id, ev.action,
                                  ev.created_at.strftime('%Y-%m-%d %H:%M:%S')])
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Da xuat {count} dong -> {output}"))
