#!/usr/bin/env python3
"""BreweryX 3.7.1追加設定の静的検証。PyYAML、JDKのjavapが必要。

品質は3.7.1のBIngredients/BRecipeを基に材料・加熱の評価を計算する。
熟成・樽材の減点を省いた候補上限で一意性を判定し、実機動作は保証しない。
"""
import argparse
import math
from pathlib import Path
import re
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "minecraft/java/plugins/BreweryX"
BASELINE = "6956c10c1af0a92bedc9b305c1ef27c9cd859cf6"

EXPECTED = [{'id': 'feato_black_tea',
  'name': '紅茶',
  'ingredients': ['feato_tea_leaves/6'],
  'cookingtime': 2,
  'difficulty': 2,
  'effects': [['HASTE', 30]]},
 {'id': 'feato_milk_tea',
  'name': 'ミルクティー',
  'ingredients': ['feato_tea_leaves/6', 'MILK_BUCKET/1', 'SUGAR/2'],
  'cookingtime': 2,
  'difficulty': 2,
  'effects': [['HASTE', 30], ['REGENERATION', 5]]},
 {'id': 'feato_royal_milk_tea',
  'name': 'ロイヤルミルクティー',
  'ingredients': ['feato_tea_leaves/10', 'MILK_BUCKET/3', 'SUGAR/3'],
  'cookingtime': 4,
  'difficulty': 4,
  'effects': [['HASTE', 60], ['REGENERATION', 8]]},
 {'id': 'feato_apple_tea',
  'name': 'アップルティー',
  'ingredients': ['feato_tea_leaves/6', 'APPLE/2'],
  'cookingtime': 3,
  'difficulty': 3,
  'effects': [['HASTE', 30], ['SPEED', 30]]},
 {'id': 'feato_berry_tea',
  'name': 'ベリーティー',
  'ingredients': ['feato_tea_leaves/6', 'SWEET_BERRIES/4'],
  'cookingtime': 3,
  'difficulty': 3,
  'effects': [['HASTE', 30], ['REGENERATION', 8]]},
 {'id': 'feato_honey_tea',
  'name': 'ハニーティー',
  'ingredients': ['feato_tea_leaves/6', 'HONEY_BOTTLE/1'],
  'cookingtime': 3,
  'difficulty': 3,
  'effects': [['HASTE', 45], ['REGENERATION', 5]]},
 {'id': 'feato_iced_tea',
  'name': 'アイスティー',
  'ingredients': ['feato_tea_leaves/6', 'SNOWBALL/4', 'SUGAR/1'],
  'cookingtime': 1,
  'difficulty': 3,
  'effects': [['SPEED', 30], ['HASTE', 20]]},
 {'id': 'feato_caffe_latte',
  'name': 'カフェラテ',
  'ingredients': ['COCOA_BEANS/8', 'MILK_BUCKET/3'],
  'cookingtime': 2,
  'difficulty': 2,
  'effects': [['SPEED', 60], ['REGENERATION', 5]]},
 {'id': 'feato_caffe_mocha',
  'name': 'カフェモカ',
  'ingredients': ['COCOA_BEANS/8', 'MILK_BUCKET/2', 'COOKIE/3'],
  'cookingtime': 3,
  'difficulty': 3,
  'effects': [['SPEED', 45], ['HASTE', 45]]},
 {'id': 'feato_honey_latte',
  'name': 'ハニーラテ',
  'ingredients': ['COCOA_BEANS/8', 'MILK_BUCKET/2', 'HONEY_BOTTLE/1'],
  'cookingtime': 3,
  'difficulty': 3,
  'effects': [['SPEED', 45], ['REGENERATION', 8]]},
 {'id': 'feato_hot_milk',
  'name': 'ホットミルク',
  'ingredients': ['MILK_BUCKET/2'],
  'cookingtime': 1,
  'difficulty': 2,
  'effects': [['REGENERATION', 5]]},
 {'id': 'feato_honey_milk',
  'name': 'ハニーミルク',
  'ingredients': ['MILK_BUCKET/2', 'HONEY_BOTTLE/1'],
  'cookingtime': 2,
  'difficulty': 2,
  'effects': [['REGENERATION', 10]]},
 {'id': 'feato_sansai_soup',
  'name': '山菜スープ',
  'ingredients': ['FERN/4', 'POTATO/3'],
  'cookingtime': 4,
  'difficulty': 3,
  'effects': [['REGENERATION', 12]]},
 {'id': 'feato_berry_compote',
  'name': 'ベリーコンポート',
  'ingredients': ['SWEET_BERRIES/12', 'SUGAR/4'],
  'cookingtime': 3,
  'difficulty': 3,
  'effects': [['REGENERATION', 10]]},
 {'id': 'feato_panna_cotta',
  'name': 'パンナコッタ',
  'ingredients': ['MILK_BUCKET/4', 'SUGAR/2', 'SLIME_BALL/1', 'SNOWBALL/2'],
  'cookingtime': 3,
  'difficulty': 4,
  'effects': [['REGENERATION', 12]]},
 {'id': 'feato_coffee_jelly',
  'name': 'コーヒーゼリー',
  'ingredients': ['COCOA_BEANS/8', 'SUGAR/3', 'SLIME_BALL/1', 'SNOWBALL/2'],
  'cookingtime': 3,
  'difficulty': 3,
  'effects': [['SPEED', 45], ['HASTE', 30]]},
 {'id': 'feato_nutrition_jelly',
  'name': '栄養補給ゼリー',
  'ingredients': ['APPLE/2', 'HONEY_BOTTLE/1', 'SUGAR/2', 'SLIME_BALL/1', 'SNOWBALL/2'],
  'cookingtime': 3,
  'difficulty': 4,
  'effects': [['REGENERATION', 10], ['SPEED', 20]]},
 {'id': 'feato_imo_shochu',
  'name': '芋焼酎',
  'ingredients': ['POTATO/12', 'WHEAT/3'],
  'cookingtime': 12,
  'difficulty': 4,
  'effects': [['RESISTANCE', 15], ['WEAKNESS', 30]]}]

class UniqueLoader(yaml.SafeLoader):
    pass


def mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def load(text):
    return yaml.load(text, Loader=UniqueLoader)


def git_file(path):
    return subprocess.check_output(
        ["git", "show", f"{BASELINE}:{path}"], cwd=ROOT, text=True
    )


def parts(ingredients):
    return [(name, int(count)) for name, count in (x.split("/") for x in ingredients)]


def matches(name, material, custom):
    if name in custom:
        return material.lower() in [x.lower() for x in custom[name]["material"]]
    return name == material


def ingredient_quality(recipe, actual, custom):
    wanted = parts(recipe["ingredients"])
    if any(not any(matches(name, mat, custom) for mat in actual) for name, _ in wanted):
        return -1
    quality = 10.0
    bad = 0
    for mat, count in actual.items():
        expected = next((n for name, n in wanted if matches(name, mat, custom)), 0)
        if not expected:
            bad += 1
            if count > sum(actual.values()) / 2 or bad >= len(actual):
                return -1
            quality -= count * recipe.get("difficulty", 0) / 2
        elif count != expected:
            allowed = max(1, math.floor((11 - recipe.get("difficulty", 0)) * max(8, expected) / 10 + .5))
            quality -= abs(count - expected) / allowed * 10
    return quality if quality >= 0 else -1


def quality_upper_bound(recipe, actual, time, distilled, custom):
    iq = ingredient_quality(recipe, actual, custom)
    if iq < 0 or (recipe.get("distillruns", 0) > 0) != distilled:
        return -1
    allowed = max(1, math.floor((11 - recipe.get("difficulty", 0)) * max(8, recipe["cookingtime"]) / 10 + .5))
    cq = 0 if time < 1 else 10 - abs(time - recipe["cookingtime"]) / allowed * 10
    if cq < 0:
        return -1
    # Age/wood qualities cannot exceed 10. Their actual penalties are omitted.
    return (iq + cq + 20) / 4 if recipe.get("age", 0) > 0 else (iq + cq) / 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-api", type=Path, required=True)
    parser.add_argument("--default-custom-items", type=Path, required=True,
                        help="3.7.1が隔離環境で生成した原本")
    args = parser.parse_args()
    recipes = load((BASE / "recipes.yml").read_text())["recipes"]
    custom = load((BASE / "custom-items.yml").read_text())["customItems"]
    original = load(git_file("minecraft/java/plugins/BreweryX/recipes.yml"))["recipes"]
    assert len(original) == 24 and sum(x.get("enabled", True) for x in original.values()) == 23
    assert all(recipes[key] == value for key, value in original.items()), "Existing recipe changed"
    assert set(recipes) - set(original) == {r["id"] for r in EXPECTED}
    assert len(recipes) == 42 and sum(x.get("enabled", True) for x in recipes.values()) == 41
    defaults = load(args.default_custom_items.read_text())["customItems"]
    assert set(custom) == set(defaults) | {"feato_tea_leaves"}
    assert all(custom[key] == value for key, value in defaults.items())
    assert custom["blue-flowers"] == {"matchAny": True, "material": ["cornflower", "blue_orchid"]}
    assert "blue-flowers/6" in recipes["gin"]["ingredients"]
    assert custom["feato_tea_leaves"] == {
        "matchAny": True, "material": ["OAK_LEAVES", "DARK_OAK_LEAVES"]}
    enum = subprocess.check_output(["javap", "-classpath", str(args.paper_api), "org.bukkit.Material"], text=True)
    materials = set(re.findall(r"public static final org.bukkit.Material (\w+);", enum))
    assert materials
    for definition in custom.values():
        if "material" in definition:
            values = definition["material"]
            for mat in values if isinstance(values, list) else [values]:
                assert mat.upper() in materials, mat
    active = {k: r for k, r in recipes.items() if r.get("enabled", True)}
    exact = boundary = 0
    for spec in EXPECTED:
        rid = spec["id"]
        r = recipes[rid]
        distilled = rid == "feato_imo_shochu"
        assert r["name"] == f"薄い{spec['name']}/{spec['name']}/上質な{spec['name']}"
        for field in ("ingredients", "cookingtime", "difficulty"):
            assert r[field] == spec[field], (rid, field)
        assert r["age"] == 0 and r["distillruns"] == (2 if distilled else 0)
        assert r["alcohol"] == (18 if distilled else 0)
        assert r.get("distilltime") == (60 if distilled else None)
        effects = [f"{name}/1-1/{60 if name == 'WEAKNESS' else max(3 if name == 'REGENERATION' else 0, seconds // 2)}-{seconds}"
                   for name, seconds in spec["effects"]]
        assert r["effects"] == effects, rid
        assert all(re.fullmatch(r"(SPEED|HASTE|REGENERATION|RESISTANCE|WEAKNESS)/1-1/\d+-\d+", x) for x in r["effects"])
        assert re.fullmatch(r"[0-9a-fA-F]{6}", str(r["color"]))
        assert all(re.search(r"[ぁ-龥]", line) for line in r["lore"])
        assert re.search(r"[ぁ-龥]", r["drinkmessage"])
        assert not ({"playercommands", "servercommands", "customModelData", "itemModel"} & set(r))
        leaves = ["OAK_LEAVES", "DARK_OAK_LEAVES"] if any(x.startswith("feato_tea_leaves/") for x in r["ingredients"]) else [None]
        for leaf in leaves:
            actual = {leaf if name == "feato_tea_leaves" else name: count for name, count in parts(r["ingredients"])}
            assert all(mat in materials for mat in actual)
            scores = {k: quality_upper_bound(v, actual, r["cookingtime"], distilled, custom) for k, v in active.items()}
            assert scores[rid] == 10
            assert all(score < 10 for k, score in scores.items() if k != rid), (rid, scores)
            exact += 1
            first = next(iter(actual))
            missing = {k: n for k, n in actual.items() if k != first}
            assert ingredient_quality(r, missing, custom) == -1
            variants = [("missing", missing, r["cookingtime"]),
                        ("less", {**actual, first: actual[first] - 1}, r["cookingtime"]),
                        ("more", {**actual, first: actual[first] + 1}, r["cookingtime"]),
                        ("short", actual, r["cookingtime"] - 1),
                        ("long", actual, r["cookingtime"] + 1),
                        ("extra", {**actual, "DIRT": 1}, r["cookingtime"])]
            if leaf:
                mixed = dict(actual)
                mixed[leaf] //= 2
                mixed["DARK_OAK_LEAVES" if leaf == "OAK_LEAVES" else "OAK_LEAVES"] = actual[leaf] - mixed[leaf]
                variants.append(("mixed", mixed, r["cookingtime"]))
            for label, contents, time in variants:
                score = quality_upper_bound(r, contents, time, distilled, custom)
                assert score < 10, (rid, label, score)
                boundary += 1
                # Show possible competitors without interpreting tolerance as outright failure.
                competitors = sorted(((k, quality_upper_bound(v, contents, time, distilled, custom))
                                      for k, v in active.items()), key=lambda x: x[1], reverse=True)
                print(f"{rid} {leaf or '-'} {label}: target upper={score:.3f}; best upper={competitors[0]}")
    for relative in ("minecraft/java/plugins.txt", "minecraft/java/plugins/BreweryX/config.yml", "minecraft/java/plugins/BreweryX/languages/ja.yml"):
        assert (ROOT / relative).read_text() == git_file(relative), relative
    print(f"PASS: 18 additions, 23 originals unchanged; {exact} exact cases uniquely quality 10; {boundary} boundary cases; defaults/gin/materials/effects/config/version pins")


if __name__ == "__main__":
    main()
