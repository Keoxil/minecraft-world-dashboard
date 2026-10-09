scoreboard players set @s casa 0
# durante un duelo PvP no se puede huir a casa
execute if entity @s[tag=pvp_combate] run return run tellraw @s {"text":"No puedes volver a casa durante un duelo PvP.","color":"red"}
execute unless data entity @s respawn.pos run return run tellraw @s {"text":"Todavía no has dormido en ninguna cama.","color":"red"}
data modify storage casa:tmp x set from entity @s respawn.pos[0]
data modify storage casa:tmp y set from entity @s respawn.pos[1]
data modify storage casa:tmp z set from entity @s respawn.pos[2]
data modify storage casa:tmp dim set from entity @s respawn.dimension
function casa:viajar with storage casa:tmp
