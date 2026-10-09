#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <player-group> <admin-group>" >&2
  exit 2
fi

player_group=$1
admin_group=$2
mapfile -t containers < <(docker ps -q --filter label=com.docker.swarm.service.name=app_minecraft-server)
if [ "${#containers[@]}" -ne 1 ]; then
  echo "Run on the minecraft-data node; expected exactly one app_minecraft-server task, found ${#containers[@]}." >&2
  exit 1
fi
container_id=${containers[0]}

set_permission() {
  docker exec "$container_id" rcon-cli "lp group $1 permission set $2 $3"
}

player_allow=(
  essentials.balance
  essentials.pay
  essentials.kit
  ei.item.emergency_return
  ei.item.administrative_enforcement_order
  EconomyShopGUI.shop
  EconomyShopGUI.shop.feato_shop
  deadchest.generate
  deadchest.get

  # GhastMaster
  ghastmaster.share

  # CraftBook: enabled user-facing mechanics.
  craftbook.mech.chair.use
  craftbook.mech.elevator
  craftbook.mech.elevator.use
  craftbook.mech.bridge
  craftbook.mech.bridge.use
  craftbook.mech.bridge.restock
  craftbook.mech.gate
  craftbook.mech.gate.use
  craftbook.mech.gate.restock
  craftbook.circuits.pipes
  craftbook.vehicles.deposit
  craftbook.vehicles.cartlift
  craftbook.vehicles.reverser
  craftbook.vehicles.station
)
player_deny=(
  essentials.spawn
  essentials.kits.return_ticket
  EconomyShopGUI.shop.all
  EconomyShopGUI.sellall
  EconomyShopGUI.sellallitem
  EconomyShopGUI.sellallhand
  EconomyShopGUI.sellgui
  EconomyShopGUI.sellall.all
  EconomyShopGUI.sellallitem.all
  EconomyShopGUI.sellallhand.all
  EconomyShopGUI.sellgui.all
)
admin_allow=(
  feato.gunvalhalla.reload
  feato.horsemanship.admin
  essentials.balance.others
  essentials.eco
  essentials.setspawn
  essentials.createkit
  essentials.showkit
  EconomyShopGUI.reload
  EconomyShopGUI.itemindexes
  EconomyShopGUI.eshop.additem
  EconomyShopGUI.eshop.edititem
  EconomyShopGUI.eshop.deleteitem
  EconomyShopGUI.eshop.addhanditem
  EconomyShopGUI.eshop.addsection
  EconomyShopGUI.eshop.editsection
  EconomyShopGUI.eshop.deletesection
  fancynpcs.command.npc.create
  fancynpcs.command.npc.remove
  fancynpcs.command.npc.list
  fancynpcs.command.npc.info
  fancynpcs.command.npc.displayname
  fancynpcs.command.npc.skin
  fancynpcs.command.npc.move_to
  fancynpcs.command.npc.interaction_cooldown
  fancynpcs.command.npc.action.add
  fancynpcs.command.npc.action.add.need_permission
  fancynpcs.command.npc.action.add.message
  fancynpcs.command.npc.action.add.player_command
  fancynpcs.command.npc.action.add.console_command
  fancynpcs.command.npc.action.remove
  fancynpcs.command.npc.action.clear
  fancynpcs.command.npc.action.list
  fancynpcs.command.fancynpcs.reload
  fancynpcs.command.fancynpcs.save
)

fancyholograms_manage=(
  fancyholograms.admin
  fancyholograms.hologram.list
  fancyholograms.hologram.nearby
  fancyholograms.hologram.create
  fancyholograms.hologram.remove
  fancyholograms.hologram.copy
  fancyholograms.hologram.info
  fancyholograms.hologram.teleport
  fancyholograms.hologram.edit.move_here
  fancyholograms.hologram.edit.center
  fancyholograms.hologram.edit.move_to
  fancyholograms.hologram.edit.rotate
  fancyholograms.hologram.edit.rotate_pitch
  fancyholograms.hologram.edit.translate
  fancyholograms.hologram.edit.scale
  fancyholograms.hologram.edit.billboard
  fancyholograms.hologram.edit.visibility_distance
  fancyholograms.hologram.edit.visibility
  fancyholograms.hologram.edit.shadow_radius
  fancyholograms.hologram.edit.shadow_strength
  fancyholograms.hologram.edit.background
  fancyholograms.hologram.edit.text_shadow
  fancyholograms.hologram.edit.text_alignment
  fancyholograms.hologram.edit.see_trough
  fancyholograms.hologram.edit.block
  fancyholograms.hologram.edit.item
  fancyholograms.hologram.edit.insert_before
  fancyholograms.hologram.edit.insert_after
  fancyholograms.hologram.edit.text_interval
  fancyholograms.hologram.edit.line.add
  fancyholograms.hologram.edit.line.remove
  fancyholograms.hologram.line.set
  fancyholograms.hologram.link
  fancyholograms.hologram.unlink
)

for permission in "${player_allow[@]}"; do set_permission "$player_group" "$permission" true; done
for permission in "${player_deny[@]}"; do set_permission "$player_group" "$permission" false; done
for permission in "${admin_allow[@]}"; do set_permission "$admin_group" "$permission" true; done

for role_group in mayor guard_captain town_clerk; do
  docker exec "$container_id" rcon-cli "lp creategroup $role_group"
done
set_permission mayor feato.mayor true
set_permission mayor ei.item.mayor_flag true
set_permission mayor slots.admin true
docker exec "$container_id" rcon-cli "lp group mayor meta setprefix 100 &9[村長] "
set_permission guard_captain feato.guard_captain true
set_permission guard_captain ei.item.guard_captain_flag true
set_permission town_clerk feato.town_clerk true
set_permission town_clerk essentials.kits.administrative_enforcement_order true

for permission in "${fancyholograms_manage[@]}"; do
  set_permission "$admin_group" "$permission" true
  set_permission mayor "$permission" true
  set_permission town_clerk "$permission" true
done

echo "Permissions applied to player group '$player_group' and admin group '$admin_group'."
echo "Mayor prefix configured: '[村長]'."
echo "Assign with: lp user <player> parent add mayor"
echo "Remove with: lp user <player> parent remove mayor"
