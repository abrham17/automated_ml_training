from django.core.management.base import BaseCommand

from ...ml import augment_dataset_with_synthetic, train_and_save_model


class Command(BaseCommand):
    help = "Retrain the price prediction model with newly augmented data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--rows",
            type=int,
            default=200,
            help="Number of synthetic rows to add before retraining",
        )

    def handle(self, *args, **options):
        rows = options["rows"]
        df = augment_dataset_with_synthetic(num_new_rows=rows)
        model_path = train_and_save_model(df)
        self.stdout.write(self.style.SUCCESS(f"Model retrained and saved to {model_path}"))
