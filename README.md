# Máquina Arcade Distribuida

Este proyecto implementa una **Máquina Arcade Distribuida** en Python, compuesta por tres juegos clásicos de raíces algorítmicas:

- **N‑Reinas**  
- **Knight’s Tour**  
- **Torres de Hanói**  

Cada juego corre como un cliente independiente con interfaz en **Pygame**, y un servidor central recibe y almacena los resultados en una base de datos **SQLite** mediante **SQLAlchemy**. Además se integra un asistente de IA basado en DialoGPT‑medium (local o vía Hugging Face), que ofrece sugerencias de jugada.

---

## 📁 Estructura de carpetas

```plaintext
Arcade_02_GonzaloFranco/
├── README.md
├── requirements.txt
├── resultados.db
├── launcher.py         
├── server/
│   ├── __init__.py
│   ├── main.py        
│   ├── network.py      
│   ├── models.py     
│   └── db.py          
└──  clients/
    ├── common/
    │   ├── __init__.py
    │   ├── network.py  
    │   ├── chat_ui.py  
    │   └── ia_client.py 
    ├── nreinas/
    │   ├── __init__.py
    │   ├── game.py     
    │   └── ui.py       
    ├── caballo/
    │   ├── __init__.py
    │   ├── game.py     
    │   └── ui.py       
    └── hanoi/
        ├── __init__.py
        ├── game.py     
        └── ui.py       

```

---

## ⚙️ Instalación y dependencias

Se recomienda Python 3.8 o superior.

1. **Clona** o descarga el repositorio y sitúate en la carpeta raíz:
   ```bash
   git clone https://github.com/GonzaloFrancoGarcia/Arcade_02_GonzaloFranco
   cd Arcade_02_GonzaloFranco
   ```

2. **Crea y activa** un entorno virtual:
   ```bash
   python -m venv venv
   # Linux/macOS
   source venv/bin/activate
   # Windows (PowerShell)
   venv\Scripts\Activate.ps1
   ```

3. **Instala** las dependencias:
   ```bash
   pip install -r requirements.txt
   ```


### Contenido de `requirements.txt`
```text
pygame>=1.9
SQLAlchemy>=1.4
transformers>=4.30.0
torch>=2.0.0
tk>=0.1.0
huggingface-hub>=0.16.4
requests>=2.25.1
``` 

> Si usas la opción remota de Hugging Face Inference API, también necesitarás `huggingface‑hub>=0.16.4` y definir la variable:
> ```bash
> export HF_API_KEY="<tu_token>"    # Linux/macOS
> $Env:HF_API_KEY="<tu_token>"      # PowerShell
> ```

---

## 🚀 Ejecución

### 1. Arrancar el servidor

Abre una terminal y ejecuta:
```bash
cd server
python main.py
```

### 2. Iniciar el launcher/menu

En otra terminal (en la raíz del proyecto):
```bash
python launcher.py
```

- Elige la opción **1‑3** para lanzar un juego (`nreinas`, `caballo` o `hanoi`).
- Opción **4** para ver resultados.
- Opción **5** para entrar al **chat IA** general.
- Opción **6** para **salir**.

### 3. Jugar y usar la ayuda IA

Dentro de cada juego, pulsa el botón **IA Help** para:
- **N‑Reinas**: resaltar casillas conflictivas y sugerir la siguiente posición.
- **Knight’s Tour**: mostrar movimientos posibles y sugerir el próximo salto.
- **Torres de Hanói**: indicar discos movibles y sugerir la siguiente torca.

La sugerencia de IA aparece en la parte inferior, con **texto adaptado** y **ajustado** a la ventana.

---

¡Listo! Disfruta y explora los puzzles con apoyo de IA.   
