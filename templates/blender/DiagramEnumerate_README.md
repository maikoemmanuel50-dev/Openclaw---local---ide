# DiagramEnumerate — 3-Card Stagger Rig

Reusable Blender template for TED-Ed style enumeration sequences.

## File
`templates/blender/DiagramEnumerate.blend` (extract from Scene 03 after render)

## Structure
- Collection: `TEDed_Overlay`
- 3 text objects with staggered scale keyframes (fade_in_out preset)
- Default stagger delay: 12 frames (0.5s @ 24fps)

## Parameters to Customize per Episode

| Parameter | Ep01 Value | Ep02 (Lagos) Example |
|-----------|-----------|---------------------|
| Card 1 label | iHub 2010 | CcHub 2011 |
| Card 2 label | Andela | Paystack |
| Card 3 label | NaiLab | Flutterwave |
| Stagger frames | 240, 540, 720 | Adjust to VO |
| Color | `#4CAF50` | City accent |

## Usage
1. Append `TEDed_Overlay` collection from template into new scene
2. Edit text object bodies
3. Retime keyframes to VO word timestamps
4. See `setup_teded_elements.py` for automation reference
