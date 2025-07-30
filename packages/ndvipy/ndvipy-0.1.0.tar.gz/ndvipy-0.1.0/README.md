# NDVI Pro Python SDK (`ndvipy`)

Quickly generate NDVI visualisations in Python using your NDVI Pro API key.

```bash
pip install ndvipy  # once published to PyPI
```

```python
from ndvipy import NDVIClient

client = NDVIClient(api_key="YOUR_API_KEY")
ndvi_bytes = client.process_image("satellite.jpg")
with open("ndvi_result.png", "wb") as f:
    f.write(ndvi_bytes)
```

## Features
* Simple one-liner to process images
* Automatic API key authentication
* Logged usage appears in your NDVI Pro dashboard
* Zero dependencies besides `requests`

## License
MIT 