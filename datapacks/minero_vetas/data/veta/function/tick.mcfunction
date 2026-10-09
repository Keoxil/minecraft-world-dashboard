scoreboard players add @a tv_agach 0
scoreboard players add @a tv_ant 0
scoreboard players operation @a tv_dif = @a tv_agach
scoreboard players operation @a tv_dif -= @a tv_ant
scoreboard players operation @a tv_ant = @a tv_agach
scoreboard players enable @a veta
execute as @a[scores={veta=1..}] run function veta:alternar
execute unless score #activado veta_cfg matches 1 run return 0
execute as @a[scores={tv_coal=1..}] run function veta:comprobar {o:"coal",b:"minecraft:coal_ore",c:"minecraft:deepslate_coal_ore",d:"minecraft:coal",x:"1"}
execute as @a[scores={tv_coald=1..}] run function veta:comprobar {o:"coald",b:"minecraft:deepslate_coal_ore",c:"minecraft:coal_ore",d:"minecraft:coal",x:"1"}
execute as @a[scores={tv_iron=1..}] run function veta:comprobar {o:"iron",b:"minecraft:iron_ore",c:"minecraft:deepslate_iron_ore",d:"minecraft:raw_iron",x:"0"}
execute as @a[scores={tv_irond=1..}] run function veta:comprobar {o:"irond",b:"minecraft:deepslate_iron_ore",c:"minecraft:iron_ore",d:"minecraft:raw_iron",x:"0"}
execute as @a[scores={tv_cop=1..}] run function veta:comprobar {o:"cop",b:"minecraft:copper_ore",c:"minecraft:deepslate_copper_ore",d:"minecraft:raw_copper",x:"0"}
execute as @a[scores={tv_copd=1..}] run function veta:comprobar {o:"copd",b:"minecraft:deepslate_copper_ore",c:"minecraft:copper_ore",d:"minecraft:raw_copper",x:"0"}
execute as @a[scores={tv_gold=1..}] run function veta:comprobar {o:"gold",b:"minecraft:gold_ore",c:"minecraft:deepslate_gold_ore",d:"minecraft:raw_gold",x:"0"}
execute as @a[scores={tv_goldd=1..}] run function veta:comprobar {o:"goldd",b:"minecraft:deepslate_gold_ore",c:"minecraft:gold_ore",d:"minecraft:raw_gold",x:"0"}
execute as @a[scores={tv_red=1..}] run function veta:comprobar {o:"red",b:"minecraft:redstone_ore",c:"minecraft:deepslate_redstone_ore",d:"minecraft:redstone",x:"3"}
execute as @a[scores={tv_redd=1..}] run function veta:comprobar {o:"redd",b:"minecraft:deepslate_redstone_ore",c:"minecraft:redstone_ore",d:"minecraft:redstone",x:"3"}
execute as @a[scores={tv_lap=1..}] run function veta:comprobar {o:"lap",b:"minecraft:lapis_ore",c:"minecraft:deepslate_lapis_ore",d:"minecraft:lapis_lazuli",x:"3"}
execute as @a[scores={tv_lapd=1..}] run function veta:comprobar {o:"lapd",b:"minecraft:deepslate_lapis_ore",c:"minecraft:lapis_ore",d:"minecraft:lapis_lazuli",x:"3"}
execute as @a[scores={tv_dia=1..}] run function veta:comprobar {o:"dia",b:"minecraft:diamond_ore",c:"minecraft:deepslate_diamond_ore",d:"minecraft:diamond",x:"5"}
execute as @a[scores={tv_diad=1..}] run function veta:comprobar {o:"diad",b:"minecraft:deepslate_diamond_ore",c:"minecraft:diamond_ore",d:"minecraft:diamond",x:"5"}
execute as @a[scores={tv_eme=1..}] run function veta:comprobar {o:"eme",b:"minecraft:emerald_ore",c:"minecraft:deepslate_emerald_ore",d:"minecraft:emerald",x:"5"}
execute as @a[scores={tv_emed=1..}] run function veta:comprobar {o:"emed",b:"minecraft:deepslate_emerald_ore",c:"minecraft:emerald_ore",d:"minecraft:emerald",x:"5"}
execute as @a[scores={tv_ngold=1..}] run function veta:comprobar {o:"ngold",b:"minecraft:nether_gold_ore",c:"minecraft:nether_gold_ore",d:"minecraft:gold_nugget",x:"1"}
execute as @a[scores={tv_nquar=1..}] run function veta:comprobar {o:"nquar",b:"minecraft:nether_quartz_ore",c:"minecraft:nether_quartz_ore",d:"minecraft:quartz",x:"3"}
