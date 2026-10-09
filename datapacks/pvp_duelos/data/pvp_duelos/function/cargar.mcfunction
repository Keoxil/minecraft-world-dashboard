# Se ejecuta al cargar el mundo y con /reload
scoreboard objectives add pvp_timer dummy
scoreboard objectives add pvp_muertes deathCount
scoreboard objectives add pvp_cfg dummy
scoreboard objectives add pvp_par dummy
scoreboard objectives add pvp_origen dummy
scoreboard objectives add pvp_dano dummy
scoreboard players set #20 pvp_cfg 20
scoreboard players add #sig pvp_cfg 0
# Modo estricto (0 = normal, 1 = estricto): ver LEEME
scoreboard players add #estricto pvp_cfg 0
# Duración del modo PvP tras el último golpe entre jugadores, en ticks (1200 = 60 s). Se puede cambiar con:
#   /scoreboard players set #duracion pvp_cfg 600
execute unless score #duracion pvp_cfg matches 1.. run scoreboard players set #duracion pvp_cfg 1200
# la primera versión usaba 200 ticks (10 s): se actualiza a 60 s
execute if score #duracion pvp_cfg matches 200 run scoreboard players set #duracion pvp_cfg 1200
# Este datapack controla la regla: por defecto, las muertes naturales sueltan el inventario
gamerule keep_inventory false
scoreboard players set #regla pvp_cfg 0
