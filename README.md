# WallifyAI
WallifyAI is an AI-powered desktop application that generates custom wallpapers from user prompts using advanced image generation models. Enter a prompt, and WallifyAI creates and sets your wallpaper—instantly transforming your desktop with AI-generated visuals.




1. python -m venv .venv

2. $ source .venv/Scripts/activate

3. pip install -r requirements.txt

or manually install following packages: 

pip install <package name> 

Requirement packages: 

altgraph
certifi
charset-normalizer
comtypes
idna
packaging
pefile
Pillow
piexif
pyinstaller
pywin32
requests
setuptools
ttkthemes
urllib3



4. Change your code

5. build the applicaiton 
pyinstaller --onefile --windowed WallifyAI.py  or .venv\Scripts\activate && pyinstaller --onefile --windowed WallifyAI.py
