# 0) marcadores al día (agacharse = el contador sneak_time sube cada tick)
scoreboard players add @a tc_agach 0
scoreboard players add @a tc_ant 0
scoreboard players operation @a tc_dif = @a tc_agach
scoreboard players operation @a tc_dif -= @a tc_ant
scoreboard players operation @a tc_ant = @a tc_agach
# 1) cada jugador puede activar/desactivar el talado con /trigger talar
scoreboard players enable @a talar
execute as @a[scores={talar=1..}] run function talar:alternar
# 2) quien acaba de picar un tronco
execute unless score #activado talar_cfg matches 1 run return 0
execute as @a[scores={tc_oak=1..}] run function talar:comprobar {id:"minecraft:oak_log",o:"oak",s:"minecraft:oak_sapling"}
execute as @a[scores={tc_spruce=1..}] run function talar:comprobar {id:"minecraft:spruce_log",o:"spruce",s:"minecraft:spruce_sapling"}
execute as @a[scores={tc_birch=1..}] run function talar:comprobar {id:"minecraft:birch_log",o:"birch",s:"minecraft:birch_sapling"}
execute as @a[scores={tc_jungle=1..}] run function talar:comprobar {id:"minecraft:jungle_log",o:"jungle",s:"minecraft:jungle_sapling"}
execute as @a[scores={tc_acacia=1..}] run function talar:comprobar {id:"minecraft:acacia_log",o:"acacia",s:"minecraft:acacia_sapling"}
execute as @a[scores={tc_dark_oak=1..}] run function talar:comprobar {id:"minecraft:dark_oak_log",o:"dark_oak",s:"minecraft:dark_oak_sapling"}
execute as @a[scores={tc_mangrove=1..}] run function talar:comprobar {id:"minecraft:mangrove_log",o:"mangrove",s:"minecraft:mangrove_propagule"}
execute as @a[scores={tc_cherry=1..}] run function talar:comprobar {id:"minecraft:cherry_log",o:"cherry",s:"minecraft:cherry_sapling"}
execute as @a[scores={tc_pale_oak=1..}] run function talar:comprobar {id:"minecraft:pale_oak_log",o:"pale_oak",s:"minecraft:pale_oak_sapling"}
