"""
Main entry point for glmpynet.
"""
import logging


def main():
    """
    Initializes and runs the glmpynet workflow.

    """
    # Configure the root logger for the application.
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


if __name__ == "__main__":
    main()
