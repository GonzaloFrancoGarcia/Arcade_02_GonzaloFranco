# Máquina Arcade Distribuida

Este proyecto implementa una “Máquina Arcade” distribuida en Python, compuesta por tres juegos clásicos de raíces algorítmicas:

- **N‑Reinas**  
- **Knight’s Tour**  
- **Torres de Hanói**  

Cada juego corre como un cliente independiente con interfaz en Pygame, y un servidor central recibe y almacena los resultados en una base de datos SQLite mediante SQLAlchemy.

---

## 📁 Estructura de carpetas

```plaintext
Arcade_01_GonzaloFranco/
├── README.md
├── requirements.txt
├── launcher.py
├── server/
│   ├── __init__.py
│   ├── main.py
│   ├── network.py
│   ├── models.py
│   └── db.py
├── clients/
│   ├── common/
│   │   ├── __init__.py
│   │   └── network.py
│   ├── nreinas/
│   │   ├── __init__.py
│   │   ├── game.py
│   │   └── ui.py
│   ├── caballo/
│   │   ├── __init__.py
│   │   ├── game.py
│   │   └── ui.py
│   └── hanoi/
│       ├── __init__.py
│       ├── game.py
│       └── ui.py
└── docs/
    └── informe.pdf
```

## ⚙️ Instalación y dependencias

1. Clona o descarga este repositorio y sitúate en la carpeta raíz:
```plaintext
git clone https://github.com/GonzaloFrancoGarcia/Arcade_01_GonzaloFranco
cd Arcade_01_GonzaloFranco
```

2. Crea y activa un entorno virtual (recomendado):
```plaintext
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

3. Instala las dependencias:
```plaintext
pip install -r requirements.txt
```

## 🛠️ Ejecución

1. Arranca el servidor. Abre una terminal nueva, sitúate en server/ y ejecuta:
```plaintext
cd server
python main.py
```

2. Lanza el launcher. Abre otra terminal, vuelve a la raíz y ejecuta:
```plaintext
python launcher.py
```

- **Variable de entorno**  
  Debes exportar tu Hugging Face API Key antes de arrancar cualquier cliente o el launcher:
  ```bash
  export HF_API_KEY="tu_token_aquí"      # Linux / macOS
  $Env:HF_API_KEY="tu_token_aquí"        # PowerShell
