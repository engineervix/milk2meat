from django.core.management.base import BaseCommand

from milk2meat.bible.models import Book, Testament


class Command(BaseCommand):
    help = "Populate the database with Bible books data"

    def handle(self, *args, **options):
        # Check if books already exist
        if Book.objects.exists():
            self.stdout.write(self.style.WARNING("Bible books already exist in the database. Command aborted."))
            return

        # Bible books data with most common abbreviations
        bible_books = [
            # Old Testament (OT)
            {"title": "Genesis", "abbreviation": "Gen.", "testament": Testament.OT, "number": 1, "chapters": 50},
            {"title": "Exodus", "abbreviation": "Ex.", "testament": Testament.OT, "number": 2, "chapters": 40},
            {"title": "Leviticus", "abbreviation": "Lev.", "testament": Testament.OT, "number": 3, "chapters": 27},
            {"title": "Numbers", "abbreviation": "Num.", "testament": Testament.OT, "number": 4, "chapters": 36},
            {"title": "Deuteronomy", "abbreviation": "Deut.", "testament": Testament.OT, "number": 5, "chapters": 34},
            {"title": "Joshua", "abbreviation": "Josh.", "testament": Testament.OT, "number": 6, "chapters": 24},
            {"title": "Judges", "abbreviation": "Judg.", "testament": Testament.OT, "number": 7, "chapters": 21},
            {"title": "Ruth", "abbreviation": "Ruth", "testament": Testament.OT, "number": 8, "chapters": 4},
            {"title": "1 Samuel", "abbreviation": "1 Sam.", "testament": Testament.OT, "number": 9, "chapters": 31},
            {"title": "2 Samuel", "abbreviation": "2 Sam.", "testament": Testament.OT, "number": 10, "chapters": 24},
            {"title": "1 Kings", "abbreviation": "1 Kings", "testament": Testament.OT, "number": 11, "chapters": 22},
            {"title": "2 Kings", "abbreviation": "2 Kings", "testament": Testament.OT, "number": 12, "chapters": 25},
            {
                "title": "1 Chronicles",
                "abbreviation": "1 Chron.",
                "testament": Testament.OT,
                "number": 13,
                "chapters": 29,
            },
            {
                "title": "2 Chronicles",
                "abbreviation": "2 Chron.",
                "testament": Testament.OT,
                "number": 14,
                "chapters": 36,
            },
            {"title": "Ezra", "abbreviation": "Ezra", "testament": Testament.OT, "number": 15, "chapters": 10},
            {"title": "Nehemiah", "abbreviation": "Neh.", "testament": Testament.OT, "number": 16, "chapters": 13},
            {"title": "Esther", "abbreviation": "Est.", "testament": Testament.OT, "number": 17, "chapters": 10},
            {"title": "Job", "abbreviation": "Job", "testament": Testament.OT, "number": 18, "chapters": 42},
            {"title": "Psalms", "abbreviation": "Ps.", "testament": Testament.OT, "number": 19, "chapters": 150},
            {"title": "Proverbs", "abbreviation": "Prov", "testament": Testament.OT, "number": 20, "chapters": 31},
            {
                "title": "Ecclesiastes",
                "abbreviation": "Eccles.",
                "testament": Testament.OT,
                "number": 21,
                "chapters": 12,
            },
            {
                "title": "Song of Solomon",
                "abbreviation": "Song",
                "testament": Testament.OT,
                "number": 22,
                "chapters": 8,
            },
            {"title": "Isaiah", "abbreviation": "Isa.", "testament": Testament.OT, "number": 23, "chapters": 66},
            {"title": "Jeremiah", "abbreviation": "Jer.", "testament": Testament.OT, "number": 24, "chapters": 52},
            {"title": "Lamentations", "abbreviation": "Lam.", "testament": Testament.OT, "number": 25, "chapters": 5},
            {"title": "Ezekiel", "abbreviation": "Ezek.", "testament": Testament.OT, "number": 26, "chapters": 48},
            {"title": "Daniel", "abbreviation": "Dan.", "testament": Testament.OT, "number": 27, "chapters": 12},
            {"title": "Hosea", "abbreviation": "Hos.", "testament": Testament.OT, "number": 28, "chapters": 14},
            {"title": "Joel", "abbreviation": "Joel", "testament": Testament.OT, "number": 29, "chapters": 3},
            {"title": "Amos", "abbreviation": "Amos", "testament": Testament.OT, "number": 30, "chapters": 9},
            {"title": "Obadiah", "abbreviation": "Obad.", "testament": Testament.OT, "number": 31, "chapters": 1},
            {"title": "Jonah", "abbreviation": "Jonah", "testament": Testament.OT, "number": 32, "chapters": 4},
            {"title": "Micah", "abbreviation": "Mic.", "testament": Testament.OT, "number": 33, "chapters": 7},
            {"title": "Nahum", "abbreviation": "Nah.", "testament": Testament.OT, "number": 34, "chapters": 3},
            {"title": "Habakkuk", "abbreviation": "Hab.", "testament": Testament.OT, "number": 35, "chapters": 3},
            {"title": "Zephaniah", "abbreviation": "Zeph.", "testament": Testament.OT, "number": 36, "chapters": 3},
            {"title": "Haggai", "abbreviation": "Hag.", "testament": Testament.OT, "number": 37, "chapters": 2},
            {"title": "Zechariah", "abbreviation": "Zech.", "testament": Testament.OT, "number": 38, "chapters": 14},
            {"title": "Malachi", "abbreviation": "Mal.", "testament": Testament.OT, "number": 39, "chapters": 4},
            # New Testament (NT)
            {"title": "Matthew", "abbreviation": "Matt.", "testament": Testament.NT, "number": 40, "chapters": 28},
            {"title": "Mark", "abbreviation": "Mark", "testament": Testament.NT, "number": 41, "chapters": 16},
            {"title": "Luke", "abbreviation": "Luke", "testament": Testament.NT, "number": 42, "chapters": 24},
            {"title": "John", "abbreviation": "John", "testament": Testament.NT, "number": 43, "chapters": 21},
            {"title": "Acts", "abbreviation": "Acts", "testament": Testament.NT, "number": 44, "chapters": 28},
            {"title": "Romans", "abbreviation": "Rom.", "testament": Testament.NT, "number": 45, "chapters": 16},
            {
                "title": "1 Corinthians",
                "abbreviation": "1 Cor.",
                "testament": Testament.NT,
                "number": 46,
                "chapters": 16,
            },
            {
                "title": "2 Corinthians",
                "abbreviation": "2 Cor.",
                "testament": Testament.NT,
                "number": 47,
                "chapters": 13,
            },
            {"title": "Galatians", "abbreviation": "Gal.", "testament": Testament.NT, "number": 48, "chapters": 6},
            {"title": "Ephesians", "abbreviation": "Eph.", "testament": Testament.NT, "number": 49, "chapters": 6},
            {"title": "Philippians", "abbreviation": "Phil.", "testament": Testament.NT, "number": 50, "chapters": 4},
            {"title": "Colossians", "abbreviation": "Col.", "testament": Testament.NT, "number": 51, "chapters": 4},
            {
                "title": "1 Thessalonians",
                "abbreviation": "1 Thess.",
                "testament": Testament.NT,
                "number": 52,
                "chapters": 5,
            },
            {
                "title": "2 Thessalonians",
                "abbreviation": "2 Thess.",
                "testament": Testament.NT,
                "number": 53,
                "chapters": 3,
            },
            {"title": "1 Timothy", "abbreviation": "1 Tim.", "testament": Testament.NT, "number": 54, "chapters": 6},
            {"title": "2 Timothy", "abbreviation": "2 Tim.", "testament": Testament.NT, "number": 55, "chapters": 4},
            {"title": "Titus", "abbreviation": "Titus", "testament": Testament.NT, "number": 56, "chapters": 3},
            {"title": "Philemon", "abbreviation": "Philem.", "testament": Testament.NT, "number": 57, "chapters": 1},
            {"title": "Hebrews", "abbreviation": "Heb.", "testament": Testament.NT, "number": 58, "chapters": 13},
            {"title": "James", "abbreviation": "James", "testament": Testament.NT, "number": 59, "chapters": 5},
            {"title": "1 Peter", "abbreviation": "1 Pet.", "testament": Testament.NT, "number": 60, "chapters": 5},
            {"title": "2 Peter", "abbreviation": "2 Pet.", "testament": Testament.NT, "number": 61, "chapters": 3},
            {"title": "1 John", "abbreviation": "1 John", "testament": Testament.NT, "number": 62, "chapters": 5},
            {"title": "2 John", "abbreviation": "2 John", "testament": Testament.NT, "number": 63, "chapters": 1},
            {"title": "3 John", "abbreviation": "3 John", "testament": Testament.NT, "number": 64, "chapters": 1},
            {"title": "Jude", "abbreviation": "Jude", "testament": Testament.NT, "number": 65, "chapters": 1},
            {"title": "Revelation", "abbreviation": "Rev", "testament": Testament.NT, "number": 66, "chapters": 22},
        ]

        # Create Book objects
        books_created = 0
        for book_data in bible_books:
            Book.objects.create(**book_data)
            books_created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully added {books_created} books of the Bible."))
