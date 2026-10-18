# Visual style, transport fixtures and CI evidence lessons

### [ERR-20261018-07] Light-value 2D stick figures and moderately simplified backgrounds
- **Symptom:** Images retain the requested stick-figure style but look dark, heavy and cluttered; even bright rooms use strong black outlines and many small background objects.
- **Reproduction Path:** Inspect the eight historical images and saved prompts in the visual-tone audit; compare six genuine Flow recreations under sys/runs/soft-pastel-style-review-20261018. Run pytest sys/tests/test_soft_visual_style.py and the prompt/full-frame/remote suites.
- **Root Cause:** Registry 1.3.0 repeats heavy black contour instructions, muted colors do not imply light values, references encode dark clothes, and scene descriptions encourage exhaustive environments. Renderer vignette adds another dark treatment.
- **Wrong Assumptions:** Stick figures require thick black outlines; shorter prompts or lower saturation alone guarantee simplicity; improving appearance requires photorealism or a fixed room/palette.
- **Resolution & E2E Proof:** Add immutable registry 1.4.0, shared authoring defaults, finer/lighter background linework, light-value colors and optional style references. Preserve full-frame/reference/text contracts and legacy pins. Route the explicit new treatment through hashed remote requests and props to suppress vignette/grain. Six real Flow images with sidecars were downloaded and visually inspected; night remains intentionally darker. Unit tests verify contracts, not user aesthetic acceptance or a real rerendered MP4.
- **Golden Rule:** Keep 2D anonymous stick figures and story-specific settings. Simplify secondary detail, preserve the focal action and use restrained contours/light values. Verify actual provider images; never rewrite historical registries or certify perception from fixtures.

### [ERR-20261018-08] Isolate both Flow transport branches in integration fixtures
- **Symptom:** Legacy prompt-integration fixtures record zero mocked sends and can fall through to a real signed-in Flow browser when no session socket exists.
- **Reproduction Path:** Run test_flow_prompt_integration with the socket transport mocked while the direct fallback is unguarded. The old fixture does not intercept that alternate boundary.
- **Root Cause:** The bridge gained a direct CDP fallback after tests were authored against only the socket sender. A new capability import also sat inside the no-reference branch, leaving attached-reference requests without the symbol.
- **Wrong Assumptions:** Mocking the old sender isolates every provider path, or exercising only the no-reference branch covers reference routing.
- **Resolution & E2E Proof:** Use a private fixture Unix socket and an explicit failing guard on real direct dispatch. Retain the real compiler, adapter, before-send checks and fake response boundary. Move capability imports before all reference branches; verify old/new pins, attached-reference variations, saved replay and tamper refusal in the integration suite.
- **Golden Rule:** Test providers fail closed at every alternate transport boundary. Treat fixture images as contract evidence only, and cover optional-reference branches whenever prompt capabilities change.

### [ERR-20261018-09] Preserve machine-readable CI evidence through gh-axi
- **Symptom:** Station 6 rejects successful GitHub Actions runs as unreadable despite a clean committed tree and green checks.
- **Reproduction Path:** Compare gh-axi api output for the head commit with json.loads: nonempty run arrays are emitted as TOON tables, not JSON. The empty-array case hides the mismatch.
- **Root Cause:** The certification code assumes --full selects JSON; it actually preserves field values while retaining TOON formatting.
- **Wrong Assumptions:** A successful API command or visible green check guarantees machine evidence can be decoded, or only the first passing run needs validation.
- **Resolution & E2E Proof:** Request an explicit jq @base64 envelope, decode strictly, then apply the unchanged all-runs/exact-commit/success validation. Regression coverage preserves pending runs and rejects malformed/TOON envelopes; live API results confirm the envelope works.
- **Golden Rule:** Separate display formatting from the machine evidence protocol. Never weaken CI validation to obtain a certificate.
