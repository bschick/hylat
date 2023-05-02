# hylat
Script for creating teams from a list of people with various pairing options. Originally created to make teams from families attending a school ping-pong tournament.

Required components:
* python3 installed locally
* numpy package installed
* clone this repository and either edit the example 'people.txt' file or create a new file
* run hylat

Scipt usage:
```
usage: hylat.py [-h] [-o] [-g] [-s SIZE] [-t TRIES] [-u] [-v] [-j] [-p SEPARATOR] family_file

Create teams from a file listing families of parents and kids (or other people groupings)

positional arguments:
  family_file           file containing list of families

optional arguments:
  -h, --help            show this help message and exit
  -o, --oktogether      do not force family members to be on different teams
  -g, --generations     try to create teams of the same generation (parents v kids)
  -s SIZE, --size SIZE  team size (default is 2)
  -t TRIES, --tries TRIES
                        maximum number of attempts to create valid teams before giving up (default is 10,000)
  -u, --uneven          try to match team sizes, but allow smaller teams or uneven teams
  -v, --verbose         display progress information
  -j, --json            output in json
  -p SEPARATOR, --separator SEPARATOR
                        separator between team members in printout (default is ' - ')
```

THE SOFTWARE AND INSTRUCTIONS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
