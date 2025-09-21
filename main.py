from typing import Union
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# fastapi dev main.py

# Datos ficticios, hay que incorporar la latitud y longitud de estas pruebas.
earthquakes = [
        {"magnitude": 7.8, "location": "Valparaíso", "date": "2024-03-15", "depth": "35 km"},
        {"magnitude": 6.2, "location": "Santiago", "date": "2024-02-28", "depth": "12 km"},
        {"magnitude": 8.1, "location": "Antofagasta", "date": "2024-01-10", "depth": "45 km"},
        {"magnitude": 5.9, "location": "Concepción", "date": "2024-01-05", "depth": "8 km"},
        {"magnitude": 7.3, "location": "Iquique", "date": "2023-12-20", "depth": "28 km"},
        {"magnitude": 6.7, "location": "La Serena", "date": "2023-11-18", "depth": "22 km"},
    ]

@app.get("/", response_class=HTMLResponse)
def get_terremotos():
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terremotos en Chile</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>Terremotos recientes en Chile</h1>
        <table>
            <tr>
                <th>Magnitud</th>
                <th>Localización</th>
                <th>Fecha</th>
                <th>Profundidad</th>
            </tr>
    """
    
    for earthquake in earthquakes:
        html_content += f"""
            <tr>
                <td>{earthquake['magnitude']}</td>
                <td>{earthquake['location']}</td>
                <td>{earthquake['date']}</td>
                <td>{earthquake['depth']}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    return html_content

@app.get("/api/terremotos")
def get_terremotos_json():
    return {"terremotos": earthquakes}