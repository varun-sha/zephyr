Please read this for using Uvision project generation script for Zephyr:-


1)
Build you zephyr sample:-
Dependencies:-
a)Install uvision5 from http://www2.keil.com/mdk5 select MDK-Professional, user need to have license to use professional version.


b)Create windows environment for zephyr using http://docs.zephyrproject.org/getting_started/installation_win.html

Install python3.6.x( we have used 3.6.5)
Install requirements.txt using 
command: 
For zephyr compilation:-
pip install -r zephyr\Scripts\requirements.txt
and
For uvision project generation:-
pip install -r zephyr\Scripts\tools\requirements.txt


Setup arm based toolchain as mentioned in  http://docs.zephyrproject.org/getting_started/installation_win.html 
& try a sample build.
e.g:-
cd %ZEPHYR_BASE%\samples\hello_world\
mkdir build & cd build
cmake -GNinja -DBOARD=sam_e70_xplained ..
ninja

2)
Use "project.py" to generate uvision project( -m switch is for target, -i for ide)
use build folder as current directory for executing script
e.g:-
cd %ZEPHYR_BASE%\zephyr\samples\hello_world\build
python -u %ZEPHYR_BASE%\scripts\tools\project.py -i uvision -m SAME70Q21 --source .


3)
On Executing above command
C:\Users\varunsha\zephyr\scripts
supported targets:['K64F', 'SAME70Q21']
project name:hello_world
toolchain_name:GCC_ARM
ide:uvision5
scan: ['.'] C:\Users\varunsha\zephyr\samples\hello_world\build
linker:C:\Users\varunsha\zephyr\samples\hello_world\build\zephyr\linker.cmd
 generating...
 
You will get 2 uvision project files in current folder
As of now Toolchain: GCC_ARM & target:  SAME70Q21 & K64F are supported , additional targets can be added by editing  target.json, index.json &  alias.json

4)Build:-

Build is done from cmake & ninja only and not from Keil.
So rebuild using cmake and run export project script. Keil project will automatically get updated if project is generated at same location.