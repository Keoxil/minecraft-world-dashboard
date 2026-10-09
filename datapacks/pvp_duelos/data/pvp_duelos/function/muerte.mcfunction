# Lo ejecuta, como el jugador que acaba de reaparecer, tick.mcfunction
# Estaba en modo PvP y lo mató otro jugador: la regla estaba activa y conservó todo
execute if score @s pvp_timer matches 1.. if score @s pvp_origen matches 1.. run tellraw @a [{"text":"⚔ ","color":"red"},{"selector":"@s","color":"gold"},{"text":" ha caído en duelo y conserva su inventario.","color":"gray"}]
# Estaba en modo PvP pero murió por otra causa
execute if score @s pvp_timer matches 1.. unless score @s pvp_origen matches 1.. run tellraw @s {"text":"Has muerto por otra causa durante un duelo.","color":"gray"}
# Muerte natural fuera de un duelo: soltó el inventario como siempre
execute unless score @s pvp_timer matches 1.. run tellraw @s {"text":"Muerte natural: tu inventario se ha quedado en el suelo.","color":"gray"}
scoreboard players set @s pvp_muertes 0
scoreboard players set @s pvp_timer 0
scoreboard players set @s pvp_par 0
scoreboard players set @s pvp_dano 0
scoreboard players set @s pvp_origen 0
tag @s remove pvp_combate
