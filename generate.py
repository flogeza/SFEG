import os
from datetime import date
from pathlib import Path

import grf

# import lib

# DEBUG_DIR = 'debug'
# os.makedirs(DEBUG_DIR, exist_ok=True)

g = grf.NewGRF(
    grfid=b'TODO',
    name='SFEG',
    description='TODO',
    url='https://github.com/flogeza/SFEG',
)

Train = g.bind(grf.Train)

# g.add(lib.set_global_train_y_offset(2))

# g.add(lib.set_global_train_depot_width_32())

RAIL, ELRL, MONO, MGLV = g.set_railtype_table(['RAIL', 'ELRL', 'MONO', 'MGLV'])


def make_sprites(path):
    OFFSETS = {
        64: [
            (1, 0),
            (-4, -3),
            (0, -5),
            (4, -4),
            (1, 0),
            (-4, -3),
            (0, -5),
            (4, -4),
        ],
        128: [
            (2, 0),
            (-8, -6),
            (0, -10),
            (8, -8),
            (2, 0),
            (-8, -6),
            (0, -10),
            (8, -8),
        ],
        256: [
            (4, 0),
            (-16, -12),
            (0, -20),
            (16, -16),
            (4, 0),
            (-16, -12),
            (0, -20),
            (16, -16),
        ],
    }

    VIEW_FILES = [6, 5, 4, 3, 2, 1, 8, 7]
    ZOOM_CONSTANT = {
        64: grf.ZOOM_4X,
        128: grf.ZOOM_2X,
        256: grf.ZOOM_NORMAL,
    }

    path = Path(path)
    sprites = []
    for view in range(8):
        alt = []
        for zoom in OFFSETS.keys():
            xofs, yofs = OFFSETS[zoom][view]
            file_view = VIEW_FILES[view]
            png = grf.ImageFile(path / f'{zoom}_{file_view:04}.png')
            sprite_zoom = ZOOM_CONSTANT[zoom]
            alt.append(grf.FileSprite(png, 0, 0, 256, 256, xofs=xofs - 128, yofs=yofs - 128, zoom=sprite_zoom))
        sprites.append(grf.AlternativeSprites(*alt))

    return [{
        'name': 'Default',
        'sprites': sprites,
    }]


Train(
    id=1,
    name='V63 "Gigant"',
    length=12,
    liveries=make_sprites('v63sprites_teszt03'),
    engine_class=Train.EngineClass.ELECTRIC,
    # sound_effects=modern_electric_sound,
    track_type=ELRL,
    max_speed=Train.kmhish(160),
    power=4795,
    introduction_date=date(1980, 1, 1),
    vehicle_life=40,
    model_life=144,
    climates_available=grf.ALL_CLIMATES,
    weight=116,
    tractive_effort_coefficient=101,
    running_cost_factor=222,
    cargo_capacity=0,
    cost_factor=24,
    refittable_cargo_classes=grf.CargoClass.PASSENGERS,
    additional_text=grf.fake_vehicle_info({
        'Info': 'Test locomotive',
    }),
)

g.write('sfeg.grf')