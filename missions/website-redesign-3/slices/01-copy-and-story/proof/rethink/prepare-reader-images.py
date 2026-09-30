"""Build ordered reader derivatives from frozen originals, retaining every original."""
import hashlib
import json
from pathlib import Path
import sys
from PIL import Image

phase = Path(sys.argv[1])
layouts = json.loads((phase / 'layout.json').read_text())
shots = phase / 'shots'
shots.mkdir(exist_ok=False)
manifest = []
provenance = []


def save(image, relative, source, operation):
    if max(image.size) > 7000:
        image.thumbnail((7000, 7000), Image.Resampling.LANCZOS)
        operation += '; resized to max dimension 7000'
    target = phase / relative
    image.save(target, quality=90)
    manifest.append(relative)
    provenance.append({'path': relative, 'source': source, 'operation': operation,
                       'width': image.width, 'height': image.height,
                       'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})


# Two long views first, then desktop sections in order, then mobile sections.
for width in (1440, 390):
    source = f'original/full-{width}.jpg'
    with Image.open(phase / source) as original:
        save(original.copy(), f'shots/full-{width}.jpg', source, 'full page')
for width in (1440, 390):
    source = f'original/full-{width}.jpg'
    with Image.open(phase / source) as original:
        scale = original.width / width
        layout = layouts[str(width)]
        if abs(original.height / scale - layout['height']) > 5:
            raise ValueError(f'Original screenshot height does not match stable layout at {width}')
        for section in layout['sections']:
            top = max(0, round(section['top'] * scale))
            bottom = min(original.height, round((section['top'] + section['height']) * scale))
            save(original.crop((0, top, original.width, bottom)),
                 f'shots/{section["id"]}-{width}.jpg', source,
                 f'section crop at pixel top {top}, bottom {bottom}')
(phase / 'reader-images.json').write_text(json.dumps(manifest, indent=2) + '\n')
(phase / 'image-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
print(f'{phase.name}: prepared {len(manifest)} ordered images with originals retained')
