from typing import Union
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

# fastapi dev main.py


earthquakes = [
    {"magnitude": 7.8, "location": "23 km al SE de Valparaíso", "date": "2024-03-15 18:29:13", "depth": "135 km", "latitud": -33.15, "longitud": -71.40},
    {"magnitude": 6.2, "location": "129 km al NE de Santiago", "date": "2024-02-28 18:02:59", "depth": "12 km", "latitud": -32.50, "longitud": -69.80},
    {"magnitude": 8.1, "location": "81 km al NO de Antofagasta", "date": "2024-01-10 16:34:34", "depth": "45 km", "latitud": -23.20, "longitud": -70.80},
    {"magnitude": 5.9, "location": "20 km al N de Concepción", "date": "2024-01-05 14:37:37", "depth": "49 km", "latitud": -36.60, "longitud": -72.95},
    {"magnitude": 7.3, "location": "68 km al S de Iquique", "date": "2023-12-20 14:31:27", "depth": "28 km", "latitud": -20.80, "longitud": -70.20},
    {"magnitude": 6.7, "location": "54 km al E de La Serena", "date": "2023-11-18 13:50:44", "depth": "40 km", "latitud": -29.90, "longitud": -70.20},
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
            table { border-collapse: collapse; width: 100%; font-size: 14px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .highlight { font-weight: bold; color: #003399; background-color: #eef; }
        </style>
    </head>
    <body>
        <h1>Terremotos recientes en Chile</h1>
        <table>
            <tr>
                <th>Fecha Local / Lugar</th>
                <th>Profundidad</th>
                <th>Magnitud</th>
            </tr>
    """
    
    for earthquake in earthquakes:
        html_content += f"""
            <tr>
                <td><span>{earthquake['date']}</span><br>{earthquake['location']}</td>
                <td>{earthquake['depth']}</td>
                <td>{earthquake['magnitude']}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    return html_content

class TerremotoData(BaseModel):
    magnitude: float
    location: str
    date: str
    depth: str
    latitud: float
    longitud: float


@app.get("/api/terremotos")
def get_terremotos_json(latitud: float = None, longitud: float = None, timestamp: str = None, limit: int = 10):
    if latitud is not None or longitud is not None or timestamp is not None:
        terremoto_solicitado = []
        for terremoto in earthquakes:
            terremoto_encontrado = True
            if latitud != terremoto.get("latitud"):
                terremoto_encontrado = False
            if longitud != terremoto.get("longitud"):
                terremoto_encontrado = False
            if timestamp != terremoto.get("date"):
                terremoto_encontrado = False
            
            if terremoto_encontrado:
                terremoto_solicitado.append(terremoto)
        return {"terremotos": terremoto_solicitado[:limit]}

@app.post("/api/terremotos")
def add_terremotos(terremoto: TerremotoData):
    earthquakes.append(terremoto.dict())
    return {"message": "Terremoto añadido con éxito."}

