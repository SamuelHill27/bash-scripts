# weblink

### description
bash script designed to create .desktop files for urls. The .desktop file will open in your default browser.

### execution
the bash file takes two arguments: a name and url.
For example, to create a .desktop file for www.google.com, you would execute the command 'weblink Google www.google.com'

### installation
download the script and put it somewhere you have permissions to access e.g. your home folder (I have a $HOME/bin folder)
ensure that the folder where you place the bash file is on your $PATH. Your path can be edited by opening the bash_rc and bash_profile files in your home directory.

### extra
If you want to add an icon to the weblink .desktop file, place pngs of the same name as the first argument (e.g. Google) at $HOME/Pictures/weblink-icons
