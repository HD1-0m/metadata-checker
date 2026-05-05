import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pandas as pd

def get_geographical_info(exif_data):
    """Extracts GPS info into a readable format."""
    gps_info = {}
    for key, value in exif_data.items():
        tag_name = TAGS.get(key)
        if tag_name == "GPSInfo":
            for t in value:
                sub_tag = GPSTAGS.get(t, t)
                gps_info[sub_tag] = value[t]
    return gps_info

def convert_to_decimal(coordinates, reference):
    degrees, minutes, seconds = coordinates
    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    if reference in ["S", "W"]:
        decimal = -decimal
    return decimal

def format_gps_data(gps_data):
    readable_gps = {}

    if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
        latitude = convert_to_decimal(gps_data["GPSLatitude"], gps_data["GPSLatitudeRef"])
        readable_gps["Latitude"] = f"{latitude:.6f}° {gps_data['GPSLatitudeRef']}"

    if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
        longitude = convert_to_decimal(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])
        readable_gps["Longitude"] = f"{longitude:.6f}° {gps_data['GPSLongitudeRef']}"

    if "GPSAltitude" in gps_data:
        readable_gps["Altitude"] = f"{float(gps_data['GPSAltitude']):.2f} meters"

    if "GPSDateStamp" in gps_data:
        readable_gps["Date"] = str(gps_data["GPSDateStamp"]).replace(":", "-")

    if "GPSTimeStamp" in gps_data:
        hours, minutes, seconds = gps_data["GPSTimeStamp"]
        readable_gps["Time"] = f"{int(hours):02d}:{int(minutes):02d}:{int(float(seconds)):02d} UTC"

    if "GPSProcessingMethod" in gps_data:
        method = gps_data["GPSProcessingMethod"]
        if isinstance(method, bytes):
            method = method.replace(b"ASCII\x00\x00\x00", b"").replace(b"\x00", b"").decode(errors="ignore")
        readable_gps["Location Source"] = str(method)

    return readable_gps

def extract_metadata(image):
    # Get EXIF data
    exif_data = image._getexif()
    if not exif_data:
        return None
    
    metadata = {}
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        # Clean up large binary data (like thumbnails) to keep it readable
        if isinstance(value, bytes):
            value = value[:20] + b"..." 
        metadata[tag] = value
    return metadata

# --- UI Setup ---
st.set_page_config(page_title="Image Metadata Detector", layout="wide")
st.title("📸 Image Metadata (EXIF) Detector")
st.write("Upload an image to see its hidden metadata, camera settings, and location data.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "tiff"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, caption='Uploaded Image', use_column_width=True)
    
    with col2:
        st.subheader("Metadata Results")
        metadata = extract_metadata(image)
        
        if metadata:
            # Convert to Dataframe for a nice table
            df = pd.DataFrame(list(metadata.items()), columns=['Property', 'Value'])
            st.dataframe(df, use_container_width=True)
            
            # Special Check for GPS
            gps_data = get_geographical_info(image._getexif())
            if gps_data:
                st.success("📍 GPS Location Data Found!")
                readable_gps = format_gps_data(gps_data)
                gps_df = pd.DataFrame(list(readable_gps.items()), columns=["GPS Property", "Value"])
                st.dataframe(gps_df, use_container_width=True)
            else:
                st.warning("No GPS data found in this image.")
        else:
            st.error("No EXIF metadata found in this image. (Many social media sites strip this data for privacy).")
