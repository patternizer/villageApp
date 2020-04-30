![image](https://github.com/patternizer/birdpy/blob/master/villageApp.png)

# villageApp

Plotly Dash Python app using APIs to obtain hourly spot data from OpenWeather. UKMO, UKEA, OpenWeather and GuageMap.

## Contents

* `villageApp.py` - main script to be run with Python 3.6+

The first step is to clone latest Village code and step into the check out directory: 

    $ git clone https://github.com/patternizer/villageApp.git
    $ cd villageApp
    
### Using Standard Python 

The code should run with the [standard CPython](https://www.python.org/downloads/) installation and was tested 
in a conda virtual environment running a 64-bit version of Python 3.6+.

villageApp can be run from sources directly, once the following module requirements are resolved:

* `keys.txt` - a 2-column CSV file having the form of 'keys_template.txt' with your keys entered inplace
* python libraries listed in villageApp

Run with:

    $ python villageApp.py
        
## License

The code is distributed under terms and conditions of the [MIT license](https://opensource.org/licenses/MIT).

## Contact information

* [Michael Taylor](https://patternizer.github.io)

