import psycopg2
import reflex as rx

class State(rx.State):
    

    # Los elementos 
    elementos = []

    @staticmethod
    def get_db_connection():
        """Establece la conexión con la base de datos PostgreSQL."""
        try:
            connection = psycopg2.connect(
                dbname="base de datos",   # Nombre de la base de datos
                user="postgres",    # Usuario 
                password="sebasbastidas22",  # Contraseña 
                host="localhost",     # Dirección del servidor
                port="5432"           # Puerto 
            )
            return connection
        except Exception as e:
            print(f"Error al conectar con la base de datos: {e}")
            return None

    def load_tareas_from_db(self):
        """Carga todas las tareas """
        connection = self.get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT nombre FROM tareas;")
                    self.elementos = [row[0] for row in cursor.fetchall()]
            except Exception as e:
                print(f"Error al cargar tareas: {e}")
            finally:
                connection.close()

    def add_item(self, form_data: dict):
        """Agrega un nuevo ítem a la lista de tareas y la base de datos."""
        new_item = form_data.get("new_item")
        if new_item:
            # Insertar en la base de datos
            connection = self.get_db_connection()
            if connection:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO tareas (nombre) VALUES (%s) RETURNING id;", (new_item,))
                        connection.commit()
                except Exception as e:
                    print(f"Error al agregar tarea a la base de datos: {e}")
                finally:
                    connection.close()

            # Agregar a la lista de tareas en el estado
            self.elementos.append(new_item)

    def finish_item(self, item: str):
        """Finaliza un ítem en la lista de tareas y lo elimina de la base de datos."""
        # Eliminar de la base de datos
        connection = self.get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM tareas WHERE nombre = %s RETURNING id;", (item,))
                    connection.commit()
            except Exception as e:
                print(f"Error al eliminar tarea de la base de datos: {e}")
            finally:
                connection.close()

        # Eliminar del estado
        self.elementos.remove(item)
        print(f"Se eliminó el ítem: {item}")  # Imprime el ítem eliminado en la consola.

    @staticmethod
    def get():
        """Devuelve el estado de los elementos de la lista de tareas."""
        return State.elementos

def todo_item(item: rx.Var[str]) -> rx.Component:
    """Renderiza un ítem en la lista de tareas."""
    return rx.list_item(
        # Un botón para finalizar el ítem
        rx.hstack(
            rx.icon_button(
                rx.icon(tag="check"),
                on_click=lambda: State.finish_item(item),
                margin_y="0.5em",
                variant="outline",
            ),
            # El texto del ítem
            rx.text(item, as_="span"),
            align="center",
        ),
        class_name="list-none",
    )

def todo_list() -> rx.Component:
    """Renderiza la lista de tareas."""
    return rx.ordered_list(
        rx.foreach(State.get(), lambda item: todo_item(item)),
    )

def new_item() -> rx.Component:
    """Renderiza el formulario  agregar un nuevo ítem."""
    return rx.form(
        rx.hstack(
            rx.input(
                name="new_item",
                placeholder="Añadir nueva tarea",
                bg=rx.color("blue", 9),
                width="300%",
            ),
            rx.button("Añadir"),
        ),
        on_submit=State.add_item,
        reset_on_submit=True,
        width="100%",
    )

def index() -> rx.Component:
    """Página principal del proyecto."""
    return rx.center( 
        rx.text("TO DO", margin="10px", 
                position="absolute", top=0, left=0,
                background_image="linear-gradient(271.68deg, #EE756A 0.75%, #756AEE 88.52%)", 
                text_shadow="5px 5px 10px rgba(0, 0, 0, 0.5)",
                background_clip="text", font_weight="bold",
                font_size="5em",),
        rx.vstack(
            rx.heading("Lista de Tareas"),
            new_item(),
            rx.divider(),
            todo_list(),
            bg=rx.color("red", 1),
            margin_top="5em",
            padding="1em",
            border_radius="0.5em",
            spacing="3",
            width="500px",
            height="auto",
        ),
        background_image="url('https://cdn-ft-site.nyc3.cdn.digitaloceanspaces.com/blog/en/short-to-do-lists.jpg')",
        height="100vh", position="relative",
    )

# Crear la aplicación y agregar el estado
app = rx.App()

# Agregar la página principal y establecer el título
app.add_page(index, title="Lista de Tareas")

# Iniciar la aplicación
if __name__ == "__main__":
    app.run()
