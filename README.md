# Lake Scale Installation  

An interactive installation that allows visitors to physically experience the scale of lakes.

Visitors place lake models on a table, and the system detects them using computer vision.  
The surface area of the lakes is then visualized in real time through projection.

By translating geographic data into physical objects and interactive visualization, the work explores the relationship between **abstract numerical information and bodily perception**.

---

# Concept

In contemporary society, almost any information can be obtained through search.  
However, information understood through numbers and data is often detached from our physical sense of scale.

This work visualizes lake surface areas through projection, allowing visitors to experience the gap between **information acquired through data** and **information understood through direct experience**.

## The "Tatami" Logic
One of the core features of this work is the visualization of area through **Tatami mats**.
While 670 km² is just a number, seeing it filled with **413,580,246 Tatami mats** creates a sense of "informational density" that can be felt intuitively.
The system dynamically scales the texture density in TouchDesigner to ensure that each individual mat remains visible as a grain, even for massive lakes.

---

# System Architecture

```

Lake Models (3D printed)
        ↓
ArUco markers (bottom of model)
        ↓
Camera inside table
        ↓
OpenCV + ArUco detection
        ↓
Python logic
        ↓
OSC communication
        ↓
TouchDesigner
        ↓
Top-down projection
        ↓
Visualization on tabletop

```

---

# Installation Setup

The installation consists of a table with an acrylic top surface.

Visitors place lake models on the table.
Each model contains an ArUco marker on its bottom surface, which is tracked by a camera hidden inside the table.

The detected marker IDs are processed using Python and OpenCV, and the lake data is sent to TouchDesigner via OSC.

A projector placed above the table projects the visualization directly onto the tabletop.

---

# Lake Models

The installation uses 30 different lake models produced using 3D printing.

- Scale: 1:100,000

- Largest model: Lake Biwa (~60 cm)

- Material: 3D printed shell + transparent resin surface

The models represent only the silhouettes of the lakes, extracted from geographic data.
Surrounding terrain is intentionally removed in order to focus on the shape and scale of the lakes themselves.

Each model functions both as a sculptural object and as a tangible interface for the interactive system.

---

# Interaction

Visitors can freely place and move the lake models on the table.

The spatial position of the models does not affect the visualization.
Instead, the system responds to which lakes are present, calculates their total surface area, and visualizes the resulting scale.

Visitors interacted with the installation in different ways:

placing lakes one by one to compare their sizes

combining multiple lakes to observe the accumulation of area

This exploratory interaction allows visitors to discover the system behavior through physical engagement.

---

# Technologies

- Python

- OpenCV

- ArUco Marker Detection

- python-osc

- TouchDesigner

- Projection Mapping

- 3D Printing

--- 

# Data

Lake models were generated from publicly available geographic datasets.

Source:
Geospatial Information Authority of Japan (GSI)

---

# Running the Program

Install dependencies:

```
pip install opencv-python
pip install python-osc
pip install numpy
```
Run the program:

```
python main.py
```

---

# Repository Structure

```
lake-scale-installation
│
├ python
│   ├ main.py
│   ├ lake_data.py
│   └ comparison_data.py
│
├ touchdesigner
│   └ visualization.toe
│
├ models
│   └ lake_models.stl
│
├ docs
│   ├ installation.jpg
│   ├ demo.gif
│   └ system_diagram.png
│
└ README.md
```

---

# Author

Graduation Project
Musashino Art University

---

# License (English Version)
This project is licensed under different terms depending on the component:

Source Code (Python): MIT License

You are free to use, modify, and redistribute the Python source code for any purpose, including research and development.

TouchDesigner Project (.toe): All Rights Reserved

The visual architecture, logic networks, and creative implementation within the TouchDesigner file are the intellectual property of the author.

Unauthorized redistribution, public exhibition, or use of this file for creating derivative installations is strictly prohibited.

3D Models & Media: All Rights Reserved

All 3D lake models, photographs, and video materials are the intellectual property of the author.
