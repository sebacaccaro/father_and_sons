# Father and Sons
**Project for Information Retrieval A.A. 2020/21** <br>
*Sebastiano Caccaro*

## Exectution
In order to run the project the following dependencies need to be satisfied:
   - `Python 3.6` or greater
  
The following python modules need to be installed:
* sklearn
* tqdm
* pyspellchecker
* nltk
* python-Levenshtein
* pandas
* matplotlib

Note that the execution script will install the missing modules if they are not already installed. <br>
Before executing the project you must check which command your system uses to run python and pip:
* If the commands are `python3` and `pip3` you will need to run `execute3.bash`
* If the commands are `python` and `pip` you will need to run `execute.bash`

Note that you will also need to place the parlamientary debates as in the ```Code/Debates folder``` as indicated in the ```Code/Debates/placeholder.txt``` file <br>

Instruction are reported for `execute.bash` but they are identical for `execute3.bash`. <br>
To execute the project:
* cd into the `Code` folder
* make `execute.bash` executable
* run it in the shell with `./execute.bash`
* find something interesting to do while the project runs
* she program will output the location of the final plotted results

Note that that text correction of the project are disabled for time reason, as the project will take to much times (days) to run.

## Structure
The project is structured as follows:
* The `code` folder holds the code and the execution script for the project
* The `Report` folder contains:
  * The report itself
  * The file `table.png`: the final table with results that can obtained by executing the project
  * The file `table_correction.png`: the final table that is computed with text_correction enabled
  * The file `short.json`: which contains the full party names associated with their short form reported in the table.
