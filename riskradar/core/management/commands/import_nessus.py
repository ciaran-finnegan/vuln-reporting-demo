from django.core.management.base import BaseCommand
from core.nessus_scanreport_import import ScannerImporter
import os

class Command(BaseCommand):
    help = "Import one or more Nessus .nessus files and print import stats."

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            type=str,
            help="Path to a .nessus file or a directory containing .nessus files"
        )

    def handle(self, *args, **options):
        path = options["path"]
        importer = ScannerImporter("Nessus")

        if os.path.isdir(path):
            files = [
                os.path.join(path, f)
                for f in os.listdir(path)
                if f.endswith(".nessus")
            ]
        else:
            files = [path]

        if not files:
            self.stdout.write(self.style.WARNING("No .nessus files found."))
            return

        for file_path in files:
            self.stdout.write(f"Importing: {file_path}")
            try:
                stats = importer.import_file(file_path)
                self.stdout.write(self.style.SUCCESS(f"Stats: {stats}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error importing {file_path}: {e}")) 