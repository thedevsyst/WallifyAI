# WallifyAI

WallifyAI is an AI-powered desktop application that generates custom wallpapers from user prompts using advanced image generation models. Enter a prompt, and WallifyAI creates and sets your wallpaper—instantly transforming your desktop with AI-generated visuals.

---

## Features

- **AI-Powered Wallpaper Generation**: Create stunning wallpapers using advanced AI models.
- **Customizable Prompts**: Enter your own prompts to generate unique visuals.
- **Professional Overlay Options**: Add overlays with customizable opacity, position, and color.
- **History Management**: Keep track of your recent prompts for easy reuse.
- **Multiple Display Styles**: Choose from styles like fill, fit, stretch, tile, center, and span.

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/thedevsyst/WallifyAI.git
   cd WallifyAI
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. Run the application:
   ```bash
   python WallifyAI.py
   ```

2. Enter a prompt in the application to generate a wallpaper.

3. Customize display settings and overlays as needed.

---

## Build Instructions

To build the application into a standalone executable:

1. Ensure all dependencies are installed.

2. Run the following command:
   ```bash
   pyinstaller --onefile --windowed WallifyAI.py
   ```

   Alternatively, if using a virtual environment:
   ```bash
   .venv\Scripts\activate && pyinstaller --onefile --windowed WallifyAI.py
   ```

---

## Requirements

The following Python packages are required:

- `altgraph`
- `certifi`
- `charset-normalizer`
- `comtypes`
- `idna`
- `packaging`
- `pefile`
- `Pillow`
- `piexif`
- `pyinstaller`
- `pywin32`
- `requests`
- `setuptools`
- `ttkthemes`
- `urllib3`

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For any inquiries or support, please contact:

- **Email**: [thedevsyst@gmail.com](mailto:thedevsyst@gmail.com)
- **GitHub**: [github.com/thedevsyst/WallifyAI](https://github.com/thedevsyst/WallifyAI)
- **Website**: [https://devsyst.com](https://devsyst.com)
