"""
Django management command: simulate_behavior

Sinh du lieu hanh vi nguoi dung (view/click/add_to_cart) va luu vao bang
user_behavior_events that (cung bang/model duoc API /events/ ghi vao),
dung de bootstrap "du lieu thuc te" cho AI service.
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from products.models import UserBehaviorEvent

NUM_USERS = 500
SEQ_LEN = 8
NUM_PRODUCTS = 17  # khop voi so san pham da seed
ACTIONS = ['view', 'click', 'add_to_cart']

PERSONAS = {
    'browser':    [0.80, 0.15, 0.05],
    'researcher': [0.35, 0.45, 0.20],
    'buyer':      [0.15, 0.30, 0.55],
}
PERSONA_WEIGHTS = [0.5, 0.3, 0.2]

# 1-8: electronics, 9-13: books, 14-17: fashion
CATEGORY_RANGES = [(1, 8), (9, 13), (14, 17)]


class Command(BaseCommand):
    help = "Sinh du lieu hanh vi nguoi dung (view/click/add_to_cart) vao bang user_behavior_events"

    def add_arguments(self, parser):
        parser.add_argument('--seed', type=int, default=123)
        parser.add_argument('--clear', action='store_true', help='Xoa du lieu cu truoc khi sinh')

    def handle(self, *args, **options):
        seed = options['seed']
        rng = random.Random(seed)

        if options['clear']:
            deleted, _ = UserBehaviorEvent.objects.all().delete()
            self.stdout.write(f"Da xoa {deleted} event cu.")

        now = timezone.now()
        events = []

        for user_id in range(1, NUM_USERS + 1):
            persona = rng.choices(list(PERSONAS.keys()), weights=PERSONA_WEIGHTS)[0]
            base_probs = PERSONAS[persona]
            cat_start, cat_end = rng.choice(CATEGORY_RANGES)

            # Moi user "duyet web" vao mot phien ngau nhien trong 60 ngay gan day
            ts = now - timedelta(
                days=rng.randint(0, 60), hours=rng.randint(0, 23), minutes=rng.randint(0, 59)
            )

            for step in range(SEQ_LEN):
                # Hieu ung "funnel": cang ve cuoi chuoi, xac suat add_to_cart cang tang
                shift = step / (SEQ_LEN - 1)
                adj = [
                    base_probs[0] * (1 - 0.5 * shift),
                    base_probs[1],
                    base_probs[2] * (1 + 1.0 * shift),
                ]
                total = sum(adj)
                adj = [p / total for p in adj]
                action = rng.choices(ACTIONS, weights=adj)[0]

                # 90% chon san pham trong category yeu thich, 10% kham pha ngau nhien
                if rng.random() < 0.90:
                    product_id = rng.randint(cat_start, cat_end)
                else:
                    product_id = rng.randint(1, NUM_PRODUCTS)

                events.append(UserBehaviorEvent(
                    user_id=user_id, product_id=product_id, action=action, created_at=ts
                ))
                ts += timedelta(minutes=rng.randint(1, 30))

        UserBehaviorEvent.objects.bulk_create(events, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(
            f"Da sinh {len(events)} behavior events ({NUM_USERS} user x {SEQ_LEN}) vao user_behavior_events."
        ))
