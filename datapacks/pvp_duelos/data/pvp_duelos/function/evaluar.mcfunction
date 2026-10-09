# Lo ejecuta, como el jugador, tick.mcfunction cuando estando en un duelo ha recibido daño que no viene directamente de un jugador
scoreboard players set #natural pvp_cfg 1
scoreboard players set #hayatacante pvp_cfg 0
execute on attacker run scoreboard players set #hayatacante pvp_cfg 1
# a) lo atacó hace poco (menos de 5 s) un jugador: lava, caída o fuego "provocados" por el rival, como los cuenta el propio juego
execute on attacker if entity @s[type=minecraft:player] run scoreboard players set #natural pvp_cfg 0
# b) no hay atacante reciente (daño de entorno): es del duelo si el rival está cerca (cama, ancla, lava, fuego, TNT sin dueño...)
execute if score #hayatacante pvp_cfg matches 0 unless score #estricto pvp_cfg matches 1 run function pvp_duelos:rival_cerca
execute if score #hayatacante pvp_cfg matches 0 unless score #estricto pvp_cfg matches 1 if score #cerca pvp_cfg matches 1 run scoreboard players set #natural pvp_cfg 0
# c) lo atacó un mob, o el daño no tiene que ver con el rival: ajeno al duelo, se cancela
execute if score #natural pvp_cfg matches 1 run function pvp_duelos:cancelar
