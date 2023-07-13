import grf

class VehicleSprites:
    def __init__(self, moving, loading=None):
        if isinstance(moving, VehicleSprites):
            self.moving = moving.moving
            self.loading = moving.loading
            return

        self.moving = moving
        self.loading = loading

    def __len__(self):
        # HACKS! xd
        return 8

    def get_sprites(self):
        res = []
        sets = []
        next_set_id = 0
        moving_range = []
        loading_range = []

        used_sets = {}

        def add_set(s):
            nonlocal next_set_id
            key = tuple(s)
            set_id = used_sets.get(key)
            if set_id is None:
                set_id = next_set_id
                next_set_id += 1
                used_sets[key] = set_id
                sets.append(s)
            return set_id


        moving_range = [add_set(s) for s in self.moving]

        if self.loading is not None:
            loading_range = [add_set(s) for s in self.loading]
        else:
            loading_range = moving_range

        layout = grf.GenericSpriteLayout(
            ent1=moving_range,
            ent2=loading_range,
        )

        res.append(grf.Action1(
            feature=grf.SHIP,
            set_count=len(sets),
            sprite_count=8,
        ))

        for s in sets:
            res.extend(s)

        return layout, res


class Ship(grf.Ship):
    def get_sprites(self, g):
        res = self._gen_purchase_sprites()
        sprite_actions = []

        if self.liveries:
            layouts = []
            for i, l in enumerate(self.liveries):
                layout, actions = l['sprites'].get_sprites()
                layouts.append(layout)
                sprite_actions.extend(actions)

            if len(self.liveries) > 1:

                self.callbacks.graphics = grf.Switch(
                    related_scope=True,
                    ranges=dict(enumerate(layouts)),
                    default=layouts[0],
                    code='cargo_subtype',
                )
            else:
                self.callbacks.graphics = layouts[0]

        res.extend(self._set_callbacks(g))

        # Liveries
        if self.liveries and len(self.liveries) > 1:
            self.callbacks.cargo_subtype = grf.Switch(
                ranges={i: g.strings.add(l['name']).get_global_id() for i, l in enumerate(self.liveries)},
                default=0x400,
                code='cargo_subtype',
            )

        self.callbacks.set_flag_props(self._props)

        res.extend(self._gen_name_sprites(self.id))

        res.append(definition := grf.Define(
            feature=grf.SHIP,
            id=self.id,
            props={
                'sprite_id': 0xff,
                'max_speed': self.max_speed,
                **self._props
            }
        ))

        res.extend(sprite_actions)

        res.append(self.callbacks.make_map_action(definition))
        return res