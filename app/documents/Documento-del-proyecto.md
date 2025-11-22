 ## Indicadores del proyecto

(_debe dejar enlaces a evidencias que permitan de una forma sencilla analizar estos indicadores, con gráficas y/o con enlaces_)

Miembro del equipo  | Horas | Commits | LoC | Test | Issues | Work Item| Dificultad
------------- | ------------- | ------------- | ------------- | ------------- | ------------- |  ------------- |  ------------- | 
[Valenzuela Muñoz,Alberto](https://github.com/AlbertoValenzuelaMunoz1) | HH | Commit | 711 | ZZ | II | Implementación de workflows de Sonar Qube, implementación del work item de comentarios de dataset, implementación junto a mis compañeros del work item de fakenodo.| H/M/L |
[Rivas Becerra, Mario](https://github.com/marrivbec) | HH | XX | YY | ZZ | II | Implementación de la vista "Trending Datasets" | H/M/L |
[Roldán Pérez, Antonio](https://github.com/AntonioRolpe11) | HH | XX | YY | ZZ | II | Descripción breve | H/M/L |
[Ramírez Morales, Juan](https://github.com/Juanramire) | HH | XX | YY | ZZ | II | Descripción breve | H/M/L |
[Ferrer Álvarez, Ángel Manuel](https://github.com/angelmanuelferrer) | HH | XX | YY | ZZ | II | Descripción breve | H/M/L |¡
[Ruiz Fernández, Javier](https://github.com/javruifer1) | HH | XX | YY | ZZ | II | Descripción breve | H/M/L |
**TOTAL** | tHH  | tXX | tYY | tZZ | tII | Descripción breve | H (X)/M(Y)/L(Z) |

La tabla contiene la información de cada miembro del proyecto y el total de la siguiente forma: 
  * Horas: número de horas empleadas en el proyecto.
  * Commits: commits hechos por miembros del equipo.
  * LoC (líneas de código): líneas producidas por el equipo y no las que ya existían o las que se producen al incluir código de terceros.
  * Test: test realizados por el equipo.
  * Issues: issues gestionadas dentro del proyecto y que hayan sido gestionadas por el equipo.
  * Work Item: principal WI del que se ha hecho cargo el miembro del proyecto.
  * Dificultad: señalar el grado de dificultad en cada caso. Además, en los totales, poner cuántos se han hecho de cada grado de dificultad entre paréntesis. 


## Resumen ejecutivo
El proyecto desarrollado, denominado Tennis-Hub, no nace desde cero, sino que constituye una refactorización del sistema de código abierto conocido como UVLHUB. El objetivo principal de esta transformación ha sido migrar de un repositorio de datos genérico a una plataforma verticalizada y altamente especializada en la gestión, almacenamiento y distribución de datasets relacionados exclusivamente con el mundo del tenis. Esta reingeniería ha implicado no solo cambios estéticos, sino una reestructuración de la lógica de negocio para soportar nuevas funcionalidades críticas que enriquecen la interacción del usuario y robustecen la seguridad del entorno.

1. Evolución de la Identidad y Experiencia de Usuario (UX)
El primer nivel de intervención se centró en la "Personalización y Refactorización Visual". El sistema original carecía de una identidad temática definida. Para Tennis-Hub, se ha implementado una nueva guía de estilo que alinea la paleta de colores, la tipografía y la disposición de los elementos (layout) con la estética deportiva del tenis.

Sin embargo, la personalización trasciende lo meramente cosmético. Se ha realizado una labor de localización y adaptación semántica; todos los textos, mensajes de error y etiquetas de la interfaz han sido reescritos para utilizar la terminología propia del dominio deportivo y del análisis de datos. Esto reduce la fricción cognitiva del usuario, quien ahora navega por un entorno que le resulta familiar y coherente, mejorando significativamente la usabilidad general de la aplicación.

2. Módulo de Transacciones y Gestión de Recursos (El Carrito)
Una de las innovaciones funcionales más destacadas respecto al proyecto base es la implementación del Sistema de Carrito de Datasets. Inspirado en los patrones de diseño del comercio electrónico (e-commerce), esta funcionalidad cambia el paradigma de descarga. En lugar de obligar al usuario a realizar descargas unitarias y repetitivas, el sistema permite ahora la selección múltiple de recursos.

Técnicamente, esto se gestiona mediante el almacenamiento en sesión (session storage) de las referencias a los datasets seleccionados. El usuario puede navegar por distintas categorías, añadir archivos a su "bolsa" virtual y, finalmente, proceder a una gestión unificada. Esto culmina en el módulo de Gestión de Descargas, que ha sido optimizado para manejar la entrega eficiente de estos archivos, permitiendo al investigador o aficionado obtener todo el material necesario en un solo flujo de trabajo, optimizando el tiempo y el ancho de banda.

3. Dinamización Social y Métricas de Popularidad
Para transformar un repositorio estático en una comunidad dinámica, se han integrado Módulos de Interacción. La característica central aquí es el sistema de comentarios. Se ha desarrollado un sistema CRUD (Create, Read, Update, Delete) que permite a los usuarios registrados iniciar hilos de discusión en cada dataset. Esto añade una capa de valor cualitativo a los datos: los usuarios pueden advertir sobre erratas en los archivos, sugerir mejoras o compartir análisis derivados, fomentando la inteligencia colectiva.

Paralelamente, se ha introducido un motor de análisis de tendencias. El sistema ya no muestra los datos de forma plana; ahora incorpora contadores internos que registran eventos de visualización y descarga en tiempo real. Estos datos alimentan la sección de "Datasets de Moda" (Trending), un algoritmo de ordenamiento que destaca en la página principal aquellos recursos que están recibiendo mayor atención por parte de la comunidad. Esto no solo mejora la descubribilidad del contenido, sino que ofrece a los administradores una visión clara de qué tipo de información es la más demandada.

4. Seguridad Avanzada: Doble Factor de Autenticación (2FA)
Dada la importancia de proteger las cuentas de usuario y la integridad de los datos subidos, se ha elevado el estándar de seguridad mediante la integración de Doble Factor de Autenticación (2FA). Esta funcionalidad supone una barrera adicional crítica frente al compromiso de credenciales.

El flujo implementado requiere que, tras la validación tradicional de usuario y contraseña, el sistema genere un token de un solo uso (OTP) mediante algoritmos criptográficos seguros. Este código es enviado automáticamente al correo electrónico del usuario a través de una integración con servicios SMTP. El acceso al sistema permanece bloqueado en una vista intermedia hasta que el usuario introduce el código correcto. Esta implementación asegura que, incluso si una contraseña es filtrada, el atacante no podrá acceder a la cuenta sin tener control simultáneo sobre el correo electrónico del propietario.

5. Infraestructura y Despliegue en la Nube
Finalmente, la arquitectura de despliegue ha sido modernizada utilizando Render, una plataforma en la nube (PaaS) que garantiza alta disponibilidad y escalabilidad. Para profesionalizar el ciclo de vida del desarrollo de software (SDLC), se han establecido dos entornos completamente diferenciados:

*Entorno de Desarrollo: Un espacio volátil donde se despliegan las nuevas funcionalidades (features) para su integración y revisión inicial.

*Entorno de Pruebas (Staging): Un espejo del entorno de producción donde se realizan las validaciones finales y pruebas de carga.

Esta separación de entornos, cada uno con su propia instancia de base de datos, permite al equipo validar cambios, probar migraciones y ejecutar tests de regresión sin poner en riesgo la estabilidad del sistema ni la integridad de los datos visibles para los usuarios finales.

## Descripción del sistema
Desde un punto de vista estratégico, el sistema busca democratizar el acceso a datos deportivos, permitiendo a analistas, entrenadores y aficionados compartir conjuntos de datos estructurados. La solución no solo almacena información, sino que fomenta la interacción mediante sistemas de comentarios y valoración, asegurando al mismo tiempo la integridad de las cuentas mediante protocolos de seguridad avanzados como la autenticación de doble factor (2FA).

La arquitectura de Tennis-Hub sigue el patrón de diseño Modelo-Vista-Controlador (MVC), implementado a través del framework Flask. Esta decisión arquitectónica permite desacoplar la lógica de negocio de la interfaz de usuario, facilitando la mantenibilidad y escalabilidad del sistema.

* Capa de Presentación (Vista/Templates): Desarrollada en HTML5 y CSS3, utiliza el motor de plantillas Jinja2 integrado en Flask. Esta capa es responsable de renderizar la información enviada por el servidor y capturar las interacciones del usuario. Se ha diseñado con un enfoque responsive para adaptarse a distintos dispositivos.

apa de Lógica de Negocio (Controlador/Rutas): Gestionada por los controladores de Flask (routes.py o views.py). Aquí residen los algoritmos que procesan las peticiones HTTP (GET, POST), gestionan la lógica del carrito de compras, validan el 2FA y calculan las tendencias de los datasets.

* Capa de Datos (Modelo): Se utiliza SQLAlchemy como ORM (Object-Relational Mapper). Esto permite interactuar con la base de datos mediante clases de Python en lugar de escribir SQL crudo, abstrayendo la complejidad de las consultas. Los modelos principales incluyen entidades como User, Dataset, Comment y Order."

El sistema interactúa con subsistemas críticos:

* Sistema de Correo: Para el envío de códigos 2FA (posiblemente vía SMTP o librerías como Flask-Mail).
* Sistema de Almacenamiento: Gestión de archivos estáticos donde se alojan los datasets físicos.
* Render (PaaS): Plataforma que orquesta el despliegue, gestionando el servidor de aplicaciones (Gunicorn/uWSGI) y la conexión a la base de datos en la nube.

Desde la perspectiva funcional, el sistema se divide en módulos interconectados:

* Módulo de Gestión de Usuarios y Seguridad (Auth) "Este módulo administra el ciclo de vida de las cuentas. La mejora más significativa es la implementación del Doble Factor de Autenticación (2FA). Tras el inicio de sesión estándar (usuario/contraseña), el sistema genera un token temporal enviado al correo del usuario, bloqueando el acceso hasta su validación. Esto mitiga riesgos de suplantación de identidad."

* Módulo de Datasets y Tendencias Es el núcleo de Tennis-Hub. Los usuarios pueden subir archivos que son indexados por el sistema. Se ha incorporado un algoritmo de popularidad que alimenta la sección 'Datasets de Moda'. Este subsistema utiliza contadores internos que registran visualizaciones y descargas, ordenando dinámicamente los recursos en la página principal para destacar el contenido más relevante.

* Módulo de Interacción Social Para fomentar la comunidad, se ha desarrollado un sistema de comentarios. Cada dataset cuenta con un hilo de discusión persistente donde los usuarios pueden aportar feedback, correcciones o análisis sobre los datos, convirtiendo el repositorio estático en un espacio dinámico de conocimiento.

* Módulo Transaccional (El Carrito) Inspirado en e-commerce, se introduce el concepto de 'Carrito de Datasets'. Funcionalmente, permite a los usuarios seleccionar múltiples archivos de interés mientras navegan, agregándolos a una lista temporal. Posteriormente, el usuario puede proceder a la 'descarga unificada' o gestión en bloque de estos recursos, mejorando la usabilidad frente a la descarga uno a uno.

El proyecto parte de la base de UVLHUB, pero ha sufrido una transformación sustancial. A continuación, se enumeran explícitamente los cambios desarrollados e integrados en la versión final de Tennis-Hub:

* Refactorización de Marca e Interfaz:
  * Modificación completa de la paleta de colores, logotipos y tipografías para alinearse con la temática de tenis.
  * Adaptación de los textos y terminología de la interfaz (traducción y localización al dominio deportivo).

* Implementación de Seguridad Avanzada (2FA):
  * Desarrollo de lógica backend para la generación de tokens OTP (One-Time Passwords).
  * Creación de nuevas vistas y formularios para la introducción del código de verificación.
  * Integración con servidor de correo para el envío de alertas.

* Sistema de Carrito de Compras (Dataset Cart):
  * Creación de estructuras de datos de sesión para almacenar selecciones temporales.
  * Desarrollo de la interfaz flotante o página dedicada para visualizar los items seleccionados.
  * Implementación de la lógica de descarga masiva o checkout.

* Métricas y 'Trending Topic':
  * Modificación del modelo de base de datos Dataset para incluir campos de contadores (view_count, download_count).
  * Creación de la lógica de ordenamiento para filtrar y mostrar los 'Datasets de Moda' en la landing page.

* Feedback de Usuario:
  * Desarrollo del sistema CRUD (Create, Read, Update, Delete) para comentarios asociados a cada dataset.
  * Validación de permisos para asegurar que solo usuarios registrados puedan comentar.

## Visión global del proceso de desarrollo (1.500 palabras aproximadamente)
Debe dar una visión general del proceso que ha seguido enlazándolo con las herramientas que ha utilizado. Ponga un ejemplo de un cambio que se proponga al sistema y cómo abordaría todo el ciclo hasta tener ese cambio en producción. Los detalles de cómo hacer el cambio vendrán en el apartado correspondiente. 

### Entorno de desarrollo
El diseño e implementación del sistema "Tennis-Hub" se ha sustentado sobre un entorno de desarrollo robusto, moderno y estandarizado. La elección de las herramientas no ha sido arbitraria, sino que responde a la necesidad de crear un flujo de trabajo eficiente, colaborativo y, sobre todo, reproducible en diferentes máquinas y sistemas operativos. A continuación, se detalla la arquitectura de desarrollo, las tecnologías empleadas y el procedimiento estricto para el despliegue del sistema.

1. Entorno de Desarrollo Integrado (IDE)
Como núcleo central del trabajo diario se ha seleccionado Visual Studio Code (VS Code). El equipo ha aprovechado las características nativas de VS Code, específicamente su motor de IntelliSense, que proporciona autocompletado inteligente y documentación de funciones en tiempo real, acelerando drásticamente la escritura de código en Python y HTML.

Además, la integración de la terminal en la propia interfaz del editor ha permitido ejecutar comandos de servidor, gestión de bases de datos y control de versiones sin necesidad de cambiar de ventana, centralizando todas las tareas en un único espacio de trabajo. El uso de herramientas de depuración (debugging) integradas fue crucial para inspeccionar variables en tiempo de ejecución y solucionar errores lógicos complejos de manera eficiente.

2. Stack Tecnológico: Backend y Frontend
La lógica del servidor se ha construido íntegramente sobre Python. Se optó por este lenguaje debido a su sintaxis limpia, su legibilidad y su extenso ecosistema de librerías orientadas al manejo de datos, lo cual es fundamental para un proyecto centrado en datasets de tenis.

Dentro del ecosistema Python, se ha implementado Flask como framework web principal. Otorga al equipo un control granular sobre los componentes del sistema, permitiendo instalar solo aquello que es estrictamente necesario. Esto ha resultado en una aplicación más ligera y optimizada.

Para la capa de presentación (Frontend), se ha mantenido una estructura clásica pero efectiva basada en HTML para la maquetación semántica y CSS para los estilos visuales, asegurando una interfaz intuitiva y adaptada a la nueva identidad de marca del proyecto. La comunicación entre el backend (Python) y el frontend (HTML) se realiza mediante el motor de plantillas Jinja2 (integrado en Flask), que permite inyectar datos dinámicos del servidor directamente en las vistas del usuario.

3. Gestión de Dependencias y Librerías
Uno de los mayores desafíos en el desarrollo colaborativo es asegurar que todos los miembros del equipo utilicen exactamente las mismas versiones de las librerías para evitar conflictos de compatibilidad. Para mitigar este riesgo, la gestión de dependencias externas se ha centralizado estrictamente en el archivo requirements.txt.

Este incluye todas las librerías de terceros necesarias para la ejecución del proyecto. Entre ellas destacan herramientas críticas como Locust, utilizada para realizar pruebas de carga y estrés, simulando el comportamiento de múltiples usuarios concurrentes para validar la robustez del servidor antes de su puesta en producción.

4. Infraestructura de Virtualización y Contenedores
Se ha optado por una estrategia de infraestructura mediante Flask, Docker y Vagrant.

* Docker: El sistema, junto con todas sus dependencias, librerías y configuraciones, se empaqueta en un contenedor aislado. Esto asegura la portabilidad total: si el contenedor funciona en la máquina de un desarrollador, funcionará idénticamente en el servidor de producción.

* Vagrant: Se ha utilizado para orquestar máquinas virtuales completas, proporcionando un entorno de desarrollo replicable que simula las condiciones del servidor final.

* Flask: Se ha utilizado para correr el sistema de manera local desde cualquier máquina.

5. Control de Versiones y Colaboración
La integridad del código fuente y la colaboración entre los miembros del equipo se ha administrado mediante Git. Se estableció un flujo de trabajo basado en ramas (branches), permitiendo desarrollar nuevas funcionalidades de manera aislada sin comprometer la estabilidad de la rama principal (main). Las operaciones habituales de sincronización —git pull para obtener cambios, git commit para guardar progresos y git push para subir modificaciones al repositorio remoto.

6. Guía Técnica de Despliegue e Instalación
Para desplegar el sistema desde cero en un nuevo entorno, es imperativo seguir un protocolo secuencial que asegure la correcta configuración de todos los componentes.

* Preparación del Entorno: El primer paso requiere importar el código fuente del proyecto. Inmediatamente después, es obligatorio generar un entorno virtual de Python (venv) en la raíz del directorio. El uso de entornos virtuales es una práctica fundamental en Python, ya que aísla las dependencias del proyecto de las librerías instaladas globalmente en el sistema operativo, evitando conflictos de versiones entre diferentes proyectos.

* Instalación de Dependencias: Con el entorno virtual activado, se procede a la instalación de las librerías mediante el comando pip install -r requirements.txt. Este proceso descarga e instala automáticamente Flask, Locust, los conectores de base de datos y cualquier otra utilidad definida por el equipo.

* Configuración de Base de Datos: El sistema requiere la configuración de dos instancias de base de datos separadas: una para el entorno de Desarrollo (donde se persiste la información mientras se programa) y otra para el entorno de Pruebas (que se limpia y regenera cada vez que se ejecutan los tests automatizados). Esta separación es vital para evitar la corrupción de datos útiles durante las fases de testeo.

* Seguridad y Variables de Entorno: Finalmente, se utiliza un archivo de configuración .env. Es responsabilidad del desarrollador asegurar que las credenciales (usuario, contraseña, host y puerto) definidas en este archivo coincidan estrictamente con la configuración real de las bases de datos creadas. Solo cuando estas variables están sincronizadas, el sistema puede arrancar correctamente.

## Ejercicio de propuesta de cambio

### 1 Creación de la tarea en el tablero del proyecto
El primer paso consiste en registrar la tarea en el tablero de gestión del proyecto. Para ello, se crea una issue que describa de manera clara y concisa el objetivo del cambio: ya sea implementar una nueva funcionalidad, corregir un error existente o realizar una mejora en el sistema. Una vez generada, la tarea se ubica inicialmente en la columna TO DO, donde se encuentran todos los elementos pendientes de abordar. Esta fase permite que el equipo mantenga una visión global del trabajo por realizar y que las tareas queden correctamente priorizadas antes de comenzar su desarrollo.

### 2 Creación de la rama correspondiente
Antes de empezar a implementar cualquier cambio en el código, es necesario crear una nueva rama en el repositorio. Esta rama siempre debe originarse desde la rama trunk. El nombre de la rama dependerá del tipo de modificación que se vaya a realizar: “feature-task/nombre-de-la-tarea” para funcionalidades nuevas o ampliaciones, y “bugfix/descripción-del-cambio” para resolver errores. Para crear la rama se ejecutan los siguientes comandos: git checkout trunk y git checkout -b nombre-de-la-rama. Una vez creada la rama, se actualiza el tablero moviendo la issue al estado IN PROGRESS, indicando así al resto del equipo que se ha comenzado a trabajar en dicha tarea.

### 3 Desarrollo de la tarea y subida inicial de cambios
Con la rama creada, se procede al desarrollo de la tarea. Durante esta fase, es recomendable realizar commits periódicos, especialmente si se desea compartir los avances con otros miembros del equip. Para subir los cambios se ejecutan los comandos git add ., git commit -m "mensaje-del-commit" y git push. Es importante respetar el formato de Conventional Commits, lo cual facilita la comprensión del historial y permite automatizar procesos como el versionado semántico. El mensaje del commit deberá seguir la estructura “feat: descripción del cambio” para nuevas funcionalidades o “fix: descripción del cambio” para correcciones. El mensaje debe ser claro, breve y descriptivo.

### 4 Ejecución de pruebas
Una vez completada la implementación, se debe realizar un conjunto de pruebas que validen la calidad y el correcto funcionamiento de los cambios. Entre las pruebas contempladas se incluyen pruebas de interfaz utilizando Selenium, pruebas de carga con Locust y pruebas unitarias. Tras completar las pruebas, , es necesario subir estos cambios a la rama siguiendo los comandos anteriores. Si el commit contiene únicamente pruebas, el prefijo adecuado será “test”, en caso contrario será el descrito en el paso anterior, manteniendo el estándar de Conventional Commits.

### 5 Integración de cambios en la rama trunk
Cuando la tarea ha sido desarrollada y validada con las pruebas correspondientes, llega el momento de incorporar los cambios en la rama trunk del proyecto. El procedimiento consiste en ejecutar git checkout trunk, git merge nombre-de-la-rama y git push. Esto actualiza la rama trunk con el nuevo código. Luego, la tarea se mueve a la columna REVIEW del tablero, indicando que está lista para ser revisada por el equipo. Si los miembros consideran que los cambios son correctos, la tarea pasa a DONE. Si se requieren correcciones, se vuelve al paso 3 para aplicar los cambios necesarios, subirlos de nuevo y repetir el proceso de revisión. Para este paso, el equipo dispondrá del despliegue de la rama trunk en render, cuya finalidad es el desarrollo así como análisis en Sonar Cloud y Codacy del código como ayuda para revisar el código realizado.

### 6 Integración en rama main
Por último, cuando el equipo de desarrollo considera oportuno generar una nueva release, se procede a integrar los cambios de la rama trunk en la rama main y a crear una nueva etiqueta de versión. Para ello, se ejecutan los siguientes comandos en este orden: git checkout main, git merge trunk, git push, git tag -a version, y finalmente git push origin version. La versión asignada debe seguir el esquema de versionado semántico, es decir, el formato MAJOR.MINOR.PATCH. En este sistema, MAJOR se incrementa cuando se realizan cambios que rompen la compatibilidad del proyecto, MINOR se utiliza para añadir nuevas funcionalidades que no afectan la compatibilidad y PATCH se incrementa cuando se realizan correcciones de errores o mejoras menores que no modifican el comportamiento general del sistema.


### Conclusiones y trabajo futuro
Se enunciarán algunas conclusiones y se presentará un apartado sobre las mejoras que se proponen para el futuro (curso siguiente) y que no han sido desarrolladas en el sistema que se entrega