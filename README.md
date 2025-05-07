# SlowMailer

A Python tool for sending personalized emails in a human-like manner to improve deliverability and avoid spam filters.

## Features

- Human-like sending patterns with random delays (45-90 seconds between emails)
- Occasional longer breaks to mimic natural behavior
- Rotating user agents to reduce consistent fingerprinting
- Support for both HTML and plain text email formats
- Secure password storage using keyring
- Test mode for previewing emails without sending
- Detailed logging of all operations
- Resumable sending process
- CSV-based recipient data

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/SlowMailer.git
cd SlowMailer
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Prepare your recipient data in a CSV file (see `students.csv` for format)
2. Create your email templates with placeholders matching your CSV columns
3. Set up your email credentials:
   - Option 1: Use environment variables (create a `.env` file):
     ```
     EMAIL=your.email@example.com
     EMAIL_PASSWORD=your_password
     ```
   - Option 2: Enter credentials when prompted

4. Run the script:
```bash
python slow_mailer.py
```

## CSV Format

Your CSV file should include at least an 'email' column, plus any other columns you want to use in your email templates. Example:

```csv
email,first_name,last_name,course
student1@example.com,John,Doe,Computer Science
```

## Email Templates

You can use any column from your CSV as a placeholder in your templates using the format `{column_name}`. Example:

```python
subject_template = "Hello {first_name}, Welcome to {course}!"
html_template = """
<html>
    <body>
        <h1>Hello {first_name}!</h1>
        <p>Welcome to the {course} program.</p>
    </body>
</html>
"""
```

## Security

- Email passwords are stored securely using the system's keyring
- No sensitive data is stored in plain text
- Test mode available to preview emails without sending

## Logging

All operations are logged to both:
- Console output
- `slow_mailer.log` file

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.