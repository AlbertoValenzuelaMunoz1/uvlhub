# 📄 Guía de Gestión de Desarrollo

Esta guía establece el flujo de trabajo estándar para la gestión de commits, ramas y tareas en nuestro proyecto.

---

## 1. 🌳 Modelo de Ramas (Branching Model)

### 1.1. Ramas Principales (Long-Lived Branches)

| Rama | Propósito | Uso y Reglas Clave |
| :--- | :--- | :--- |
| **`main`** | **Código estable/producción.** Contiene el código más probado y listo para *releases*. | **Solo se hacen *merges*** de la rama `trunk` para crear una nueva versión (*release* o *tag*). **Nunca se commite directamente.** |
| **`trunk`** | **Rama principal de desarrollo.** Contiene la última versión del código en desarrollo activo. | Todas las ramas de tarea (*features*, *bugfixes*) deben ser *merged* en `trunk`. |

### 1.2. Ramas de Tarea (Short-Lived Branches)

* **Creación:** Siempre se deben crear a partir de la rama **`trunk`**.
* **Nomenclatura (Recomendada):** `[tipo-de-tarea]/[descripcion-corta]`
    * **Ejemplos de Tipos:**
        * `feat-task/descripción-de-la-funcionalidad`: Nuevas funcionalidades (ej: `feat/fakenodo`).
        * `bugfix/arreglo-de-código`: Solución de errores (ej: `fix/nombramiento-de-usuario`).
* **Integración:** Se debe realizar un **merge** para fusionar la rama de tarea en **`trunk`**.
* **Eliminación:** Una vez fusionada en `trunk`, la rama de tarea debe ser eliminada.

---

## 2. 📝 Convención de Commits (Commit Messages)

Utilizamos el formato **Conventional Commits** para una trazabilidad clara.

### 2.1. Formato Básico

El mensaje debe seguir el formato:

**`<tipo>(<ámbito>): <descripción-corta>`**

* **`<tipo>`:** Debe ser una de las palabras clave de tarea (ej: `feat`, `fix`, `test`).
* **`<descripción-corta>`:** Un resumen conciso de la acción realizada.

> **Ejemplo Válido:**
> `feat: Mostrar datasets más populares por visitas y descargas`

---

## 3. 📅 Gestión de Incidencias y Tareas (Kanban)

Todas las tareas (incidencias, *features*) se gestionan a través de nuestro tablero Kanban en GitHub.

### 3.1. Flujo de Tareas

Toda tarea debe pasar por las siguientes columnas:

| Columna | Estado | Acción Requerida |
| :--- | :--- | :--- |
| **To do** | **Pendiente de iniciar.** | Tareas definidas y priorizadas. |
| **In progress** | **Desarrollo activo.** | El desarrollador está trabajando en el código. Se debe crear la rama de tarea asociada. |
| **In review** | **Pendiente de revisión.** | El código espera aprobación de otro desarrollador. |
| **Done** | **Completado y Fusionado.** | El código ha sido aprobado por otro desarrollador y fusionado en la rama `trunk`. |