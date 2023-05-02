# hylat
Script for creating teams from a list of people with various pairing options. Originally created to make teams from families attending a school ping-pong tournament.

Required components:
* python3 installed locally
* numpy package installed
* clone this repository 
* either edit the example 'people.txt' file or create a new file
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
usage: hylat.py [-h] [-o] [-g] [-s SIZE] [-t TRIES] [-i] [-v] [-j] [-p SEPARATOR] family_file

Create teams from a file listing families of parents and kids (or other people groupings)

positional arguments:
  family_file           file containing list of families

optional arguments:
  -h, --help            show this help message and exit
  -o, --oktogether      do not force family members to be on different teams
  -g, --generations     try to create teams of the same generation (parents v kids)
  -s SIZE, --size SIZE  team size (default is 2)
  -t TRIES, --tries TRIES
                        maximum number of attempts to create valid teams (default is 10,000)
  -i, --inexact         try to match team size, but allow smaller or uneven team sizes
  -v, --verbose         display more progress information
  -j, --json            output in json
  -p SEPARATOR, --separator SEPARATOR
                        separator between team members in printout (default is ' - ')
```

THE SOFTWARE AND INSTRUCTIONS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
