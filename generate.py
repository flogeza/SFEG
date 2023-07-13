import os
from datetime import date
from pathlib import Path

import grf

import lib

# DEBUG_DIR = 'debug'
# os.makedirs(DEBUG_DIR, exist_ok=True)

g = grf.NewGRF(
    grfid=b'V637',
    name='V63_007',
    description='V63_007',
    url='https://github.com/flogeza/SFEG',
    id_map_file='id_map.json',
)

g.set_cargo_table(('OIL_',))

Train, Ship = map(g.bind, (grf.Train, lib.Ship))

set_global_train_y_offset = lambda ofs: grf.ComputeParameters(target=0x8e, operation=0x00, if_undefined=False, source1=0xff, source2=0xff, value=ofs)
g.add(set_global_train_y_offset(4))

# g.add(lib.set_global_train_depot_width_32())

RAIL, ELRL, MONO, MGLV = g.set_railtype_table(['RAIL', 'ELRL', 'MONO', 'MGLV'])


def make_sprites(path, offsets, mask_path=None):
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
        for zoom in offsets.keys():
            xofs, yofs = offsets[zoom][view]
            file_view = VIEW_FILES[view]
            png = grf.ImageFile(path / f'{zoom}_{file_view:04}.png')
            sprite_zoom = ZOOM_CONSTANT[zoom]
            mask = None
            if mask_path:
                mask = (grf.ImageFile(Path(mask_path) / f'{zoom}_{file_view:04}_mask.png'), 0, 0)
            alt.append(grf.FileSprite(png, 0, 0, 768, 768, xofs=xofs - 384, yofs=yofs - 384, zoom=sprite_zoom, mask=mask))
        sprites.append(grf.AlternativeSprites(*alt))

    return [{
        'name': 'Default',
        'sprites': sprites,
    }]


def make_train_sprites(path):
    OFFSETS = {
        64: [
            (1, 0),
            (-6, -4),
            (0, -7),
            (6, -6),
            (1, 0),
            (-6, -4),
            (0, -7),
            (6, -6),
        ],
        128: [
            (2, 0),
            (-12, -8),
            (0, -14),
            (12, -12),
            (2, 0),
            (-12, -8),
            (0, -14),
            (12, -12),
        ],
        256: [
            (4, 0),
            (-24, -16),
            (0, -28),
            (24, -24),
            (4, 0),
            (-24, -16),
            (0, -28),
            (24, -24),
        ],
    }

    return make_sprites(path, OFFSETS)


def make_ship_sprites(path_empty, mask_path, path_loaded):
    OFFSETS = {
        64: [
            (1, 0),
            (-6, -4),
            (0, -7),
            (6, -6),
            (1, 0),
            (-6, -4),
            (0, -7),
            (6, -6),
        ],
    }

    empty = make_sprites(path_empty, OFFSETS, mask_path=mask_path)[0]
    loaded = make_sprites(path_loaded, OFFSETS, mask_path=mask_path)[0]
    return [{
        'name': empty['name'],
        'sprites': lib.VehicleSprites(
            moving=[
                empty['sprites'],
                empty['sprites'],
                empty['sprites'],
                loaded['sprites'],
            ],
        ),
    }]



Train(
    id=1,
    name='V63 "Gigant"',
    length=22,
    liveries=make_train_sprites('v63nagyr4'),
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


Ship(
    id=300,
    name='CVN68',
    liveries=make_ship_sprites('cvn68', 'cvn68_mask2cc', 'cvn68_loaded'),
    max_speed=Ship.kmh(100),
    introduction_date=date(1980, 1, 1),
    vehicle_life=40,
    model_life=144,
    climates_available=grf.ALL_CLIMATES,
    running_cost_factor=222,
    cargo_capacity=20,
    cost_factor=24,
    default_cargo_type=g.get_cargo_id('OIL_'),
    # refittable_cargo_classes=grf.CargoClass.LIQUID | grf.CargoClass.PIECE_GOODS,
    additional_text=grf.fake_vehicle_info({
        'Info': 'Test ship',
    }),
)


g.write('V637.grf')