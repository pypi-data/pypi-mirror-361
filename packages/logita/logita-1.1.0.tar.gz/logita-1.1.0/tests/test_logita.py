import os
import tempfile
from logita import Logita  # Asegúrate que Logita esté en logita.py y accesible

def test_logita_console_and_file():
    # Crear archivo temporal para log
    temp_log_file = tempfile.NamedTemporaryFile(delete=False)
    temp_log_file.close()

    try:
        # Instancia con colores activados y logging a archivo
        logger = Logita(log_to_file=True, log_filename=temp_log_file.name, print_to_console=True, use_colors=True)

        print("\n--- Probando niveles de log con colores activados ---")
        logger.info("Mensaje INFO")
        logger.success("Mensaje SUCCESS")
        logger.warning("Mensaje WARNING")
        logger.error("Mensaje ERROR")
        logger.debug("Mensaje DEBUG")
        logger.critical("Mensaje CRITICAL")

        try:
            1 / 0
        except Exception as e:
            logger.exception(f"Exception atrapada: {e}")

        # Instancia con colores desactivados y solo consola
        logger_no_color = Logita(log_to_file=False, print_to_console=True, use_colors=False)

        print("\n--- Probando niveles de log sin colores ---")
        logger_no_color.info("Mensaje INFO sin color")
        logger_no_color.success("Mensaje SUCCESS sin color")
        logger_no_color.warning("Mensaje WARNING sin color")
        logger_no_color.error("Mensaje ERROR sin color")
        logger_no_color.debug("Mensaje DEBUG sin color")
        logger_no_color.critical("Mensaje CRITICAL sin color")

        # Leer y verificar el contenido del archivo de log
        with open(temp_log_file.name, "r") as f:
            logs = f.read()
            assert "Mensaje INFO" in logs
            assert "Mensaje SUCCESS" in logs
            assert "Exception atrapada" in logs
            print("\nArchivo de log contiene entradas esperadas.")

    finally:
        pass  # No borrar aquí para evitar conflicto con archivo abierto

    # Borrar el archivo temporal ya cerrado
    #os.unlink(temp_log_file.name)


if __name__ == "__main__":
    test_logita_console_and_file()
    print("\nTest completado con éxito.")
