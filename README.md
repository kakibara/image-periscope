# Image Viewer Web Application

This project is a simple web application that allows users to view images stored in a specified directory. The application maintains the directory structure and displays images in a gallery format.

```bash
pipx install git+https://github.com/kakibara/image-periscope.git
```

## Project Structure

```
image-periscope
├── image_periscope
│   ├── __init__.py          # Initializes the package
│   ├── app.py               # Entry point for the Flask application
│   ├── cli.py               # CLI commands for launching the application
│   ├── image_utils.py       # Utility functions for image processing
│   └── templates            # HTML templates for the application
│       ├── index.html       # Index page template
│       └── gallery.html     # Gallery page template
├── tests
│   ├── __init__.py          # Initializes the test package
│   ├── test_app.py          # Unit tests for app.py
│   └── test_image_utils.py  # Unit tests for image_utils.py
├── setup.py                 # Package setup file
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## Installation

To install with pipx, run:
```bash
pipx install git+https://github.com/kakibara/image-periscope.git
```

## Usage

To start the web application, use the CLI command:

```bash
image-periscope <port_number> <directory_path> [--host <ip_address>]
```

-   `<port_number>`: The port number to run the web application on.
-   `<directory_path>`: The path to the directory containing your images.
-   `--host <ip_address>` (optional): The host IP to bind to. Defaults to `127.0.0.1` (localhost), which only allows access from the local machine. To allow access from other machines, use `0.0.0.0`.

Example:
```bash
# Run on port 8000, serving images from the current directory
# Accessible only from the local machine
image-periscope 8000 .

# Run on port 8888, serving images from /path/to/images
# Accessible from any IP address
image-periscope 8888 /path/to/images --host 0.0.0.0
```

## Features

-   Displays images in a gallery format while preserving the directory structure.
-   Simple command-line interface for easy usage.
-   Built with Flask for a lightweight web application experience.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
