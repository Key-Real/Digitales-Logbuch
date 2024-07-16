from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError
import json
from digilog_backend.models import User, Course
from pprint import pprint


class Command(BaseCommand):
    help = 'Import Course Data'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--file',
            dest='file',
            default=None,
            help='json file to import from',
        )

    def handle(self, *args, **options):
        from pprint import pprint
        file = options.get('file')

        if not file:
            raise CommandError("--file FILENAME is required")
        if not file.endswith('.json'):
            raise CommandError("file has to be a json file")

        with open(file, 'r') as f:
            entries = json.load(f)

            for entry in entries:
                e = {}
                e["host"] = User.objects.first()
                e["qualification"] = entry.get("Qualifizierungsbereich", "")[:Course.qualification.max_length]
                e["title"] = entry.get("Titel des Kurses", "")[:Course.title.max_length]
                e["level"]=entry.get('Level', "I").split(" ")[0][:Course.level.max_length]
                e["requirements"]= entry.get("Material/Unterlagen", "")[:Course.requirements.max_length]
                e["description_short"] = entry.get("Kurzbeschreibung/Untertitel des Moduls")[:Course.description_short.max_length]
                e["content_list"] = entry.get("Inhalte des Kurses", "")[:Course.content_list.max_length]
                e["methods"]=entry.get("methods", "")[:Course.methods.max_length]
                e["material"] = entry.get("Material/Unterlagen", "")[:Course.material.max_length]
                e["dates"] = entry.get("Wie oft wird der Kurs angeboten", "")[:Course.dates.max_length]
                e["duration"] = entry.get("Kursdauer", "")[:Course.duration.max_length]
                
                try:
                    course = Course.objects.get_or_create(title=e.pop("title"), defaults=e)
                    print(course)
                except Exception as e:
                    print([(key, len(str(val))) for key, val in e.items()])
                    pprint(e)
                    pprint(e)
                
