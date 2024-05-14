docker run -it --rm --name mynodered --net lab4_network -p 1880:1880 -v %cd%\nodered\data\:/data nodered/node-red
pause