# Bakeri Stella – 3D explorer model

Built from the developer's 52-page CAD brochure for Stella (floor plans for basements, ground, 1st, 2nd, 3rd–20th, 21st skip floor, 22nd–33rd and the terrace; all plan pages share one page frame) and current satellite imagery.

* `geom.py` – traces floor plates from the brochure pages rendered at 300 dpi (`pdftoppm -r 300`). Scale 7.22 pt per metre, from the 300 mm stair treads; checked on the shop sizes printed on the ground-floor plan.
* `fit.py` – overlays the brochure plot and floor plates on Google imagery to fit position and rotation (GEO_GIFT frame: x = -29.1, y = -268.5, rotation -72.9°).
* `assemble.py` – writes `t3d.json` and the page config: three towers (Skye A, Sol B, Sygnus C) on a shared podium, the 2nd-floor amenity level with the pool deck, the 21st skip floor with the safe corridor across Sol's roof, planted bands and roof gardens (renders), the Sabarmati river (OpenStreetMap water area), GIFT City metro station, GIFT One & Two, and the projects next door as simple blocks from their own explorers (`neighbors.py`).
* Unit numbers and carpet areas stay as on the Gujarat RERA register; unit positions on each floor are indicative.

`tools/build.py` loads `t3d.json` in place of the generic form.
