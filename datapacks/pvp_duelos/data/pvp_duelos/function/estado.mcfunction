# /function pvp_duelos:estado  -> comprueba que el datapack funciona
tellraw @s [{"text":"PvP Duelos ","color":"gold","bold":true},{"text":"activo. Duración del modo PvP: ","color":"gray","bold":false},{"score":{"name":"#duracion","objective":"pvp_cfg"},"color":"white"},{"text":" ticks (20 = 1 s).","color":"gray"}]
tellraw @s [{"text":"Regla keep_inventory gestionada por el datapack: ","color":"gray"},{"score":{"name":"#regla","objective":"pvp_cfg"},"color":"white"},{"text":"  (1 = encendida ahora mismo)","color":"gray"}]
execute if entity @a[tag=pvp_combate] run tellraw @s [{"text":"Jugadores en modo PvP: ","color":"gray"},{"selector":"@a[tag=pvp_combate]","color":"red"}]
execute unless entity @a[tag=pvp_combate] run tellraw @s {"text":"Ahora mismo nadie está en modo PvP.","color":"gray"}
