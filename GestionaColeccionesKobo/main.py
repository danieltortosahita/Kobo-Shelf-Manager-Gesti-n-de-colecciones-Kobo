import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ConexionKOBO import libroElectronico
from UI import *
import cgitb 
import ConexionBBDD

# Para convertir ui a py:
# pyuic5 -x ui.ui -o ui.py

class AppWindow(QMainWindow):
    def __init__(self):
        
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        width = 832
        height = 380
        self.setFixedSize(width, height)
        self.setWindowIcon(QIcon("GestionaColeccionesKobo/img/favicon.ico"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        

        self.coleccionSeleccionada = ""
        self.unidad_kobo = ""
        self.mostrar_colecciones()
        
        

        self.ui.tblColecciones.itemClicked.connect(lambda: self.listar_archivos_coleccion())

        self.ui.btnComprobar.clicked.connect(lambda: self.mostrar_colecciones())
        self.ui.btnEliminaColeccion.clicked.connect(lambda: self.pregunta_eliminacion())
        self.ui.btnIncluyeLibroColeccion.clicked.connect(lambda: self.muestraArchivos())        
        self.ui.btnCreaColeccion.clicked.connect(lambda: self.crear_Coleccion())
        self.ui.btnEliminaLibroColeccion.clicked.connect(lambda: self.elimina_libro_coleccion())
        self.ui.btnModificarColeccion.clicked.connect(lambda: self.modifica_nombre_coleccion())

    def mostrar_colecciones(self):

        libro = libroElectronico()
        
        self.unidad_kobo = libro.comprueba_KOBO_conectado()
        #Para realizar pruebas en local:
        #self.unidad_kobo = "D:/"

        if self.unidad_kobo == "No detectado" and self.ui.cboUnidad.findText("No detectado") == -1:

            self.ui.cboUnidad.addItem(self.unidad_kobo)

        else:

            self.ui.cboUnidad.removeItem(0)
            self.ui.cboUnidad.addItem(self.unidad_kobo)            
            self.conexion = ConexionBBDD.BBDD(self.unidad_kobo)
            colecciones = self.conexion.consult_collections()
            tabla = self.ui.tblColecciones
            tabla.setRowCount(0)
            tabla.clearContents()

            for row_number, row_data in enumerate(colecciones):
                
                tabla.insertRow(row_number)

                for column_number, data in enumerate(row_data):

                    tabla.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            
            self.ui.lblColecciones.setText(str(len(colecciones)))       

    def muestraArchivos(self):

        if self.unidad_kobo == "":

            self.mensaje_aviso("Por favor, conecte el dispositivo.", "Warning")

        elif self.ui.txtColeccion.text() == "":

            self.mensaje_aviso("Por favor, seleccione una colección.", "Warning")

            
        else:

            fname = QFileDialog.getOpenFileNames(self, 'Open file', self.unidad_kobo, 'Archivos KOBO (*.epub ,*.epub3 ,*.flepub ,*.pdf ,*.mobi ,*.jpeg ,*.gif ,*.png ,*.bmp ,*.tiff ,*.txt ,*.html ,*.rtf ,*.cbz ,*.cbr)')
            archivos_seleccionados = list(fname)[0]
            archivos_a_asociar=[]
            
            if self.unidad_kobo[0:2] != archivos_seleccionados[0][0:2]:

                self.mensaje_aviso("El archivo seleccionado no está en el dispositivo.\nPor favor, copie el fichero en el dispositivo para poder asociarlo a una colección.", "Warning")
            
            else:

                for archivo in archivos_seleccionados:

                    if self.unidad_kobo[0:2] != archivo[0:2]:

                        self.mensaje_aviso("El archivo seleccionado no está en el dispositivo.\nPor favor, copie el fichero en el dispositivo para poder asociarlo a una colección.", "Warning")
                        break

                    else:          

                        archivos_a_asociar.append(archivo.replace(archivo[0:2],'file:///mnt/onboard'))
                        self.conexion.associate_book_to_collection(archivos_a_asociar,self.coleccionSeleccionada)
                    
                self.listar_archivos_coleccion()
                self.mensaje_aviso("Libros añadidos a la colección.", "Information")

    def listar_archivos_coleccion(self):

        self.coleccionSeleccionada = self.ui.tblColecciones.selectedIndexes()[0].data()
        self.ui.txtColeccion.setText(self.coleccionSeleccionada)      
        libros = self.conexion.consult_books_and_collections(self.coleccionSeleccionada)
        tabla = self.ui.tblLibros
        tabla.setRowCount(0)
        tabla.clearContents()

        for row_number, row_data in enumerate(libros):

            tabla.insertRow(row_number)

            for column_number, data in enumerate(row_data):               
                
                item = QTableWidgetItem(str(data[data.rfind("/")+1:]))
                item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(Qt.CheckState.Unchecked)
                tabla.setItem(row_number, column_number, item)

        self.ui.lblLibros.setText(str(len(libros)))
 
    def obtener_elementos_seleccionados(self, tabla):

        lista_libros = []

        for row in range(tabla.rowCount()):

            if tabla.item(row,0).checkState() == Qt.CheckState.Checked:

                lista_libros.append(tabla.item(row,0).text())

        return lista_libros

    def crear_Coleccion(self):
        
        resultado = self.conexion.create_collection(self.ui.txtColeccion.text())

        if resultado:

            self.mensaje_aviso("Colección creada correctamente.", "Information")

        else:

            self.mensaje_aviso("El nombre de esta colección ya existe.\nEscoja otro nombre.", "Warning")        


        self.mostrar_colecciones()
        self.limpia_tabla(self.ui.tblLibros)

    def pregunta_eliminacion(self):

        buttonReply = QMessageBox.question(self, 'Mensaje de confirmación', "¿Estás seguro de que quieres eliminar la colección seleccionada?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if buttonReply == QMessageBox.Yes:

            self.elimina_coleccion()

    def elimina_coleccion(self):
        
        print(self.ui.tblLibros.selectedIndexes())
        self.conexion.delete_collection(self.coleccionSeleccionada)
        self.limpia_tabla(self.ui.tblLibros)
        self.mostrar_colecciones()
        self.ui.txtColeccion.setText("")
        self.mensaje_aviso("Colección eliminada correctamente.", "Information")
  
    def elimina_libro_coleccion(self):  

        libros = self.obtener_elementos_seleccionados(self.ui.tblLibros) 
        self.conexion.delete_book_from_collection(self.coleccionSeleccionada, libros)
        self.listar_archivos_coleccion()
  
    def limpia_tabla(self, nombre_tabla):
        
        nombre_tabla.setRowCount(0)
        nombre_tabla.clearContents()

    def modifica_nombre_coleccion(self):
        
        resultado = self.conexion.modify_collection_name(self.coleccionSeleccionada, self.ui.txtColeccion.text())
        
        if resultado:

            self.mensaje_aviso("Modificación realizada correctamente.", "Information")

        else:

            self.mensaje_aviso("El nombre de esta colección ya existe.\nEscoja otro nombre.", "Warning")

        self.mostrar_colecciones()

    def mensaje_aviso(self, mensaje, tipo):

        msg = QMessageBox()

        if tipo == "Information":

            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Información")

        elif tipo == "Warning":

            msg.setWindowTitle("Atención")
            msg.setIcon(QMessageBox.Warning)
        
        msg.setText(mensaje)
        msg.exec()


if __name__ == "__main__":

    cgitb.enable(format = 'text') #Permite que la interfaz gráfica no se cierre cuando salte una excepción.
    app = QApplication(sys.argv)
    w = AppWindow()
    
    w.show()
    sys.exit(app.exec_())
