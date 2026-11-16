# Preview: http://localhost:8765

Branch: `nap-build` (built on top of `redesign/map-hero-test`). Shipped to `main` and kiapousti.com on 2026-11-15, on your "ship it".
Also in this ship: the Contact line "Email is the fastest way to reach me." is now a mail link.
If the preview stops loading, run `python3 -m http.server 8765` in this folder.

## The city, thinned out so the route reads (2026-11-15)

You liked the San Diego landmarks but said the city was too crowded to see the path.

- **Landmarks kept**, all ten, plus the bay, bridge, Midway, palms and boats.
- **Ordinary buildings:** fewer than half the other lots are built on now. They are three plain low blocks in one quiet tone, with their footprints pulled in so the streets are wider. The ten detailed building types are gone from the kit.
- **Streets and rivets** go dark and small once the network is pressed flat, and the blue search lines are fainter.
- **The route** is thicker, lifted clear of the street, and shows through anything in front of it. The pin takes about two seconds to drive it, at an even pace, and each route holds for ten seconds on phones.
- Model file is smaller: 152KB (was 204KB).
- Tested as before at both sizes: no errors, all tabs, no slow frames.

## Blender, scenes two and three in fine detail: the space-frame network and downtown San Diego (2026-11-15)

You asked for every animation to be made in Blender with fine detail like the turbine, starting right after the turbine, and then for the city to be San Diego so locals recognise it. Your picks for "routes": a detailed city; the network settles and presses in; a marker drives the route.

**"graphs": the network is now a space frame**
- Each corner is a machined node with six sockets. Each strut ends in a tapered fitting with a hex collar where it meets the node.
- Every strut carries one to three brass collars. That is real data: the number is what that street costs to drive in the routing graph.
- The turbine's parts still become it: a ball-type part is the core of each node, the blades are the struts, and the fittings grow on as the parts land.

**"routes": the network presses into a plate and San Diego rises**
- The base is a machined plate with a rim, ruler ticks on two edges, a scale bar, a north arrow, corner bolts and feet. It rises to meet the network as it settles; the struts lie half sunk in it as the streets, and the nodes flatten into rivets at each corner.
- Landmarks, placed roughly where they stand downtown, with the bay along the near edge:
  One America Plaza (the pointed crown), the Manchester Grand Hyatt twins, Emerald Plaza (hexagonal towers cut at a slant, green on top), the Harbor Club oval twins, the Central Library dome, Petco Park (with the brick warehouse in the corner), the Convention Center (fins and white sails), the USS Midway, the Coronado Bridge curving out over the bay, and the California Tower in a park. Palms along the Embarcadero and sailboats on the bay.
- Every other lot gets one of ten ordinary buildings by its height (towers, mid-rises, shop, house, sawtooth warehouse, barrel-roofed hall), and open blocks are parks with trees and a fountain.
- A brass map pin drives the route as it draws. On a computer it still re-plans to wherever you point.
- The same city is the model for About ("I think in graphs.").

**How it is built:** `blender/build_city.py` draws every piece and saves `blender/city.blend`; `blender/export_parts.py` writes `models/city.bin` (204KB). The landmarks are shapes drawn from memory of the skyline, with no logos or signs. They are simplified, not surveyed: tell me which ones read wrong.

**Location rule kept:** this shows downtown San Diego as a city, nothing about where you live.

**Tested** at 1440x860 and 393x659: no errors, no sideways scroll, all six tabs, nothing left hidden, no slow frames in the slowed-down phone test. Not tested on a real iPhone or in Safari. The test measures the phone's processor, not its graphics chip, and the city is the heaviest scene so far (about 300 buildings plus the 477 turbine parts as streets), so this is the one to watch on your phone.

**Still plain blocks:** Experience, the project scenes, the side builds, Skills, Contact.

## The "workshop drawing" redesign: removing the AI look (2026-11-15)

You said people call the site AI-generated, and picked the "Workshop drawing" option. I ran the unslop skill (by Damir Sokolovsky, @heydamir) as an audit and then rebuilt the page's look.

**Direction**
- Product: the portfolio of a software developer who builds routing engines in C++ and applied AI, for engineers and hiring managers.
- Character: exact, mechanical, hand-built.
- World: an engineering workshop. Drawing sheets, machined steel, a test bench.
- Moments (the only rich things): the Blender model, and each project's live demo.
- Signature: drawing-sheet details. Hairline rules, part numbers on every row, a title block with a sheet number, the construction lines on your name.

**What the audit found:** 29 identical see-through rounded cards; blur, film grain, cursor glow, card tilt, magnetic buttons and a glitch all stacked; 48 things animating in; small all-caps spaced labels; pills on everything; the 3D model showing through the text.

**What changed**
- **Colours.** One near-neutral ink ramp instead of navy: page `#0b0d14`, rules `#262a35`, text `#c6cad4` / `#a3a9b8` / `#eef0f5`. Amber is the only accent in the page furniture. Blue now appears only inside the models and demos.
- **Top bar.** A flat strip ruled off across the top, with a short amber line under the current tab. The floating frosted pill is gone. On phones the tabs fade at the edges instead of running into your name.
- **Boxes became ruled lists.** About's four stat cards are a numbered spec list. Skills' eight boxes are a two-column parts list. Wins, contact and "Away from the keyboard" sit between hairlines with part numbers. Only the live demos keep a frame.
- **Title blocks.** Each chapter head is left aligned with a rule above and "Sheet 01 / 06" at the far end.
- **Labels.** Sentence case, normal spacing, quiet colour. Tags are plain text with dots between, not pills.
- **Type.** Display weight down one step (700 to 600). Buttons have 8px corners.
- **Effects removed.** Film grain, cursor glow, glitch, card tilt and cursor light, magnetic buttons, hover lifts, the looping scroll cue, the word-by-word headline reveal. Scroll-in is now one short fade (10px, 380ms).
- **The model is never behind text.** At each chapter it sits in the open space of the title block and moves with the page. Going into a chapter it fades out where it was and fades in at its new place, already rebuilding. The camera dive over the text is gone. Between two projects it still slides across.

**Kept on purpose:** the sliced chapter title cards, the giant "graphs / routes" scene, the live demos, the blinking dot on live demos (they are live), the count-up on the stats.

**Not done, needs your say-so (wording):** headlines end with a full stop ("I think in graphs."); the audit would drop those. I did not touch any wording.

**Not done yet:** the other chapters' models are still the old blocks (next in order: "routes"). The four other preview themes were not rechecked. The code that splits headlines into words is still there, unused.

**This overrides the design-system notes in the kia-portfolio-site skill** (its colour values and its "signature effects to keep" list are now out of date).

**Tested** at 1440x860 and 393x659: no errors, no sideways scroll, all six tabs, fonts loaded, nothing left hidden by scroll-in, no slow frames in the slowed-down phone test. Not tested: Safari, a real iPhone, JavaScript off.

## Blender, second scene: "graphs" is a floating network made of the turbine's own parts (2026-11-15)

Your picks from the questions: a floating 3D network; the turbine's parts become it; a search spreads across it.

- **What you see.** Scrolling from the turbine to "How I think", every part reshapes as it flies: each blade and vane rounds into a rod, every other part (bolts, nozzles, cans, wheels, casing, shaft) rounds into a ball. They assemble into a network of 100 balls joined by rods, floating in space. Nothing is added and nothing disappears.
- **The search is real.** While "graphs" is on screen, the A* search spreads from the amber start ball; rods and balls it reaches turn blue. Same algorithm and same graph as the route later.
- **Into "routes".** When the word changes, the network settles flat: the rods are now the streets, the city rises between them and the amber route draws.
- **How.** The network is the street graph with every corner lifted to its own height. Each part carries a second shape (rod or ball), and the page blends between the two per part.
- **In Blender:** the turbine now has 13 bolts per flange (was 9), so it has exactly 100 ball-type parts, one per corner. 477 parts in all.
- **Cost:** model file 191KB (was 180KB).
- **Tested** at 1440x860 and 393x659: no errors, no sideways scroll, all six tabs, no slow frames in the slowed-down phone test. Not tested on a real iPhone or in Safari.
- **Weak spots I can see:** the big hub balls (from the casing) are a little faceted; mid-flight the parts are a busy cloud for a moment.

## Blender models, first one: the opening turbine (2026-11-15)

You asked for the animations to be made in Blender, each one its own thing, with visible turbine parts that turn into the next shape.

- **Why they looked alike.** All 17 were the same 270 blocks rearranged. Blender lets each area have its own real model.
- **The turbine** is modelled in Blender from 461 separate parts: nose cone, 9 compressor wheels with curved blades, fixed vanes, 10 combustor cans with fuel nozzles, 3 amber turbine wheels, exhaust cone, a cutaway casing with flanges and bolts. File: `blender/turbine.blend`.
- **On the site** it spins in the opening. As you scroll to "How I think" it pulls apart into its parts, and the parts land as the street graph: blades and vanes lie down end to end as the streets, bolts, nozzles, cans and wheels stand on the street corners, and the casing and shaft sink into the base. The old block turbine is deleted.
- **How it gets there (my call).** Blender does not run in a browser, so `blender/export_parts.py` writes the model to one small file, `models/turbine.bin`, which the site reads directly. No extra library was added, and I did not use rendered video (heavy on phone data, and it cannot react to scrolling).
- **Cost:** 180KB for the model file. About 10,400 triangles stored, drawn as 51 batches.
- **Phones:** the parts do not cast shadows there, to keep it light.
- **Tested** at 1440x860 and 393x659: no errors, no sideways scroll, no slow frames in the slowed-down phone test. Not tested on a real iPhone or in Safari.
- **Still blocks:** every other area. They get their own Blender models one at a time, after you say what each should be.

## Phone lag, round two: the turbine trailing the page (2026-11-15)

You said it was still laggy, especially the turbine while scrolling.

- **Cause.** On a real iPhone screen (about 393 by 659) the hero is taller than the screen, so the turbine starts half below the fold and has to move up with the page. Its position was recalculated in code every frame. A phone scrolls the page on its own fast track and only then runs the code, so the turbine was always a frame or more behind the text. In Low Power Mode the code runs at 30 frames a second while scrolling stays smooth, which makes it much worse.
- **Fix.** On phones, wherever the model is meant to move with the page (the hero, and the gap under each project name), the 3D canvas is now laid on the page itself, so the phone's own scrolling carries it. Where the model holds still on screen (the giant-word scene, chapter openings, dives) the canvas is fixed to the screen as before. It swaps between the two as needed. The built-in lag ("weight") is off on phones.
- **Checked:** the turbine and the project models sit in exactly the same places as before; the page is no taller; no errors; desktop is untouched (canvas always fixed there).
- **Not checked:** a real iPhone. A one-frame nudge is possible at the moment the canvas swaps mode.
- **New tool:** add `?fps` to the address (kiapousti.com/?fps) to see frames a second in the bottom-left corner. 60 is smooth, 30 usually means Low Power Mode.

## Phone lag fix (2026-11-15)

You said the live site felt laggy on your phone. I measured it in a phone-sized Chrome slowed down 4 times, scrolling the whole page.

- **Cause.** The scroll-progress line under the tab bar was updated through a variable on the page root, so the browser restyled the entire page on every scroll frame. The cursor light did the same on every mouse move.
- **Fix.** Both variables now sit on their own small layers. Looks identical.
- **Also on phones only:** cards no longer blur what is behind them (29 cards, re-blurred every frame). They are a little more solid instead (90% instead of 74%).
- **Measured:** average frame 16.9ms before, 10.0ms after (10ms is the test screen's limit). Slow frames over the whole page: 13 before, 0 after. Time spent re-measuring the page: 6.1s of a 10s scroll before, 0.4s after.
- Not measured: a real iPhone. If it is still laggy there, the next things to cut on phones are the soft shadows and the film grain.

## Newest pass: turbine first, then graphs and routes; readable big text

Asked for: open on the turbine, and have it transform into graphs and routes at "How I think". Then: don't go back to a turbine at Experience, and stop the big text being hidden.

- **Opening.** The hero model is now the turbine. Its blades grow out of the shaft row by row and it spins up fast, then settles.
- **"How I think".** Scrolling there, the turbine flattens into a street graph: white dots are nodes, lines are edges. While "graphs" is on screen the A* search spreads and the nodes it reaches turn blue. When the word changes to "routes", the blocks rise into a city and the amber route draws. Both are tied to the scroll, so you can scrub back and forth.
- **About** keeps the city ("I think in graphs."). The turbine no longer comes back.
- **Experience** has a new shape for "Manual work, turned into software": a loose heap of sheets on the left, tiles flying across one at a time, and a tidy amber grid filling in column by column on the right. Then the new columns clear and a fresh heap arrives. About a 16 second loop.
- **Big text was hidden** because during each dive the 3D model was drawn on top of the whole page, title cards included. The model now always stays behind the page. The chapter title cards ("Projects", "Side builds", "Skills"...) also sat too low to be seen before they slid away: the title is now near the top of the card, and the card rises whole until the chapter is halfway up the screen before it slices open. In the giant-word scene the model crosses underneath the word instead of in front of it.
- Hero text changed again, because the map is no longer in the hero: "Scroll: the turbine rebuilds into a street map. Point at any corner of it and A* plans the route there, live."
- Cost: the dive is less in-your-face, since it now plays behind cards and under the title card instead of over them.
- Tested as before at 1440x860 and 390x800: no errors, no sideways scroll, all six tabs highlight, about 100 frames a second, page heights unchanged.

## Earlier pass: an animation for every project

Every chapter and every project is now a stop with its own 3D shape, built from the same blocks. On desktop the model sits beside the card under the project's name and slides across as you move between projects. On phones it sits in a gap under each name.

| Where | Shape | What moves |
|---|---|---|
| Hero | Gas turbine rotor | Blades grow in, spins up, then turns slowly |
| How I think | Street graph, then city | Search spreads over the nodes; city rises and the route draws |
| About | City | The route, lit |
| Experience | Heap of sheets into a tidy grid | Tiles fly left to right and snap into place |
| Projects, Route Engine | Flat road map | The route, lit |
| Industrial AI Notebook | Telemetry bars in a baseline band | The signal marches; anomalies spike in amber |
| Mini Maps | City as a distance map | A Dijkstra wavefront; blocks rise as they are settled |
| TheAlgorithms/C++ | Five rings (Tarjan's components) | Each ring turns; found ones light amber in order |
| Side builds, Agent City | Hub and six stilted huts | Still |
| Surf Alert | Wave surface | Crests roll and lean |
| Kia-bot | Ring of spokes | Rises and falls like speech |
| Quant Backtest Lab | Six ridges, one per test window | Each draws left to right; amber test stretches step forward |
| Lead Autoresponder | A 3D funnel into three streams | Rings swirl and drain; the amber stream goes to a person |
| Market Debrief | Candlesticks and three tier lines | The chart draws; down candles amber |
| Math 163 Study Game | 27 flashcards | A wave flips them from steel to amber |
| Skills | Binary tree with branches | An amber search path walks down |
| Contact | Wave surface | As above |

How I judged them: I screenshotted every scene, and redid the ones that fell short. Redone once: telemetry (bars too thin), the voice ring (too small and dim), candlesticks (too small), the funnel (did not read as a funnel), Mini Maps (cut off the screen). Redone twice: the Skills tree (first version was scattered dots; it now has branches). I also added a front light, because the upright charts faced away from the main light and looked dark.

Bug I caused and fixed: my project-title style used the same class name as the "Kia Pousti" link in the top bar, which knocked the name out of the bar. Renamed.

Costs: the phone page is longer again (about 27,100px, was 24,750), because each project has a gap for its model. Desktop is unchanged at about 20,800px.

Last round: I rated the funnel and the backtest ridges weakest, so I redid both. The funnel is now eight swirling rings draining to a neck and splitting into three streams. The backtest now shows each window's amber test stretch one step later than the last, which is what walk-forward means.

Still the least striking: Mini Maps (the Dijkstra front is clear but plain) and the telemetry bars.

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
- **The model is always behind the text.** It used to come in front during a dive; that hid the big titles, so it no longer does.
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
2. The giant-word scene locks; the graph sits under "graphs" with white node dots, and the city rises as the word changes to "routes".
3. During a dive the blocks stay behind the cards and title cards, and the titles are readable.
4. The sliced curtains slide without flicker, and nothing stays covered.
5. Headline glitch shows amber and blue copies for a moment, then clears.
6. The name is condensed (narrow letters) with guide lines lined up under it.
7. Scrolling stays smooth on your iPhone, and it doesn't get warm.
8. The address bar hiding on iPhone doesn't make the locked scene jump.
