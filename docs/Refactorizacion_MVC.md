# 🧠 Documentación de Refactorización MVC — Proyecto Interfaz Estilo Celular

Este documento describe los cambios estructurales y funcionales realizados durante el proceso de refactorización del código del proyecto, enfocados en una arquitectura **MVC (Modelo-Vista-Controlador)** más clara y sostenible.

---

## 📁 Estructura General del Proyecto (Post-Refactorización)

```
Proyecto_1/
├── controller/
│   ├── main_controller.py
│   ├── menu_controller.py
│   ├── ajustes_controller.py
│   ├── apps_controller.py
│   └── llamadas_controller.py
├── model/
│   ├── __init__.py
│   ├── ajustes_model.py
│   ├── apps_model.py
│   ├── llamadas_model.py
│   ├── disco_model.py
│   └── menu_model.py
├── view/
│   ├── __init__.py
│   ├── ajustes.py
│   ├── apps.py
│   ├── llamadas.py
│   ├── menu.py
│   ├── icono.py
│   ├── fondo.py
│   └── screen.py
├── docs/
│   └── REFACTORIZACION_MVC.md  ← este archivo
└── main.py
```

---

## 🎯 Objetivo de la Refactorización

Simplificar y modularizar la lógica del proyecto original, separando responsabilidades de **interfaz**, **controlador** y **modelo** bajo el paradigma MVC, para facilitar el mantenimiento, pruebas y escalabilidad.

---

## 📦 Cambios en `model/`

### `apps_model.py`
- Contiene funciones relacionadas con la obtención de apps desde `adb`.
- Se separó `obtener_apps_menu()` hacia un nuevo módulo `menu_model.py`.

### `menu_model.py`
- Define las apps visibles en el menú principal (iconos, colores, texto y función asociada).

### `llamadas_model.py`
- Centraliza la obtención del historial de llamadas desde `adb`.

### `ajustes_model.py`
- Contiene `actualizar_info_adb()`, que detecta dispositivos ADB conectados.

### `disco_model.py`
- Implementa `execute_df_h()` para consultar el uso de almacenamiento en el dispositivo vía `adb`.

### `__init__.py` en `model`
- Expone funciones comunes mediante importaciones desde los módulos anteriores.

---

## 🎮 Cambios en `controller/`

### `main_controller.py`
- Controlador principal que orquesta toda la navegación y lógica de alto nivel.
- Se conecta con las pantallas `menu`, `ajustes`, `llamadas`, `apps`.
- Delega la creación del menú a `menu_controller.py`.
- Conecta botones y acciones con vistas mediante métodos como `mostrar_pantalla_X`.

### `menu_controller.py`
- Crea la interfaz principal (menú).
- Utiliza `menu_model.py` para definir las apps mostradas.
- Recibe un diccionario de funciones del `main_controller` para manejar eventos.

### `ajustes_controller.py`
- Crea la vista de ajustes.
- Usa `actualizar_info_adb()` desde `ajustes_model.py` para mostrar los dispositivos conectados vía ADB.
- Gestiona el refresco de datos y la lógica de validación.

### `apps_controller.py`
- Se conecta a la vista `apps.py`.
- Usa `obtener_apps_instaladas()` de `apps_model.py` para mostrar las apps reales si hay un dispositivo conectado.
- Fallback automático a una lista de ejemplo en caso de error ADB.

### `llamadas_controller.py`
- Gestiona la vista `llamadas.py`.
- Utiliza `obtener_llamadas()` desde `llamadas_model.py`.
- Muestra errores si no hay dispositivos o ADB falla.

---

## 🖼️ Cambios en `view/`

### Modularización mantenida
No se hicieron refactorizaciones profundas aquí salvo lo siguiente:

- `menu.py`: ahora espera una lista de apps y un diccionario de funciones externas para construir dinámicamente el menú.
- `icono.py`: widget personalizado para representar cada app.
- `screen.py`: plantilla base con barra de título y botón de retroceso.
- `llamadas.py`, `ajustes.py`, `apps.py`: utilizan `AppScreen` para mantener consistencia visual.

---

## ✅ Resultados

- Código más organizado y legible.
- Separación estricta entre lógica, presentación y control.
- Más fácil de testear, mantener y escalar.
- Mayor flexibilidad para cambiar vistas o lógica interna sin romper la estructura principal.

---

## 📌 Próximos Pasos Recomendados

- Documentar cada archivo `.py` con docstrings modulares.
- Crear pruebas unitarias para los métodos en `model/`.
- Considerar añadir manejo de errores más robusto (logs, mensajes en UI, etc.).
- Agregar animaciones/transiciones entre pantallas.

---

_Última actualización: 31 mayo 2025 — por Danitza Lazo_
