import folium
from folium.plugins import MarkerCluster
import sqlite3
from django.http import JsonResponse
from django.shortcuts import render

def index(request):
    # Create a Folium map centered around a reasonable location
    folium_map = folium.Map(location=[52.0, 5.0], zoom_start=6)

    # Save the generated map to an HTML string
    folium_map_html = folium_map._repr_html_()

    # Pass the map to the template
    return render(request, 'opvarenden/index.html', {'map': folium_map_html})

def get_sailors_soldiers(request):
    start_year = request.GET.get('start_year')
    end_year = request.GET.get('end_year')

    # Validate that start_year and end_year are provided and are numeric
    try:
        start_year = int(start_year)
        end_year = int(end_year)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid year range'}, status=400)

    # Connect to the SQLite database directly
    db_path = '../notebooks/wic-opvarenden.db'  # Adjust path as necessary
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    query = """
        SELECT 
            P.name, 
            P.role, 
            L.label AS location_name, 
            L.country, 
            L.latitude, 
            L.longitude,
            D.deed_date
        FROM 
            Persons P
        JOIN 
            Locations L ON P.location_standardized = L.location_id
        JOIN 
            Transactions T ON P.person_id = T.sailor_id
        JOIN 
            Deeds D ON T.deed_id = D.deed_id
        WHERE 
            L.latitude IS NOT NULL 
            AND L.longitude IS NOT NULL
            AND strftime('%Y', D.deed_date) BETWEEN ? AND ?
    """
    
    # Execute the query with parameters
    cursor.execute(query, (str(start_year), str(end_year)))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Prepare the data for the JSON response
    markers = [
        {
            'name': row[0],
            'role': row[1] if row[1] else 'Unknown',
            'location_name': row[2],
            'country': row[3],
            'latitude': row[4],
            'longitude': row[5],
            'deed_date': row[6],
        } for row in rows
    ]
    
    return JsonResponse(markers, safe=False)
