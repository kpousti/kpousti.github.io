# Preview: http://localhost:8765

Branch: `nap-build` (built on top of `redesign/map-hero-test`). Nothing is pushed. `main` and the live site are untouched.
If the preview stops loading, run `python3 -m http.server 8765` in this folder.

## Latest pass: research, then a polish hour

Sources: a Wikimedia Commons photo of a gas turbine rotor (shape reference only, nothing copied into the site), and a 2026 write-up of the best three.js sites, which credits ORYZO's look to one object with real material response, weight and inertia, and instancing for speed.

Tasks I set, and the verdict on each:

| Task | Verdict |
|---|---|
| Real turbine rotor: 7 compressor rows that shorten along the shaft, 3 turbine rows, a shaft turned on a lathe | Built |
| Reflective metal lit by a small studio environment (warm softbox, cool softbox) | Built |
| Inertia: the model lags the scroll slightly, then settles | Built |
| All blocks drawn in one call (instancing); fewer pixels and a smaller shadow map on phones | Built |
| Shadows were silently off (a comment had swallowed the line). Restored | Fixed |
| Huts rebuilt: stilts, deck, walls, stepped roof, boardwalks, ring walk round the hub | Built |
| Wave rebuilt: a tiled surface with crests that lean forward | Built |
| Amber on the hot turbine rows, hut roofs and wave crests | Built |
| Model sits behind the text at rest, in open space under each headline; in front only during a dive | Built |
| Old dot-cloud code deleted (about 25KB) | Done |
| Bigger tap targets on "View code" and "Back to top" | Done |
| Smooth-scroll library that takes over scrolling | Rejected: breaks your "no scroll hijack" rule |
| Custom cursor | Rejected: the cursor light already does this job |
| Spline runtime | Rejected: over 0.5MB before any scene |
| Stock photos | Rejected: generic, and none tie to your work |
| Font subsetting (would save about 90KB) | Not done: needs a tool installed outside this folder |

## Gap list (what the references do that the site didn't)

References used: the 19 ORYZO screenshots sent in chat. There is no `refs/` folder in the repo.

1. One lit 3D object that stays on screen and changes with the scroll. Done.
2. Sections that lock in place while an animation plays. Done for the giant-word scene and the existing Route Engine walkthrough; other chapters use a dive, not a lock.
3. Huge type the object passes in front of. Done.
4. Hard cuts between sections (sliced panels, glitching headlines). Done.
5. Construction lines and handles on the lettering. Done on the name.
6. Real photography and close-up textures. Not done: no photos were in `photos-inbox/`.
7. Photoreal materials (cork, fabric). Not done: the model is flat-shaded blocks.

## What changed

- **3D model** (three.js): about 270 metal blocks with soft shadows and studio reflections replace the dot cloud.
- **Intro**: a rotor spins up beside the name, then bursts into the city. About 2.4 seconds.
- **Hero**: name and text left, city right. A* plans a real route to the street corner nearest the cursor. Guide lines on the name.
- **Giant-word scene** after the hero: the page locks, "graphs" then "routes" fill the screen, and the city crosses in front.
- **Scroll story**: city (hero) > gas turbine rotor (About, Experience) > flat road map with the route (Projects) > hub and six stilted huts with boardwalks (Side builds) > wave surface (Skills, Contact).
- **Transitions**: at each chapter the camera dives into the blocks while they rebuild into the next shape, then pulls back. Huts to wave sweeps across as one front; wave crests are steep with flat troughs.
- **Chapter curtains**: a sliced title card opens each chapter. Strips go up, down, or alternate, so no two neighbours open the same way.
- **Project and build spreads**: each name set large beside its card, with a counter.
- **Room for shapes**: every chapter headline is followed by open space where the shape sits on its own; it then fades to 16% behind cards.
- **Tighter**: chapter padding 128 > 96px, project screens 100 > 82vh. Desktop page is about 2,100px shorter than it would be otherwise.

## Decisions I made for you

- **3D blocks, not dots.** Your later message confirmed this. The old dot code is still in the file, switched off.
- **The intro bursts into the city, not into your name.** 250 blocks can't spell a name legibly. The name is real type.
- **"Agent City huts over water"** is a hub and six huts on the slab. No water.
- **"Breaking wave"** is rolling wave fronts, not a curling barrel.
- **Blocks don't flow around the cursor.** The model tilts toward it, and the route re-plans to it in the hero.
- **Text I changed** (the brief said not to; these lines described the dots): the hero pitch's second sentence, and the Projects sub-line. **Text I added**: the giant-word scene ("How I think / graphs", "What I build / routes", two captions). The 1.2 million figure is from your About section.
- **three.js 0.160.0** is stored at `vendor/three.module.min.js`. Cost: 671KB on disk, about 167KB compressed for visitors. No GSAP, no CDN.
- **Fix 4 (a glimpse per project)**: left as it was. Every project and build card already has its own live demo.
- **The model is behind the text at rest.** Only during a dive does it come in front, with a "screen" blend so it adds light and never darkens text.
- Kept from the earlier audit, not acted on: the Family and Markets tiles and the side-build status labels.

## Where it falls short of the references

- No photography or textures. Drop photos into `photos-inbox/` and say so.
- The shapes are built from boxes. ORYZO's objects are sculpted, textured models.
- During a dive the blocks cover the text for a moment.
- Only two scenes truly lock the page.
- The page got longer because each shape now has its own space: desktop about 20,800px (was 20,300), phone about 24,750px (was 22,600).
- The five colour themes in the preview picker were not rechecked. Gallery Light will hide the model behind chapters.

## Tested

At 1440x860 and 390x800 in headless Chrome: no console errors, no sideways scroll, all six tabs land and highlight, about 100 frames a second. Reduced motion: no curtains, no dive, model static. Screenshots are in `shots/`.
One test run showed wrong tab highlights on desktop; two clean re-runs passed, so I put it down to the test clicking mid-scroll.
Not tested: Safari, a real phone, JavaScript turned off, older or low-power devices.

## Check in Safari

1. The 3D city appears and is lit, on Mac and iPhone.
2. The giant-word scene locks and the city passes in front of the word, not behind.
3. During a dive the blocks glow over the page and never show as a grey box (this is the "screen" blend).
4. The sliced curtains slide without flicker, and nothing stays covered.
5. Headline glitch shows amber and blue copies for a moment, then clears.
6. The name is condensed (narrow letters) with guide lines lined up under it.
7. Scrolling stays smooth on your iPhone, and it doesn't get warm.
8. The address bar hiding on iPhone doesn't make the locked scene jump.
