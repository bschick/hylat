# hylat
Script for creating teams from a list of people with various pairing options. Originally created to make teams from families attending a school ping-pong tournament.

Required components:
* python3 installed locally
* numpy package installed
* clone this repository 
* edit the example 'people.txt' file or create a new file
* run hylat

Example usage:
```
% ./hylat.py --size 3 -v people.txt
~~~~ Plan ~~~~
team sizes of exactly 3
family memebers kept apart
parents and kids mixed

~~~~ Distributing ~~~~
11 kids and 7 parents

~~~~ Results (6 teams)~~~~
Olivia Randall - Gordon Wallace - Craig Manning
Felicity Allan - Hennry Manning - Luke
Eric Peters - Kid Gray - Parker Randall
Ava Peters - Brother Peake - Hills Wallace
Parent Gray - James Freeman - Samantha Peake
Jack Manning - Weston Peters - Matthew Randall
```

Script usage:
```
usage: hylat.py [-h] [-o] [-g] [-s TEAMSIZE] [-c TEAMCOUNT] [-t TRIES] [-d] [-u] [-j] [-r {closest,down,up}] [-p SEPARATOR]
                [-v] family_file

Create teams from a file listing groups of people in different categories (like family with kids and parents)

positional arguments:
  family_file           file containing list of families

options:
  -h, --help            show this help message and exit
  -o, --oktogether      allow familes to be on the same team
  -g, --generations     try to create teams from the same category (aka parents v kids)
  -s TEAMSIZE, --teamsize TEAMSIZE
                        size of each team, must be more than 1 (default is 2)
  -c TEAMCOUNT, --teamcount TEAMCOUNT
                        number of teams, must be more than 1
  -t TRIES, --tries TRIES
                        maximum number of attempts to create valid teams (default is 10,000)
  -d, --drop            drop random extra people if teams are not even
  -u, --uneven          try to match team size, but allow uneven team sizes
  -j, --json            output in json
  -r {closest,down,up}, --round {closest,down,up}
                        used with --uneven and --teamsize to round resulting number of teams down, up, or to closest even
                        number (default is 'closest')
  -p SEPARATOR, --separator SEPARATOR
                        separator between team members in printout (default is ' - ')
  -v, --verbose         display more progress information
```

THE SOFTWARE AND INSTRUCTIONS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
