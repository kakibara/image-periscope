# Image Viewer Web Application

This project is a simple web application that allows users to view images stored in a specified directory. The application maintains the directory structure and displays images in a gallery format.

## Project Structure

```
image-viewer
├── image_viewer
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

To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage

To start the web application, use the CLI command:

```
python -m image_viewer.cli <directory_path> <port_number>
```

Replace `<directory_path>` with the path to the directory containing your images and `<port_number>` with the desired port number.

## Features

- Displays images in a gallery format while preserving the directory structure.
- Simple command-line interface for easy usage.
- Built with Flask for a lightweight web application experience.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.