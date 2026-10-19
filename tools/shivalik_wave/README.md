# Shivalik Wave 3D explorer, from the brochure floor plans (19 Oct 2026)

The 3D model on `shivalik-wave-sg-highway-ahmedabad.html` is built from the developer's own drawings,
not from the generic tower forms in `forms.py` / `t3d_auto.py`.

Sources
- Shivalik Wave brochure (24 pages) and "all floor plans" PDF (9 pages), as published on
  theestateroots.com/images/brochure/shivalik-wave-brochure.pdf and
  theestateroots.com/images/shivalik-wave/shivalik-wave-all-floor-plans.pdf
  (ground floor site plan; 1st, 2nd, 3rd, 4th, 5th, 6th-17th, 18th skip, 19th-24th and 25th-29th floor plans with unit tables).
- Official renders on shivalikgroup.com/projects/wave (two wave-shaped glass lobes facing S.G. Highway, 5-level podium,
  copper band at the 18th skip floor, service core along the back).
- Gujarat RERA unit register (CAA14544): 459 unit numbers; every floor's unit list matches the brochure exactly.

Method
1. `seg.py` finds each unit (beige fill) on the 220-dpi plan pages; `labels.py` maps each region to its unit number
   (checked on overlays) and holds the brochure tables (RERA carpet area, terrace, size).
2. `build_model.py` traces each floor's outline (terraces excluded), gives each unit its share of walls and facade,
   and converts to metres (5.45 px per foot, checked against the 10 ft passage and the 21'6" x 85'10" units).
   Frame: x along the building towards Vaishnodevi Circle (north-north-east), y towards S.G. Highway; origin at the
   centre of the 1st-floor outline. Output: `wave_geom.json`.
3. `assemble.py` writes the explorer config (`t3d.json`): one cell per unit on every floor, unit details,
   service-core prisms, podium terraces, roof parapets, the plot traced from the brochure site plan and the map
   placement (geo x 22.1, y 0.8, rot 75.5 = parallel to S.G. Highway, inside the RERA-mapped plot).
   Floor-to-floor heights (4.8 m ground, 3.9 m above) and parapet heights are estimates from the renders.

`tools/build.py` loads `tools/shivalik_wave/t3d.json` for this project (see the hook after the T3D table), so a full
site rebuild keeps this model. To regenerate: render the PDFs to fp/h-N.png and br/gf-12.png at 220 dpi, run seg.py
on each page, then build_model.py and assemble.py.
