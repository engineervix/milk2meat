import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from milk2meat.bible.models import Book
from milk2meat.notes.models import Note, NoteType

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo notes for development purposes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of notes to create (default: 20)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force creation even if not in development",
        )

    def handle(self, *args, **options):
        # Check if we're in development
        if not settings.DEBUG and not options["force"]:
            self.stdout.write(
                self.style.ERROR("This command can only run in development mode. Use --force to override.")
            )
            return

        count = options["count"]
        fake = Faker("es")

        # Get or create a superuser to be the owner of notes
        owner = self._get_or_create_superuser()
        self.stdout.write(f"Using user: {owner.email} as the note owner")

        # Get or create note types
        note_types = self._get_or_create_note_types()
        self.stdout.write(f"Created/Found {len(note_types)} note types")

        # Get Bible books
        books = Book.objects.all()
        if not books.exists():
            self.stdout.write(self.style.WARNING("No Bible books found. Run 'populate_bible_books' command first."))
            return

        # Generate tags
        tags = self._generate_tags()
        self.stdout.write(f"Using {len(tags)} tags for notes")

        # Create notes
        notes_created = 0
        for _ in range(count):
            self._create_note(fake, owner, note_types, books, tags)
            notes_created += 1
            if notes_created % 10 == 0:
                self.stdout.write(f"Created {notes_created} notes so far...")

        self.stdout.write(self.style.SUCCESS(f"Successfully created {notes_created} demo notes!"))

    def _get_or_create_superuser(self):
        # Try to get the first superuser
        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            return superuser

        # No superusers exist, create one
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword",
        )
        superuser.first_name = "Admin"
        superuser.last_name = "User"
        superuser.save()
        return superuser

    def _get_or_create_note_types(self):
        # Define note types that might be useful for Bible study
        note_type_definitions = [
            {"name": "Bible Study", "description": "In-depth study of Bible passages"},
            {"name": "Sermon Notes", "description": "Notes from sermons"},
            {"name": "Devotional", "description": "Personal devotional reflections"},
            {"name": "Exhortation", "description": "Exhortations prepared for church"},
            {"name": "Book Review", "description": "Reviews of Christian books"},
            {"name": "Family Devotion", "description": "Devotions prepared for family worship"},
            {"name": "Prayer Journal", "description": "Recording prayers and answers to prayer"},
            {"name": "Character Study", "description": "Study of Biblical characters"},
            {"name": "Theological Study", "description": "Explorations of theological concepts"},
            {"name": "Scripture Memorization", "description": "Notes to aid scripture memorization"},
        ]

        note_types = []
        for type_def in note_type_definitions:
            note_type, created = NoteType.objects.get_or_create(
                name=type_def["name"],
                defaults={"description": type_def["description"]},
            )
            note_types.append(note_type)

        return note_types

    def _generate_tags(self):
        # Define potential tags relevant to Bible study
        return [
            "salvation",
            "faith",
            "grace",
            "gospel",
            "Jesus",
            "prayer",
            "worship",
            "sin",
            "redemption",
            "covenant",
            "prophecy",
            "wisdom",
            "love",
            "mercy",
            "justice",
            "holiness",
            "sanctification",
            "sovereignty",
            "trinity",
            "discipleship",
            "mission",
            "atonement",
            "justification",
            "election",
            "eschatology",
            "pentateuch",
            "historical-books",
            "prophets",
            "gospels",
            "epistles",
            "revelation",
            "parables",
            "miracles",
            "creation",
            "fall",
            "exodus",
            "kingdom",
            "church",
            "heaven",
            "hell",
            "end-times",
            "spiritual-gifts",
            "fruit-of-spirit",
            "sermon-on-mount",
            "ten-commandments",
            "lords-prayer",
            "apologetics",
            "hermeneutics",
            "typology",
        ]

    def _create_note(self, fake, owner, note_types, books, tags):
        # Select random note type
        note_type = random.choice(note_types)

        # Create timestamps within the last year
        now = timezone.now()
        days_ago = random.randint(0, 365)
        created_at = now - timedelta(days=days_ago)
        updated_at = created_at + timedelta(days=random.randint(0, min(days_ago, 30)))

        # Generate title and content using Faker
        title = f"{note_type.name}: {fake.sentence().replace('.', '').title()}"

        # Generate paragraphs of content
        paragraphs = []
        paragraphs.append(f"# {title}")

        # Add 3-6 paragraphs
        for _ in range(random.randint(3, 6)):
            paragraphs.append(fake.paragraph(nb_sentences=random.randint(4, 10)))

        # Add a scripture reference
        book = random.choice(books)
        chapter = random.randint(1, max(1, book.chapters))
        verse_start = random.randint(1, 20)
        verse_end = verse_start + random.randint(0, 10)
        paragraphs.append(f"> {book.title} {chapter}:{verse_start}-{verse_end}")

        # Add reflection questions
        paragraphs.append("## Reflection Questions")
        for _ in range(3):
            paragraphs.append(f"- {fake.sentence()}")

        # Join content
        content = "\n\n".join(paragraphs)

        # Create note
        note = Note.objects.create(
            title=title,
            content=content,
            note_type=note_type,
            owner=owner,
            created_at=created_at,
            updated_at=updated_at,
        )

        # Add referenced books (0-3 books)
        num_books = random.randint(0, 3)
        if num_books > 0:
            referenced_books = random.sample(list(books), min(num_books, books.count()))
            note.referenced_books.add(*referenced_books)

        # Add tags (1-5 tags)
        num_tags = random.randint(1, 5)
        selected_tags = random.sample(tags, num_tags)
        note.tags.add(*selected_tags)

        return note
