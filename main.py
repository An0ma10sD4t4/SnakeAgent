import sys
import os
import ctypes
import platform
import subprocess
import winreg as reg
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QMovie
from dotenv import load_dotenv

class WallpaperChanger( QMainWindow ):
    def __init__( self ):
        super().__init__()
        
        load_dotenv()

        self.initUI()        

    def initUI( self ):
        self.setWindowTitle( 'Wallpaper Changer' )
        self.setGeometry( 200, 200, 400, 300 )

        central_widget = QWidget()
        self.setCentralWidget( central_widget )

        self.label = QLabel( 'No Image Selected', self )
        # self.label.setAlignment( Qt.AlignCenter )
        self.button_select = QPushButton( 'Select Image', self )
        self.button_select.clicked.connect( self.select_image )
        self.button_set = QPushButton( 'Set Wallpaper', self )
        self.button_set.clicked.connect( self.set_wallpaper )

        layout = QVBoxLayout()
        layout.addWidget( self.label )
        layout.addWidget( self.button_select )
        layout.addWidget( self.button_set )

        central_widget.setLayout( layout )

    def select_image( self ):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName( 
            self, 
            'QFileDialog.getOpenFileName()', 
            '', 
            'Images ( *.png *.xpm *.jpg *.jpeg *.bmp *.gif );;All files ( * )', 
            options=options 
        )

        if file_name:
            if file_name.endswith == '.gif':
                self.display_gif( gif=file_name )
            else:
                self.display_image( image=file_name )

            self.image_path = file_name
        else:
            QMessageBox.warning( self, 'Warning', 'No Image Selected' )
            return

    def display_image( self, image ):
        display_selected_image = QPixmap( image )
        self.label.setPixmap( display_selected_image.scaledToWidth( 500 ) )

    def display_gif( self, gif ):
        gif_movie = QMovie( gif )
        self.label.setMovie( gif_movie )
        gif_movie.start()

    def set_wallpaper( self ):
        image_path = self.image_path
        if not image_path:
            QMessageBox.warning( self, 'Warning', 'Please Choose and Image First' )
            return
        if not os.path.isfile( image_path ):
            QMessageBox.warning( self, 'Warning', 'File Does Not Exist' )
            return
        
        os_name = platform.system()
        if image_path.endswith == '.gif' and os_name == 'Windows':
            pass
        else:
            if os_name == 'Windows':
                self.set_static_wallpaper( image_path=image_path )
            elif os_name == 'Darwin':
                script = f"""osascript -e 'tell application "Finder" to set desktop picture to POSIX file "{image_path}"'"""
                os.system( script )
            elif os_name == "Linux":
                desktop_env = os.getenv("DESKTOP_SESSION")
                if desktop_env in ["gnome", "unity", "cinnamon", "mate"]:
                    os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{image_path}")
                elif desktop_env == "xfce":
                    os.system(f"xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s {image_path}")
                elif desktop_env == "lxde":
                    os.system(f"pcmanfm --set-wallpaper={image_path} --wallpaper-mode=stretch")
                else:
                    QMessageBox.warning(self, "Warning", "Your desktop environment is not supported!")

    def set_gif_wallpaper( self, image_path ):
        try:
            subprocess.run( [ 'livelywpf', '--file', image_path ], check=True )
        except Exception as error:
            QMessageBox.critical( self, 'Error', f'Failed to Set Gif Wallpaper: { error }' )

    def set_static_wallpaper( self, image_path ):
        try:
            ctypes.windll.user32.SystemParametersInfoW( 20, 0, image_path, 0 )
        except Exception as error:
            QMessageBox.critical( self, 'Error', f'Failded to Set Static Wallpaper: { error }' )

if __name__ == '__main__':
    app = QApplication( sys.argv )

    main_ex = WallpaperChanger()
    main_ex.show()

    sys.exit( app.exec_() )