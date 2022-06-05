import sqlite3


class BBDD():
    """
    Una clase para realizar las conexiones con la BBDD del Kobo.

    """
    def __init__(self, unidad="D:/") -> None:
        """
        Constructor.

        Si no se le pasa ninguna unidad por parámetro se le asigna la unidad D
        para hacer pruebas sin necesidad de tener el Kobo conectado.

        Con la variable self.ruta definiremos la unidad y la ruta donde está guardada
        la BBDD en el Kobo.

        Parameters
        ----------
        unidad : str, optional
            se trata de la unidad donde está conectado el Kobo (default is D:/)

        Returns
        -------
        None
        """
        self.unidad = unidad
        self.BBDD = ".kobo/KoboReader.sqlite"
        self.ruta = self.unidad + self.BBDD

    def DB_connection(self, unidad="D:/"):
        """
        Método para realizar la conexión con la BBDD.

        Parameters
        ----------
        unidad : str, optional
            se trata de la unidad donde está conectado el Kobo (default is D:/)

        Returns
        -------
        La conexión con la BBDD del dispositivo.
        """
        self.conexion=sqlite3.connect(self.ruta)
        #Para pruebas sin el KOBO conectado:
        #self.conexion = sqlite3.connect("D:/Manga/KoboReader.sqlite")
        return self.conexion

    def consult_collections(self):
        """
        Método para realizar consulta a la BBDD de todas las colecciones.

        Parameters
        ----------
        None

        Returns
        -------
        El resultado de la consulta realizada a la BBDD.
        """
        SQL_consulta = "SELECT name FROM Shelf"
        resultado = self.execute_SQL_consult(SQL_consulta)        
        return resultado

    def consult_books_and_collections(self, coleccion):
        """
        Método para realizar consulta a la BBDD de todos los libros asociados a la
        colección seleccionada.

        Parameters
        ----------
        coleccion : str
            El nombre de la colección de la cual queremos saber los libros asociados a ella.
        Returns
        -------
        El resultado de la consulta realizada a la BBDD.
        """
        SQL_consulta = "SELECT ContentId FROM ShelfContent where shelfname = ?"
        resultado = self.execute_SQL_consult(SQL_consulta, coleccion )
        return resultado

    def is_collection_created(self, coleccion):
        """
        Método comprobar si la colección está creada en la BBDD.
        
        Parameters
        ----------
        coleccion : str
            El nombre de la colección de la cual queremos saber si ya está creada.
        Returns
        -------
        True    si la colección está dada de alta.
        False   si la colección no está dada de alta.
        """
        isColeccionCreada = False
        SQL_consulta = "SELECT count(name) FROM Shelf where name = ?"
        resultado = self.execute_SQL_consult(SQL_consulta, coleccion )        
        
        if resultado[0][0] == 0:

            isColeccionCreada = False

        if resultado[0][0] == 1:

            isColeccionCreada = True

        return isColeccionCreada

    def is_book_associated_to_collection(self, coleccion, libro):
        """
        Método comprobar si un libro está ya asociado a la colección.
        
        Parameters
        ----------
        coleccion : str
            El nombre de la colección.

        libro : str
            El nombre del libro con su extensión. La cadena de texto debe comenzar por
            file:///mnt/onboard

        Returns
        -------
        True    si el libro está asociado a la colección.
        False   si el libro no está asociado a la colección.
        """
        isLibroAsociado = False
        SQL_consulta = "SELECT count(shelfname) from ShelfContent where shelfname = ? and ContentId = ?"
        self.cursor = self.DB_connection(self.unidad).cursor()
        self.cursor.execute(SQL_consulta,(coleccion,libro))
        resultado = self.cursor.fetchall()
        self.cursor.close()
        self.conexion.close()
        
        if resultado[0][0] == 0:

            isLibroAsociado = False
 
        if resultado[0][0] == 1:

            isLibroAsociado = True

        return isLibroAsociado

    def create_collection(self, nombreColeccion):
        """
        Método para crear una colección.
        
        Parameters
        ----------
        nombreColeccion : str
            El nombre de la colección.

        Returns
        -------
        True    si la colección NO se ha creado.
        False   si la colección se ha creado.
        """
        resultado = False
        coleccion = ("", nombreColeccion, nombreColeccion, "",
                     nombreColeccion, "", "false", "true", "false", "", "")
        SQL_insertar = "INSERT INTO Shelf VALUES(?,?,?,?,?,?,?,?,?,?,?)"
  
        if self.is_collection_created(nombreColeccion):

            resultado = False

        else:

            self.execute_SQL_action(SQL_insertar,coleccion,0)
            
            resultado = True

        return resultado

    def associate_book_to_collection(self, listaArchivos, nombreColeccion=""):
        """
        Método para asociar un libro a una colección.
        
        Parameters
        ----------
        listaArchivos : list
            lista de archivos a asociar, debe tener la ruta completa del archivo.
        
        nombreColeccion : str
            El nombre de la colección.        
        Returns
        -------
        True    si la colección NO se ha creado.
        False   si la colección se ha creado.
        """
        SQL_insertar = "INSERT INTO ShelfContent VALUES(?,?,?,?,?)"

        for archivo in listaArchivos:

            if self.is_book_associated_to_collection(nombreColeccion, archivo) == False:

                parametros = (nombreColeccion, archivo, "", "false", "false")
                self.execute_SQL_action(SQL_insertar,parametros,0)    

    def delete_collection(self, coleccion):        
        """
        Método para eliminar una colección.
        Elimina de la tabla Shelf la colección
        Elimina de la tabla ShelfContent los libros asociados a dicha colección.
        
        Parameters
        ----------
        coleccion : str
            El nombre de la colección a eliminar.

        Returns
        -------
        None
        """
        SQL_Eliminar_Coleccion = "DELETE FROM Shelf WHERE Name=?"
        SQL_Eliminar_ColeccionYLibros = "DELETE FROM ShelfContent WHERE shelfname=?"
        self.execute_SQL_action(SQL_Eliminar_Coleccion,(coleccion,),0)
        self.execute_SQL_action(SQL_Eliminar_ColeccionYLibros,(coleccion,),0)

    def delete_book_from_collection(self, nombreColeccion, libros):

        SQL_Eliminar = "DELETE FROM ShelfContent WHERE ShelfName=? and ContentId=?"

        for libro in libros:

            nombreLibro = self.consult_book_path(libro)[0][0]
            self.execute_SQL_action(SQL_Eliminar, (nombreColeccion, nombreLibro),0)
        

    def modify_collection_name(self, nombreAntiguo, nombreNuevo):
        """
        Método para modificar el nombre de una colección.
        Comprueba si el nombre nuevo existe como colección.
        Modifica el nombre de la colección en la tabla Shelf.
        Modifica el nombre de la colección en la tabla ShelfContent.

        Parameters
        ----------
        nombreAntiguo : str
            El nombre antiguo de la colección.  

        nombreNuevo : str
            El nombre nuevo de la colección.        
        Returns
        -------
        True    si la colección NO se ha modificado.
        False   si la colección se ha modificado.
        """
        resultado = False

        if self.is_collection_created(nombreNuevo):

            resultado = False

        else:

            SQL_actualizar_shelf = "UPDATE Shelf SET InternalName = ?, Name = ? WHERE Name = ?"
            SQL_actualizar_content = "UPDATE ShelfContent SET ShelfName = ? WHERE ShelfName = ?"
            self.execute_SQL_action(SQL_actualizar_shelf,(nombreNuevo, nombreNuevo, nombreAntiguo),0)
            self.execute_SQL_action(SQL_actualizar_content,(nombreNuevo, nombreAntiguo),0)
            resultado = True

        return resultado

    def execute_SQL_consult(self, SQL_consulta, parametros=""):
        """
        Método para ejecutar sentencias SQL de consulta.

        Parameters
        ----------
        SQL_consulta : str
            Consulta a ejecutar.  

        parametros : str
            Parámetros de la consulta.        
        Returns
        -------
        El resultado de la consulta.
        """        
        self.cursor = self.DB_connection(self.unidad).cursor()
        self.SQL_consulta = SQL_consulta
        
        if parametros=="":

            self.cursor.execute(self.SQL_consulta)

        else:

            self.cursor.execute(self.SQL_consulta,(parametros,))
            
        resultado = self.cursor.fetchall()
        self.cursor.close()
        self.conexion.close()

        return resultado

    def execute_SQL_action(self, SQL_accion, parametros="", tipo_ejecucion=0):
        """
        Método para ejecutar sentencias SQL de acción.

        Parameters
        ----------
        SQL_accion : str
            Consulta a ejecutar.  

        parametros : str
            Parámetros de la consulta.        

        tipo_ejecucion : int, optional
            Implementación en desuso.

        Returns
        -------
        None
        """  
        self.cursor = self.DB_connection(self.unidad).cursor()

        if tipo_ejecucion == 0:
            
            self.cursor.execute(SQL_accion, (parametros))


        elif tipo_ejecucion == 1:

            self.cursor.executemany(SQL_accion, (parametros))

        elif tipo_ejecucion == 2:

            self.cursor.executescript(SQL_accion, (parametros))


        self.conexion.commit()
        self.cursor.close()
        self.conexion.close()

    def consult_book_path(self, libro):

        libro = "%"+libro
        SQL_consulta = "select ContentId from ShelfContent where ContentId like ?"
        resultado = self.execute_SQL_consult(SQL_consulta, libro )
        return resultado