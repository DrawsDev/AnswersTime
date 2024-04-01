pyinstaller --noconfirm --onefile --windowed --icon "./icon.ico" --name "Answers Time" --add-data "./scripts;scripts/" --add-data "./assets;assets/" --add-data "./data;data/"  "./main.py"
md "./NewTest"
copy "./icon.png" "./NewTest"
copy "./dist" "./NewTest"
rd "./dist" /s /Q
rd "./build" /s /Q
del "./Answers Time.spec" /Q