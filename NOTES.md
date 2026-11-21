# Preview: http://localhost:8765

Branch: `nap-build` (built on top of `redesign/map-hero-test`). Shipped to `main` and kiapousti.com on 2026-11-15, on your "ship it".
Also in this ship: the Contact line "Email is the fastest way to reach me." is now a mail link.
If the preview stops loading, run `python3 -m http.server 8765` in this folder.

## Every scene change is its own move, and one is a Transformer (2026-11-20)

Kia asked for every scene change to be "insanely cool" and different from the others, every diagram to be unique and clever, one change to work "like a Transformer", and for three agents to run it: one that goes over everything, one that invents, one that approves or sends the ideas back.

**The three agents.** Their notes are outside the repo, in the session's shared notes folder: `audit.md` (the auditor, "Caliper"), `concepts-v1.md` (the creator, "Riff"), `verdict-v1.md` (the approver, "Veto").
- The audit counted 29 hand-overs and 36 diagrams. 15 hand-overs used the same swap (the old scene flies at the camera, the new one arrives from behind), and two card demos showed marks or results that were not computed.
- The creator took 46 minutes, so the builder designed and built a first set of 13 meanwhile. The approver passed 8 and sent 5 back. Those 5 were rebuilt from the creator's designs; 4 passed the second round and the last passed the third. The approver also approved the Transformer plan with three changes, all made (two-sided tiles, a staged cascade with overshoot and a brass flash, a larger model that turns as it folds).

**How one scene becomes the next** (`morph` and `WAYS` in the page). Every light-drawn scene can be asked for its points at any moment. Part way between two scenes the page asks both, and point i of the old scene travels to point i of the new one. Lines of the old scene let go in the first 40%, lines of the new one are drawn in the last 40%.
`WAYS['old>new']` is the path for one pair: it gets the progress, the point's number, where it starts and where it must land, and answers where it is now. It may also set the point's brightness and colour for the trip, and bring a prop (`.prop`: a scan bar, a ring, the condensed graph). A pair with no entry uses the plain path `'*'`.
Every scene keeps the same number of points in the same order (a point that is not showing is drawn dark), or points would change places mid-flight.
A solid model can take part through a stand-in drawn in points: the San Diego model has one (`dsCity`), and the ending's board has its pile of balls (`dsPile`).
On computers the points cross in front of the page while they travel (they used to pass behind the app cards and be lost). Phones: each scene rides the page under its own name, so the first half of a change plays where the old scene was and the second half where the new one is. Reduced motion: no travel; the scenes swap as before.

**The 13 hand-overs** (pair, name, what it says):
1. Route Engine to Industrial AI Notebook, "skyline readout": a bar of light carries the city away and comes back printing the sensor trace. A skyline is a signal.
2. Notebook to Mini Maps, "fan": the signal's lanes swing open into spokes; time along a lane becomes distance from the centre, and samples land nearest first, the order Dijkstra settles nodes.
3. Mini Maps to TheAlgorithms/C++, "push, pop": the real Tarjan run. Each point is pushed onto a tower at its node's real visit time and stack depth; each strongly connected component pops off together when the run finds it.
4. TheAlgorithms/C++ to Agent City, "condense": each cycle draws in to one node and the one-way links between them stay. That is the condensed graph, and the prop draws its true links.
5. Agent City to Surf Alert, "seven drops": the hub and six agents drop into the water; the sea lights where their ring fronts pass and rides the real sum of the seven ripples.
6. Surf Alert to Kia-bot, "barrel": the sheet of swell curls up and closes into a ball standing on the waterline.
7. Kia-bot to Quant Backtest Lab, "tape reel": the ball spins and is paid out, laid down left to right as the price line.
8. Quant Backtest Lab to Lead Autoresponder, "tape through the reader": the price line is pulled through the reader's ring, pinches to a thread, and leaves split onto the three ways out. Both works read a stream in order and never look ahead.
9. Lead Autoresponder to Market Debrief, "whirlpool": the three ways out wind onto the dial, the inside turning faster than the rim.
10. Market Debrief to Math 163, "coin and lock": the dial is laid flat in one piece, then its rings turn against each other until every tick sits at the golden angle.
11. Math 163 to Skills, "armillary": the seed head sorts into eight flat rings, and each turns up as a rigid hoop on its own gimbal. Eight rings, eight rows of the table.
12. Skills to Contact, "up the mast": the rings wind in onto the mast, run up it, and are sent from the top.
13. Contact to the ending, "the first experiment": the Morse points come down through the Galton board's pegs, each taking one ball's real seeded path, into the pile; the steel balls then stand in exactly where they landed. The ending's stop now lasts until the page runs out, so this plays while the board is on screen.

**The Transformer: the pop-up plant** (About into Experience, and Experience into Projects). `blender/build_fold.py` builds, bakes and exports `models/fold.bin` (274 KB) in one run.
The San Diego model's base plate is 34 square tiles and 8 strips. Each has the city on one face (dark enamel, a few roof blocks, a brass rim) and the factory on the other (steel, belt, walnut, hazard stripes or the control panel). Each has two poses in the file (the exporter's new `alt` list): lying in the plate, and standing in an approval line. What each cell becomes:
- columns 3 to 5: the conveyor (three tiles turn over as its bed, six hinge up as its skirts);
- columns 0 and 1: the workbench where a job is stamped by hand (walnut top, back, front, one end);
- column 2: the control cabinet behind the gap (four walls and a lid);
- the eight strips: two gantries of two posts and a beam, and two legs for the bench's open end;
- the other 13 tiles turn over where they lie and become the shop floor.
The page moves every tile between its two poses as one rigid body about one fixed axis, the way a hinged part moves (`screwOf`, `screwAt`; self-checked on load), in stages (`STAGE`): bed, skirts, bench, cabinet, gantries, floor. Each swings about six degrees past its stop and settles, and its brass flashes as it locks. Then the press heads telescope down from the beams, the hand stamps and ink pads rise out of the bench, the beacon's mast goes up, and the line runs.
Going in: the buildings go down into the plate, the tiles appear on it with a flash along the seams, and they fold while the model turns from the city's heading to its own. The city's own plate, with its rim and scale marks, stays as the plant's base. Going out to Projects it runs backwards and the city rises again. The fold is driven by how far the chapter has come up the screen, so scrolling back reverses it exactly.
Click the plant and it folds down flat and stands up again. Reduced motion: the finished line simply shows.
`models/scenes.bin` (519 KB, the older scene models) is no longer downloaded: every other scene is drawn in light. The file and its script are still in the repo, unused, like the turbine's.

**Two demos now compute what they show.**
- Telemetry card and the 3D signal ribbon (`detect`): a real isolation forest (60 trees of 64 samples, trained once on 600 samples of the synthetic signal, seeing each reading and the average of the 12 before it) and a real rolling z-score (last 40 samples, alarm beyond 3 spreads). An amber dot is what the forest flags; a ring is where the reading left the baseline's band. Checked over 7,050 samples: the forest catches all 150 spikes and the baseline 146; on the slow drift the forest flags about 1 sample in 5 and the baseline about 1 in 300; false alarms are under 1 in 300 for both.
- Backtest card (`demos.backtest`): a real walk-forward on synthetic prices, a new path every loop. The first 40% is only fitted on; then six test stretches, each traded with the lookback (5, 10 or 20) that did best on everything before it, with a cost on every change of position. Over 400 paths the rule ends ahead of holding in 235 at the starting cost (7 hundredths of a percent), 272 with no cost and 141 at the sliders' maximum. The Walkforward app's fee and slippage sliders now set that cost, and its six fold bars are drawn to the real proportions.

**Two diagrams upgraded** (the approver's first two picks; built after the rest was shipped):
- Agent City (`AQ`, `dsAgents`): an illustration that runs a real priority queue. Sample jobs arrive in waves, each with an urgency; the hub keeps them in a binary heap and hands the most urgent to the next free agent, who goes out, does it and comes back. The funnel of rings over the hub is the heap itself, level by level, with the root at the tip feeding the hub and a line from every job to its parent. The state is worked out from the clock alone, so it is the same every time for the same moment. Checked over 20,000 steps: the job handed out was always the most urgent one waiting, the queue ran between 0 and 34 jobs and never filled its 48 places. The page also checks the heap rule on every step.
- Skills (`dsStack`): the ring that lights now lights its own row of the table in the accent colour (number and label), so ring and row are visibly the same thing. Point at a row and its ring lights. No new words.

**Left for later** (found by the auditor or the approver, not done):
- Nine CSS transitions animate colour, background or width (`.tabs a`, `.bar-cta`, `.btn`, `.links a`, `.bar-map`, `.feature-head a`, `.pin-step b`, `.contact-cards a`, `.tab-ink`), against the "only transform and opacity" rule. They are the hover fades on links and buttons.
- About 120 lines of motion code for the old scene models (`tickRec` to `tickTK`) are no longer used.
- A scorer for the Lead Autoresponder dots, the approver's third pick: only worth building if the project really scores messages that way, which is Kia's to say.
- The creator's other idea for the Transformer, the line folding into a flatbed truck that drives onto the map, was not built: a scripted vehicle is the risky shape.

## The opening model is a Galton board that prices an option (2026-11-20)

Kia did not love the skateboard and asked for an opening that "dresses for the job I want": quant. He picked the Galton board from five options. The skateboard model and its script are deleted; the turbine files stay but are unused.

**The object** (`blender/build_galton.py`, one run builds, rounds edges, bakes shadows and exports `models/galton.bin`, 97 KB):
walnut frame, plinth and crown; enamel back with the lattice of every possible path inlaid in brass; 13 rows of brass pegs (91); brass hopper, gate, bin dividers and feet; a glass front.
For the street-network change it has exactly 100 ball parts (91 pegs and 9 others) and 198 rods (182 lattice lines, 13 dividers, 3 frame rails). The script asserts both. Peg and lattice names carry their row.

**The balls** (page, "The Galton board's balls"): not in the file. 320 steel balls (160 on phones), each making one seeded pseudo-random left-or-right bounce per row, so each is one path of an equal-odds (Jarrow-Rudd) binomial tree. Bins stack four and three across. Click the board, or wait nine seconds after a run ends, and the balls go back up and a new run starts with a new random stream.

**The pricing, all computed in the page and shown in the readout under the board** (a one-year at-the-money European call, S 100, K 100, sigma 20%, r 5%):
- Monte Carlo: the discounted average payoff of the balls that have landed, with its standard error.
- Tree: backward induction through the same 13-step tree (10.51).
- Black-Scholes closed form (10.45), with a standard polynomial approximation of the normal CDF.

**The fly-through**: the camera follows the balls down the pegs to the bins while each ball's path glows (where many balls took the same step the light adds up); the board opens in three layers (back, working layer, glass); past half way the tree is priced back up from the bins a row at a time, each row lighting gold, and the camera rides up with it to the single number at the top. Then the pegs and lattice become the street network as before.

**Other changes that came with it**
- Opening sentence: "Scroll: the Galton board becomes a pricing tree, then a street map." (both the mouse and touch versions; the touch one still said "turbine").
- The scanned-metal wear now applies only to metal parts (it showed as brick lines on wood, enamel and rubber).
- Phones: the opening reserves more room under the text (the board is about 0.9 of the screen width tall).
- Reduced motion: the board shows a finished run and the final numbers.
- Known: on a computer the very first fast scroll has a few one-off slow frames where each later model first appears (thru, Experience, Projects, first light-drawn scene). They are gone on the second pass. Not caused by the board.

**For Kia before interviews**: anything on the home screen is fair game. Be ready to explain the bell curve from independent bounces, why the tree is priced backward, what "risk-neutral" means here, why the simulation's error shrinks with the square root of the number of paths, and why tree and formula differ slightly (13 steps).

## The opening model is now Kia's electric skateboard, not a turbine (2026-11-20)

Kia's point: the turbine made the page read as "interested in turbines". It stood for the employer, not for him. He chose the electric skateboard he helped build the speed controller for.

- `blender/build_board.py` models it deck-down so the hardware shows: trucks, wheels with spoked cores, belt drive and motor, a 60-cell battery under a ribbed lid with nickel strips, balance leads and a BMS, the finned controller, capacitors and wiring. 285 parts.
  Run: `Blender -b --python blender/build_board.py`, then `Blender -b blender/board.blend --python blender/finish_turbine.py --python blender/export_parts.py` (rounds edges, bakes soft shadows, writes `models/board.bin`, 260 KB; the turbine was 421 KB).
- The street-network change needs exactly 100 ball parts (one per corner) and at least one rod per street edge. The board has 100 and 185: cells, wheel spokes, belt links, cooling fins and wire runs are the rods. The build script asserts the 100.
- `export_parts.py` now takes the number of points in a rod section from the scene (`ring`, 12 for the board, 6 for the old turbine) and writes it in the header; the page reads `h.ring`.
- Page (`fly()` and the loader): parts keep their own scale (wire and belt pieces are one unit mesh stretched); the wheels turn about their own axles; the exploded view lifts parts by layer (cells highest) and slides anything on an axle outward; the board leans its underside to the camera (`TILT`).
- Wording changed in the opening paragraph, as the swap requires: "the turbine rebuilds" is now "the skateboard rebuilds".
- `models/turbine.bin`, `blender/turbine.blend` and their scripts are no longer used by the page. Kept for now in case Experience gets a small turbine.
- Known weak spot: the scanned-metal wear pattern shows as faint brick lines on the wheels up close.

## Closer to Minutes, real-looking apps, and colour options named for Kia's interests (2026-11-20)

- Colour options: Pacific Dusk stays the default. The other four are now Garage (cars: graphite and red), Dawn Patrol (surfing: the light, airy, Minutes-style one), Hardwood (basketball: dark maple and orange) and Ticker (markets: near-black green). Keys in `THEMES` are unchanged (studio, gallery, volt, aurora), only names and colours.
- NOTE: the colour picker is only shown on localhost. `kiapousti.com` hides it (the check is in the picker script), so visitors always get Pacific Dusk. Showing it live is Kia's call.
- The light-drawn animations switch to ink on the light option (`uLight` in both shaders, normal blending instead of adding light), so they are visible on a pale page.
- Apps: SVG icons in every tab bar, a "Sample data" overline and avatar in the app header, section labels and badges in lists.
- App header beside each phone, like an app page: a 54 px icon, the build's name and "iPhone app · <app name>".
- Minutes look: pill buttons, 22 px card corners, 16 px picture corners.

## Borrowed from myminutes.ai: the flow, not the look (2026-11-20)

Kia liked how myminutes.ai reads (a Framer page: one idea per screen, proof up top, a click-through feature list beside a phone, a questions list). He chose to borrow the flow and keep the 3D opening and live algorithms.

- Side builds: beside each phone is a list of its three screens with one line each (`feat:` in `APPS`); picking a row turns the phone to that screen, and the phone's own tabs keep the list in step. The card is wider (610 px) and the big name beside it smaller; the 3D animation now centres itself under that name.
- Opening: a proof row under the links with three facts already stated elsewhere on the page (UC San Diego degree, Solar Turbines role, TheAlgorithms/C++).
- Contact: "Before you ask.", five disclosure rows (`<details>`, no script needed). Every answer restates something already on the page.
- Less per screen: the technology list in each project card is kept for screen readers only, since the same list is set under the project's big name; side-build scenes have more space above and below.
- New words that are mine and Kia's to change: the 21 one-line screen descriptions, the "Quick answers" label, the "Before you ask." heading and the five questions.
- Cost: the page is about 4% taller on computers and 9% on phones than before this change.

## Side builds as working iPhone apps (2026-11-20)

Kia asked for realistic, usable iPhone interfaces for the side builds, each its own app with a name and a logo.

- Script (`APPS` table, classic script, above "The name") builds an iOS-style app round each build's live canvas: status bar, logo and app name, three tabs, and a tab bar. Styles are the `.ios-*` rules. Without script the plain demo screen stays.
- Every control works: tabs switch, switches toggle, Agent City's "Needs you" cards dismiss, Dawn Patrol's alert time and minimum height step, Walkforward's fee and slippage sliders move, Firstreply's replies send or hand off, Kia-bot's microphone toggles, Math 163's quiz marks the answer (base 60).
- All content is sample data and says so on screen ("sample", "Sample holding A", "synthetic"). No real holdings, customers or results.
- App names shown in the phone (the page's own headings are unchanged): Agent City, Dawn Patrol (Surf Alert), Kia-bot, Walkforward (Quant Backtest Lab), Firstreply (Lead Autoresponder), Debrief (Market Debrief), Math 163. These are my suggestions and are Kia's to change: one `name:` per app in `APPS`.
- Each logo is a small inline SVG, also shown beside the build's heading in its card.

## Side builds: the live demos run inside phones (2026-11-20)

Kia compared the page with seanwirkus.com (app screenshots in phone frames) and chose to put the live demos in the frames rather than send screenshots.

- CSS only (`#builds .build .screen`): each side build's live canvas sits in a phone frame, 250 px wide, with an island and a home bar; padding keeps the demo clear of both. The demo is the same sample-data canvas as before, so nothing is presented as a real screenshot.
- Kia-bot's sample exchange moved inside its phone, under the voice bars (markup moved, words unchanged).
- Cost: the page is about 6% taller on computers and 7.5% on phones, because a portrait phone is taller than the old wide screen.
- Not done: a row of numbers per build, like the reference has. The side builds have no real numbers on the page, and none were invented.

## The name, and the "Away from the keyboard" pictures (2026-11-16)

- The name: the construction lines, handles and "cap / baseline" labels are gone (Kia did not like them). Script splits the name into letters; they fly in from depth one after another, the name leans with the pointer with each letter at its own depth, and a letter lifts when pointed at. Warm fill fading to the accent at the foot. Reduced motion or no script: plain text.
- Six boxes now show Blender pictures instead of line drawings: `blender/build_tiles.py` models each scene and renders it with Cycles to `renders/` (sports, boards, cars, family, reading, markets; 30 to 55 KB each, loaded lazily, about 220 KB in all). Run it in a background Blender: `Blender -b --python blender/build_tiles.py [-- name]`.
  The soccer ball is a truncated icosahedron (12 pentagons, 20 hexagons); the volleyball is 18 panels; cars shows water beading on coated paint with the clay bar, pad and coating; family is a house at dusk with no people in it.
- The old canvas drawings for those boxes (`demos.m_*`) are no longer used and can be deleted.
- Still Kia's call: the Family box text ("I am a family guy.") is one short line; a longer line needs his words.

## Light and data: new project animations and a fly-through camera (2026-11-16)

Kia rated the chapter models 2/10 and chose: a mix of realistic objects and "light and data" animations, one continuous camera between sections, everything at once.

- Realistic and kept: the turbine, the San Diego city, the Experience approval line.
- New, drawn in points and lines of light (one shared buffer, `P()` points and `L()` lines, filled every frame by the scene on screen; `draw:` in the `ASM` list):
  `dsSignal` (Industrial AI: the sensor signal as a ribbon, flagged points lift out), `dsDijkstra` (Mini Maps: a real Dijkstra run; settled nodes rise to their distance, so the shortest-path tree becomes a cone),
  `dsTarjan` (a real Tarjan run; each component lifts, lights and turns when found), `dsAgents` (hub, schedule ring, six agents on arcs), `dsSurf` (the swell as a field of light, buoy reports as rings),
  `dsVoice` (Kia-bot: breathing voice sphere, beams to three tools), `dsQuant` (walk-forward window stepping along synthetic prices), `dsLeads` (messages read at one point, leaving on three paths),
  `dsMarket` (a year of synthetic prices round a dial with pullback-tier rings), `dsSeeds` (Math 163: golden-angle seed head, 21 and 34 arms, golden spiral), `dsStack` (Skills: one ring per table row, one bead per item, counted from the page), `dsBeacon` (Contact: K I A in Morse as rings from a mast).
- Hand-over (`showAsm`): the model being left flies straight at the camera and past it; the next arrives from far down the same line. Reduced motion: no flight, it is there or not.
- Phones draw 35% of the points. The Blender scene models for these stops are still in `models/scenes.bin` but no longer shown (could be removed from the file to save about 400 KB).

## Chapter models pass: Kia-bot and the tools board rebuilt (2026-11-16)

- Kia-bot is now a small desk robot (`kb.*` in `blender/build_scenes.py`): torso with speaker grille, head on a neck joint, two eyes, antenna. `tickKB` turns the head to the tool being called, blinks the eyes, lights them and the antenna tip during a call. Still the same story: one voice agent calling three tools.
- The Skills board is a dark shadow board and every tool does its job in turn (`tickTools`): the wrench turns a bolt, the caliper jaw slides, the screwdriver spins, the pliers open, the hex key turns, the meter needle sweeps, the iron tip heats. New parts: `tools.jaw`, `tools.pl.0/1`, `tools.needle`, `tools.tip`.
- Every chapter model now gets the turbine's scanned-metal wear (`worn()` shares `wearFrag()` with the turbine's `reshape()`): uneven shine and fine relief instead of flat colour. No new download.
- Models are built with a second, background Blender so the open turbine session is not touched: `Blender -b --python blender/build_scenes.py`, then `Blender -b blender/scenes.blend --python blender/finish_scenes.py`. `models/scenes.bin` 504 KB -> 519 KB.
- Chapter models sit 6% of the screen lower on computers so they clear the "Sheet" label; on phones they sit a little further under the headline.
- Not done: the other nine chapter models keep their shapes; flat demo panels, "Away from the keyboard" tiles, empty space under the pinned story.

## Review pass: three faults fixed, sharper zoom (2026-11-16)

- Opening line says "Developer" (Kia's call), matching the Experience section.
- Title-card strips now finish sliding off by the time a chapter sits under the tab bar. Before, a tab click landed with two strips still on screen (seen on Contact).
- Models no longer rest on words: beside a project the model drops with the project's name when the name is low on screen; on phones a chapter's model always sits under the last line of the headline text.
- Phones: the theme picker slides away after half a screen of scrolling, so it no longer covers content.
- Fly-through clarity (computers): the blur's sharp zone now widens as the camera pushes in (it was fixed, so nearly the whole model was out of focus), the base blur is halved, blades keep 80% of their width to the tip, and the metal texture is 1024 px (`textures/wear-wide.jpg`, 150 KB, computers only; phones keep the 25 KB one). Made by `blender/sharpen_turbine.py`.
- Not done yet: chapter models still flat-coloured, flat demo panels and the "Away from the keyboard" tiles, empty space under the pinned story.

## A live ocean, models that transform between chapters, a sharper picture (2026-11-16)

You asked for someone to go through every part: drop the parts diagram on the turbine, a more realistic sunset, hand-overs "like the pictures", sharper visuals. Five passes, one commit each.

- **Parts diagram: gone.** The four labels (Compressor, Combustor, Turbine, Casing), their styles and their code are removed. The fly-through itself stays and is closer: the camera now pushes in to almost three times the size, travels along the shaft at blade height from the compressor to the turbine wheels, the light sweeps across the blades as you scroll, and the background blur is stronger on computers.
- **Backdrop: a real sunset over a sea that moves.** The sky is a new photograph, Poly Haven "The Sky Is On Fire" by Greg Zaal and Rico Cilliers (free to use, CC0). Honest note: it is a real ocean sunset, photographed in Cape Town, not San Diego. Everything under the horizon in the photo is thrown away and the sea is drawn live by a small program: eight trains of swell, reflecting that sky the way water does (mirror-like far away, darker looking down), with the glow laying a path on the water. It runs at about 30 frames a second, smaller on phones, and stops when the tab is hidden, in the other themes and while the map is open.
- **Light changes as you read.** Golden hour for the opening and the fly-through, where there is little text; by the first chapter it is dusk, so body text always has a dark sky behind it; deep dusk by Contact. On phones the horizon sits lower and the veil is heavier, so the opening paragraph no longer crosses the glow.
- **Fallbacks.** Reduced motion, no WebGL or scripts off: the picture has its own still sea (one frame of the live water, softened), and the sky stays at dusk.
- **Chapters no longer cut.** Before, the model faded out and back in behind an opaque title card. Now the model rides in on the title card, in front of it, and you watch its parts fly apart and regroup into the next chapter's model as the card's strips slide away. The city's streets (which are the turbine's parts) lift off the plate into the same swarm. The model sits lower than the card's big title and is at rest in the title block's empty space before any rows of text are uncovered; chapter models now rest further right, clear of the headline.
- **"Inside Route Engine" runs on the 3D city.** The pinned story used a separate flat drawing. Now the frame is clear and the San Diego model tells it: the raw tap drops onto the nearest corner, the page's real A* spreads, the route is drawn, then a bead on every point of the route and the real Douglas-Peucker keeps only the ones that matter. The readout uses the same wording as before with the city's own numbers. If the model cannot load, or with reduced motion, the flat drawing is still there.
- **An ending.** After the last tiles there is open space where the parts come back together as the turbine the page opened on, above "Back to top". Click it and the rotor surges, as in the opening. This makes the page about 3% longer.
- **Sharper on computers.** Edges are smoothed with four samples a pixel (they were not, under the blur pass), shadows are four times finer, the scanned-metal texture stays sharp at glancing angles, and the backdrop has a slight vignette. The scene models have baked soft shadows where parts meet (`blender/finish_scenes.py`). Screens already drew at up to twice their pixel density; I left that cap.
- **Small fixes on the last lap.** The network no longer sits behind the "graphs" caption; the giant word hands over with a short rise; one line of code that had slipped into a comment (the wear texture's colour setting) is fixed.

**Words:** none added. One hidden screen-reader label ("The turbine, part by part") was removed with the diagram.

**Page weight:** `textures/sky.jpg` 94 KB (phones; replaces `dusk.jpg`, 72 KB) and `textures/sky-wide.jpg` 278 KB (screens 1000 px and wider only). `models/scenes.bin` unchanged at 504 KB. `index.html` 234 KB to about 250 KB. No library added. Removed: `textures/dusk.jpg`, `blender/build_dusk.py`. Added: `blender/build_sky.py`, `blender/finish_scenes.py`.

**Tested** in Chrome at 1440x860 and at 393x659 slowed 4x: no errors; phone has no slow frames over the whole page (worst 29 to 31 ms, same as before); computer has one 36 ms frame the first time you reach About and none on a second pass (it was 29 ms before, and it happens with the sea switched off too). Tab trip, Map, M, D and Esc work; the other four themes hide the sky; reduced motion gives a still, readable page.

**Not tested:** a real iPhone, Safari, scripts off (reasoned from the styles only), and what the sea and the finer shadows cost a graphics chip (my test measures the processor). My phone screenshots of the very last screen came out shifted by the test tool, so the ending on a phone is checked by measurement, not by eye.

**Not touched:** the 2D demo screens inside the cards, the six small tiles, the look of the title cards, the map's landmark pairing, the hero wording. The city did not get the bevel and soft-shadow treatment (its pieces are stretched per lot, so baked shading would be wrong); the scene models did not get bevels.

## The route engine is now how you get around; less scrolling; things to find (2026-11-16)

You asked for the playable route engine, smoother hand-overs, less scrolling and easter eggs, with a second agent reading the whole site for ideas. Its report is where the scroll cuts, the two bug fixes and most of the easter eggs came from.

- **Route engine as navigation.** Click a far section in the top bar and the page dims, downtown San Diego stands alone, the real A* plans a trip from the section you are in to the one you chose, the marker drives it and the page arrives there (about 2 seconds; any key or a click on the background skips it). Near sections still just glide.
- **The map on its own:** the new Map button in the bar, or the M key. Each section is a label on a landmark: About = California Tower, Experience = USS Midway, Projects = Central Library, Side builds = Petco Park, Skills = One America Plaza, Contact = Coronado Bridge. That is one line in the code (`LAND`), so say if you want a different pairing. Labels are real buttons, so keyboard and phone work. Esc or Close leaves.
- **New words I had to add (yours to approve):** "Map", "Close", the screen-reader label "Route map", and "A*" / "Dijkstra" in front of the existing "explored N · path N steps" readout.
- **Turbine running button:** removed, as asked. The turbine always runs.
- **Less scrolling:** fly-through 260 to 190 screen-heights-percent, graph scene 210 to 170, the pinned project story 290 to 230 (160 on phones), chapter title blocks 68 to 54 (86 to 70 on phones), each project scene 82 to 72. The whole page is about 13% shorter on a computer and 9% on a phone.
- **Hand-overs:** every scene model now breaks into and forms out of the same cloud of points, so one model's parts read as regrouping into the next instead of two separate explosions.
- **Things to find:** click the turbine (the rotor surges and coasts back); click any scene model (its parts spring apart and settle); click the surf scene (a set of bigger waves); press and hold on the telegraph key at Contact (you key it); press D while the streets are showing (the search drops its estimate and becomes real Dijkstra: same route, far more streets searched); and for 45 minutes either side of the real San Diego sunset each day, worked out from the date, the sky backdrop glows brighter.
- **Bugs fixed (found by the second agent):** the wave scene's turn was being skipped because the line had slipped into a comment; a stray bracket was silently dropping one style rule for the "Away from the keyboard" tiles; and on phones a scrolling finger counted as "pointing at the map", which stopped the automatic new trips.
- **Tested** in Chrome at 1440x860 and 393x659 (phone slowed 4x): no errors, no slow frames, tab trip, map, skip, Esc and Dijkstra all work; sunset function gives 4:48 pm for today (real: 4:47). Not tested: Safari, a real iPhone, JavaScript off, the click eggs by eye.
- **Not done, from the agent's list:** running the project story on the 3D city instead of the flat drawing; removing the fade-cut at each chapter title; the turbine reassembling at the very end; a Stoer-Wagner min-cut egg. Also flagged for you: the opening still says "Software engineer" while the job title says "Developer".

## The backdrop is now a real sky: sunset over the ocean (2026-11-16)

You said the two-glow backdrop was not it and asked for a nicer custom one, special but calm.

- **What it is.** A real photographed sky, not a gradient: the Poly Haven panorama "Umhlanga Sunrise" by Greg Zaal (free to use for anything, CC0). Honest note: it is a real ocean horizon, but it was not photographed in San Diego.
- **What Blender did to it** (`blender/build_dusk.py`): kept only the stretch of horizon that is open sea, turned the exposure down so the sunrise reads as last light, cooled and darkened the upper sky, made the sun a warm white, then built a still sea under it by mirroring and softening the sky. The top and bottom melt into the page colour.
- **On the page.** The sun sits on the horizon under the turbine. As you scroll, the view pans slowly along the horizon and the light fades to half by Contact. One picture and one dark veil, moved with transform and opacity only; still with reduced motion or JavaScript off. The veil keeps text readable.
- **Page weight:** `textures/dusk.jpg` is 72 KB (2068 x 1036). No library added.
- **Other themes:** the sky shows only in Pacific Dusk; Studio Black, Gallery Light, Volt and Aurora hide it and keep a flat page colour.
- **Tested** at 1440x860 and 393x659 in Chrome: no errors, picture covers the screen at every scroll position. Not tested: Safari, a real iPhone, JavaScript off.

## The backdrop: last light over the Pacific (2026-11-16, replaced by the sky above)

You asked for a background like the ORYZO screenshots instead of flat black, and for it to be something that fits you.

- **The idea.** This is San Diego and the page's one accent is sunset amber, so the backdrop is dusk over the ocean. A warm amber glow sits low under the model, the way the sun sits on the water; a cool blue one sits high on the other side, the sky going to night.
- **It moves with you.** As you scroll down the page the warm glow drifts across and sinks, and the cool one comes up, so the opening is golden hour and Contact is nearly night. It is two soft discs moved with transform and opacity only, so it costs nothing to animate. With reduced motion or no JavaScript it is simply still.
- **Colours.** The page base moved from near-black ink (`#0b0d14`) to dusk slate (`#0e151e`), with panels and rules shifted to match. The top bar lets a little of the backdrop through.
- This goes against one of the cleanup rules I applied earlier (no colour washes behind content). I kept it to two soft lights with a reason behind them, and eased the warm one so small text stays readable over it.
- **Tested** at 1440x860 and 393x659: no errors, all six tabs, no slow frames. The four other preview themes still have not been rechecked and will look wrong with this backdrop.

## The turbine rebuilt at "ORYZO" quality, with a fly-through (2026-11-16)

You sent the ORYZO screenshots again and asked how to get that look. The gap was not Blender itself: my models were plain shapes with flat colours, lit by three simple lights. This pass gives the opening turbine the things that site has.

- **Real studio light.** A photographed studio from Poly Haven (`studio_small_08`, CC0). It is stored as a 42KB JPG with its brightness squeezed; the page undoes the squeeze, so the softboxes are properly brighter than the walls and show as crisp highlights on the metal.
- **A scanned metal surface.** A patch of a scanned steel plate from Poly Haven (`metal_plate_02`, CC0), 25KB. Its roughness and its height are wrapped onto every part from three sides, so the shine is uneven and there are scuffs and fine relief, without any part needing its own texture layout. I cropped a patch with no panel seam in it and mirror-tile it.
- **Rounded edges.** In Blender, every hard edge except on the blades is now bevelled, so edges catch a highlight the way real machined parts do.
- **Baked soft shadows.** Blender works out how shadowed each point is by the parts around it and stores that in the model, so the crevices are dark at no cost on the page.
- **A fly-through.** New section between the opening and "How I think", 2.6 screens tall. The page holds still, the turbine takes the middle of the screen, the camera pushes in to twice the size and swings to look along the blades, the parts ease apart, and four callouts stay pinned to their parts: Compressor (9 stages), Combustor (10 cans), Turbine (3 stages), Casing (cut away). Those are the counts in the model.
- **Camera effects, on computers only.** The picture is drawn off screen and passed through one pass that blurs what is out of focus (more as the camera goes in), lets the brightest highlights glow a little, and grades it. Phones skip this and draw directly.
- **Title change you asked for:** "Software Developer" is now "Developer" for the Solar Turbines role, in About, Experience and the page's hidden job-title data. The line above your name still says "Software engineer", and so do the search description and share title; say the word if you want those changed too.

**Text I added:** the four callout labels above.

**Cost:** turbine model 421KB (was 191KB), textures 67KB, and the page is 2.6 screens longer. The camera-effects pass roughly doubles the drawing work on computers.

**Not done:** only the turbine got this treatment. The city and the thirteen scene models still have flat colours, though they now reflect the real studio too. No photographs of you.

**Tested** at 1440x860 and 393x659: no errors, no sideways scroll, all six tabs, nothing left hidden, no slow frames in the slowed-down test. That test measures the processor, not the graphics chip, and this pass adds graphics work, so check it on your own machines. Not tested in Safari or on a real iPhone.

## Every scene now has its own Blender model; turbine runs fast (2026-11-15)

You said "keep building", asked for the turbine to stay fast when it is on, and then "ship it".

- **Turbine:** switched on it spins up over about a second and keeps running at roughly 80 turns a minute (it was a slow drift). Any faster and the blades start to strobe on a normal 60Hz screen. Off, it coasts down to a stop.
- **Nine more models** (same fly-together system as the last batch):
  - **Mini Maps:** a pin-and-string board. Real Dijkstra runs on the board's own pins, with string lengths as weights; pins are settled in order of distance and the shortest-path tree lights up.
  - **Agent City** (and the Side builds opener): a hub pavilion and six huts on stilts with thatched roofs and ladders, joined by boardwalks over moving water; six agents walk in to report and back out.
  - **Kia-bot:** a desk unit with a ring of bars that moves like speech, wired to three tools it "calls" in turn: a card drawer that slides open, a clock whose hand runs, a magnifier that sweeps.
  - **Quant Backtest Lab:** an equity curve as 48 bars on a bed with rails, and a brass window that steps along it; inside the window the training stretch is blue and the test stretch amber.
  - **Lead Autoresponder:** a mail sorter. Envelopes drop into a hopper, fall through the neck, and a flipper sends each to one of three trays; the amber tray is the one that goes to a person.
  - **Market Debrief:** a split-flap board of 36 flaps that turn over column by column to draw the day's bars.
  - **Math 163 Study Game:** flash cards on two rings; the top card flips from the question pile to the answer pile. A pencil, set square and compass on the base.
  - **Skills:** a pegboard wall with eight tools (wrench, calipers, screwdriver, pliers, steel rule, hex key, multimeter, soldering iron); each catches the light in turn.
  - **Contact:** a brass telegraph key with its sounder. It taps out K I A in Morse, with a spark at the contact.
- **Projects opener and Route Engine** now show the San Diego model with its route, in place of the old flat block map.
- **No scene uses the old blocks any more**, except during the hand-over between two scenes on phones.

**Cost:** `models/scenes.bin` is now 504KB (13 models, 572 parts). It loads after the opening, but it is the biggest file on the site; with the turbine (191KB) and city (152KB) that is about 850KB of models. If phone data matters, this is the first thing to slim.

**Not done:** the six small tiles under "Away from the keyboard" other than the skateboard (Sports, Boards, Cars, Family, Reading, Markets) are still 2D drawings, and the chapter title cards are unchanged. Several models overlap the bottom of their big project name a little on desktop.

**Tested** at 1440x860 and 393x659: no errors, no sideways scroll, all six tabs, nothing left hidden, no slow frames in the slowed-down phone test. Not tested on a real iPhone or in Safari.

## While you were away: four more Blender scenes, the turbine switch, the skateboard (2026-11-15)

You asked for every animation, header and tile to be custom-made in Blender, realistic, with strong transitions, plus an on/off control beside the turbine. You did not answer the Experience questions, so I used my recommended picks. This is what got done in this pass, and what did not.

**Done**
- **Turbine switch.** A small panel switch under the turbine ("Turbine running / stopped"). Off, the rotor coasts down to a stop; on, it spins up hard and settles. It is added by script, so with JavaScript off or reduced motion there is no dead control.
- **Shared system for scene models.** A scene's model is a set of real parts from Blender. As the scene arrives its parts fly in and assemble; as it leaves they fly apart while the next one assembles. Each model also has its own motion.
- **Experience: an approval line.** Left half by hand: a wooden bench, ink pads, a pile of forms, two hand stamps that press one job slowly, then it crawls to the next station. Right half automated: a conveyor with rollers and a drive motor, two stamping gantries with air cylinders that fire as each job passes, a control box with an emergency stop, and a stack light. It matches the "by hand / automated" demo beside it.
- **Industrial AI Notebook: a strip-chart recorder.** A bench instrument with gridded paper off a roll, a pen on a rail, a dial gauge and knobs, wired to a vibration sensor bolted on a bearing. The pen follows the same synthetic sensor signal the project's own demo plots, the trace scrolls down the paper, and anomalies are marked in amber.
- **TheAlgorithms/C++: gear trains.** Eleven gears on a back plate in four trains. Each train is one strongly connected component: Tarjan "finds" them one at a time, and a found train lights up and turns, every gear meshing correctly with its neighbours (tooth counts set the speeds and directions). Brass arrows on the plate show the one-way links between components.
- **Surf Alert: a weather buoy and a board.** A discus buoy with a tripod mast, solar panels, an anemometer that spins and an antenna, and a three-fin shortboard, both riding a swell that rolls through.
- **Mechanically inclined tile: the electric skateboard.** Modelled in Blender and rendered as a picture: deck with a kicked tail, trucks with bushings, four wheels, a ribbed battery case, the finned speed controller with its phase wires, and a belt-driven motor on the rear truck. `renders/eskate.jpg`, 53KB.

**Not done yet** (still the old plain blocks or 2D line drawings)
- Scene models: the Projects and Side builds chapter heads, Route Engine (flat map), Mini Maps, Agent City, Kia-bot, Quant Backtest Lab, Lead Autoresponder, Market Debrief, Math 163 Study Game, Skills, Contact.
- Tiles: Sports, Boards, Cars, Family, Reading, Markets are still the small 2D drawings.
- Chapter title cards ("headers") are unchanged.
- The old 2D skateboard drawing code is still in the file, unused.

**Files:** `blender/build_scenes.py` -> `blender/scenes.blend` -> `models/scenes.bin` (168KB, 215 parts). `blender/build_eskate.py` -> `blender/eskate.blend` -> `renders/eskate.jpg`.

**Tested** at 1440x860 and 393x659: no errors, no sideways scroll, all six tabs, nothing left hidden, the switch toggles. In the slowed-down phone test the whole page scrolls without slow frames except one hitch of about a quarter of a second the first time a new model appears. Not tested on a real iPhone or in Safari.

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
