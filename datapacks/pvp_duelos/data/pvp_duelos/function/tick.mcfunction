# 0) que nadie tenga marcadores vacíos
scoreboard players add @a pvp_dano 0
scoreboard players add @a pvp_origen 0
scoreboard players add @a pvp_par 0
# 1) quien ha muerto desde el último tick (primero, para limpiar sus marcadores)
execute as @a[scores={pvp_muertes=1..}] run function pvp_duelos:muerte
# 2) daño que NO viene directamente de un jugador estando en un duelo: ¿lo ha provocado el rival (lava, cama, ancla, fuego...) o es ajeno?
execute as @a[tag=pvp_combate,scores={pvp_dano=1..,pvp_origen=0}] run function pvp_duelos:evaluar
scoreboard players set @a[scores={pvp_dano=1..}] pvp_dano 0
scoreboard players set @a[scores={pvp_origen=1..}] pvp_origen 0
# 3) peligros que no esperan al primer daño: lava y caídas largas
execute as @a[tag=pvp_combate] run function pvp_duelos:vigilar
# 4) cuenta atrás de quienes están en modo PvP
scoreboard players remove @a[scores={pvp_timer=1..}] pvp_timer 1
# 5) entrar y salir del modo PvP
execute as @a[tag=!pvp_combate,scores={pvp_timer=1..}] run function pvp_duelos:entrar
execute as @a[tag=pvp_combate] unless score @s pvp_timer matches 1.. run function pvp_duelos:salir
# 6) aviso con la cuenta atrás
execute as @a[tag=pvp_combate] run function pvp_duelos:aviso
# 7) regla de inventario: activa mientras haya alguien en modo PvP
execute if entity @a[tag=pvp_combate] unless score #regla pvp_cfg matches 1 run function pvp_duelos:regla_on
execute unless entity @a[tag=pvp_combate] if score #regla pvp_cfg matches 1 run function pvp_duelos:regla_off
