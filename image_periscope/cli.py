"""This module provides a command-line interface for the Image Viewer application."""
import argparse

from image_periscope.app import create_app


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(description="Start the image viewer web application.")
    parser.add_argument("port", type=int, help="The port number to run the web application on.")
    parser.add_argument("directory", type=str, help="The directory containing images to display.")

    args = parser.parse_args()

    app = create_app(args.directory)
    app.run(host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()
