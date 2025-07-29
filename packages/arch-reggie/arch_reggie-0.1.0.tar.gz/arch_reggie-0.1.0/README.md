# Arch Reggie

A Python package for checking professional registration status across various certification bodies, particularly useful for architecture.

It can check the NSW and QLD ARBs at the moment, but there's potential to add more in the future.

![A slow loris, looking at you](docs/slow_lorris.png)

## Installation

```bash
pip install arch-reggie
```

## Quick Start

```python
from reggie import RegistrationProcessor, ProcessingConfig

# Initialize with default configuration (works with standard CSV format)
processor = RegistrationProcessor()

# Process a CSV file - default expects columns: Email, Full Name, LinkedIn URL, State Board Name, Registration Number, State Board Code
results = processor.process_csv("path/to/your/registrations.csv")

# Save results as JSON
processor.save_json(results, "output.json")
```

## CSV Format

The default configuration expects a headerless CSV with these columns in order:

1. Email
2. Full Name
3. LinkedIn URL
4. State Board Name (e.g., "NSW Architects Registration Board")
5. Registration Number
6. State Board Code (e.g., "NSW", "QLD")

## Supported Registration Bodies

- NSW Architects Registration Board
- Board of Architects of Queensland
- ~Northern Territory Architects Board~ not yet
- ~Architects Registration Board of Victoria~ not yet
- ~Registered Design Practitioner NSW~ not yet

## Configuration

The package works out-of-the-box with the standard CSV format, but supports custom configuration:

```python
from reggie import RegistrationProcessor, ProcessingConfig

# For different CSV formats, customize the configuration
config = ProcessingConfig(
    # If your CSV has different column names:
    column_names=["email", "name", "linkedin", "body", "number", "state"],
    email_column="email",
    full_name_column="name",

    # Processing options:
    check_registrations=True,  # Set to False to skip web scraping
    selenium_headless=True,    # Set to False to see browser window
    output_format="json"
)

processor = RegistrationProcessor(config=config)
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
