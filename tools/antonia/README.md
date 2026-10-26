# Antonia: page data, gallery and 3D explorer from the developer's brochure (26 Oct 2026)

Source: Antonia Infra LLP brochure "SPIRAL BOOK 22-06-26" (14 pages, June 2026), supplied by the owner:
renders (pp. 2-3), drop-off / entrance foyer / front entry / lift foyer / common open plot images (pp. 4-6),
floor plans with super built-up tables: ground (p. 7), 1st & 2nd (p. 8), 3rd-20th (p. 9), 21st skip (p. 10),
22nd-31st (p. 11), 32nd-42nd (p. 12), and the section with floor-to-floor heights (p. 13).

- `build_antonia.py` traces each floor plate and every showroom/office from the plans rendered at 300 dpi
  (13.25 px per foot, checked against the 12'6" foyer and the 14'0" offices) -> `antonia_geom.json`.
- `assemble_antonia.py` writes `t3d.json`: 43 levels (G + 42), 181 units, heights from the section
  (4.5 m ground, 4.275 m floors 1-2, 3.2 m floors 3-20, 3.35 m floors 21-31, 3.65 m floors 32-42; terrace 147.65 m),
  the dark blade and crown frame from the renders (sizes estimated), plot / garden / ramp from the site plan,
  map placement aligned with S.G. Highway and the 12 m road.
- `gallery.json`: the brochure images (assets/img/ext/antonia-*.webp) and building highlights shown on the page.

`tools/build.py` loads `t3d.json` (hook after the T3D table) and renders `gallery_section(p)` for listings with
`gallery=True` in props_build.py, so a full rebuild keeps all of this.
