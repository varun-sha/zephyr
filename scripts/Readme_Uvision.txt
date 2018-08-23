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
cd C:\Users\varunsha\zephyr\samples\hello_world\
mkdir build & cd build
cmake -GNinja -DBOARD=frdm_k64f ..
ninja

2)
Use "project.py" to generate uvision project( -m switch is for target, -i for ide)
use build folder as current directory for executing script
e.g:-
cd C:\Users\varunsha\zephyr\samples\hello_world\build
python -u C:\Users\varunsha\zephyr\scripts\tools\project.py -i uvision -m K64F --source .
or
python -u %ZEPHYR_BASE%\scripts\tools\project.py -i uvision -m K64F --source .


3)
On Executing above command
C:\Users\varunsha\zephyr\samples\hello_world\build>python -u C:\Users\varunsha\zephyr\scripts\tools\project.py -i uvision -m K64F --source .
C:\Users\varunsha\zephyr\scripts
VARUN:C:\Users\varunsha\zephyr\scripts\tools\targets\..\..\targets\targets.json
supported targets:[u'K64F']
project name:hello_world
toolchain_name:GCC_ARM
ide:uvision5
scan: ['.'] C:\Users\varunsha\zephyr\samples\hello_world\build
linker:C:\Users\varunsha\zephyr\samples\hello_world\build\zephyr\linker.cmd
 generating...
 
You will file 2 files u
As of now GCC_ARM & K64F is supported , additional targets can be added by editing  target.json, index.json &  alias.json

4) Working model:-

Build is done from cmake & ninja only.
ninja generates deps file( .ninja_deps), I have used this file to create project depency list using command "ninja -t deps" using scripts & then used that file to populate zephyr source code for uvision.
scan_resources_zephyr() is used to acheive above functionality.

Then after created c/h/cpp/s/linker files resource dictionary, it is fed to uvision generater, which fills various values in template & create uvision project.
Various helper scripts for toolchain, target, export, utils  & path are required & have been changed according to Zephyr requirements.
