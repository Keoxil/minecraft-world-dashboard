# Lava o caída larga: es del duelo si el rival está cerca (trampa de lava, empujón...); si no, es un peligro ajeno y cancela
function pvp_duelos:rival_cerca
execute unless score #estricto pvp_cfg matches 1 if score #cerca pvp_cfg matches 1 run return 0
function pvp_duelos:cancelar
