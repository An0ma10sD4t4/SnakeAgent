import sys
import os
import ctypes
import platform
import winreg as reg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
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

        self.button_select = QPushButton( 'Select Image', self )
        self.button_select.clicked.connect( self.select_image )

        self.style_select = QComboBox()
        self.style_select.addItem( 'Center' )
        self.style_select.addItem( 'Tile' )
        self.style_select.addItem( 'Stretch' )
        self.style_select.addItem( 'Fit' )
        self.style_select.addItem( 'Fill' )
        self.style_select.addItem( 'Span' )

        self.button_set = QPushButton( 'Set Wallpaper', self )
        self.button_set.clicked.connect( self.set_wallpaper )

        layout = QVBoxLayout()
        layout.addWidget( self.label )
        layout.addWidget( self.button_select )
        layout.addWidget( self.style_select )
        layout.addWidget( self.button_set )

        central_widget.setLayout( layout )

    def select_image( self ):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName( 
            self, 
            'QFileDialog.getOpenFileName()', 
            '', 
            'Images ( *.png *.xpm *.jpg *.jpeg *.bmp );;All files ( * )', 
            options=options 
        )

        if file_name:
            display_selected_image = QPixmap( file_name )
            self.label.setPixmap( display_selected_image.scaledToWidth( 500 ) )

            self.image_path = file_name
        else:
            self.label.setText( 'No Image Selected' )

    def set_wallpaper( self ):
        image_path = self.image_path
        if not image_path:
            QMessageBox.warning( self, 'Warning', 'Please Choose and Image First' )
            return
        if not os.path.isfile( image_path ):
            QMessageBox.warning( self, 'Warning', 'File Does Not Exist' )
            return
        
        os_name = platform.system()

        if os_name == 'Windows':
            style_dict = {
                'Center': '0',
                'Tile': '1',
                'Stretch': '2',
                'Fit': '6',
                'Fill': '10',
                'Span': '22'
            }

            selected_style = self.style_select.currentText()
            if selected_style not in style_dict:
                QMessageBox.warning( self, 'Warning', 'Style Currently Unsupported' )
                return

            try:
                ctypes.windll.user32.SystemParametersInfoW( 20, 0, image_path, 0 )

                key = reg.OpenKey(reg.HKEY_CURRENT_USER, r'Control Panel\Desktop', 0, reg.KEY_SET_VALUE)
                reg.SetValueEx(key, 'WallpaperStyle', 0, reg.REG_SZ, style_dict[selected_style])
                reg.SetValueEx(key, 'TileWallpaper', 0, reg.REG_SZ, '0' if selected_style != 'Tile' else '1')
                key.Close()

                ctypes.windll.user32.SystemParametersInfoW( 20, 0, image_path, 3 )
            except Exception as e:
                QMessageBox.critical( self, 'Error', f'Failed To Set Wallpaper: { e }' )
                return
        
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

if __name__ == '__main__':
    app = QApplication( sys.argv )

    main_ex = WallpaperChanger()
    main_ex.show()

    sys.exit( app.exec_() )