# Lo ejecuta, como cada jugador en modo PvP
execute at @s if block ~ ~ ~ minecraft:lava run function pvp_duelos:peligro
execute at @s if block ~ ~1 ~ minecraft:lava run function pvp_duelos:peligro
execute store result score #fd pvp_cfg run data get entity @s fall_distance 1
execute if score #fd pvp_cfg matches 10.. run function pvp_duelos:peligro
