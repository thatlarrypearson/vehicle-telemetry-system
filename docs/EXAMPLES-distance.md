# Examples - Distance

Without vehicle support for the OBD command ```ODOMETER``` (0xA6), calculating distance travelled by the vehicle can be a bit of a chore.  Two methods come to mind:

- OBD command ```DISTANCE_SINCE_DTC_CLEAR``` (0x31) provides kilometers since the last Diagnostic Trouble Code (DTC) was cleared.
- OBD command ```SPEED``` (0xA6) provides kilomters per hour that can be mulitplied by sample time to get distance.

However, we can't just assume that these methods are accurate.  They must be verified against Odometer readings made at intervals consistent with telemetry data file boundaries.

## ```compare_distance.sh```

This is a Linux bash shell script that will also run on Windows (using [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/) [Ubuntu](https://ubuntu.com/wsl) or [git for Windows](https://gitforwindows.org/)).

Using vehicle data collected by [```telemetry_obd.obd_logger```](https://github.com/thatlarrypearson/telemetry-obd) and then put into CSV format records by [```obd_log_to_csv.obd_log_to_csv```](https://github.com/thatlarrypearson/telemetry-obd-log-to-csv), ```compare_distance.sh``` calculates the distance covered in the input file and then converts distance measures into miles for output.

Before running ```compare_distance.sh```, environment variables must be modified to match the file system of the target machine.

Sample ```compare_distance.sh```  output from 2013 Jeep Wrangler Rubicon data set:

```bash
human@widebody:/mnt/c/Users/human/src/telemetry-obd-log-to-csv$ bash examples/compare_distance.sh
input_file_name,first_distance,last_distance,DISTANCE_SINCE_DTC_CLEAR_difference,distance_calculated_from_SPEED_X_duration,difference,difference_percent
C4HJWCG5DL0000-20220123150422-utc.json,4061.9,4156.97,95.07,95.3539,-0.2839,-0.298622%
C4HJWCG5DL0000-20220123163551-utc.json,4156.97,4184.31,27.34,27.3087,0.0313,0.114484%
C4HJWCG5DL0000-20220123173549-utc.json,4184.31,4237.75,53.44,53.6589,-0.2189,-0.409618%
C4HJWCG5DL0000-20220123182149-utc.json,4238.37,4311.07,72.7,72.6153,0.0847,0.116506%
C4HJWCG5DL0000-20220123192346-utc.json,4311.07,4392.47,81.4,81.5691,-0.1691,-0.20774%
C4HJWCG5DL0000-20220123210857-utc.json,4392.47,4429.76,37.29,37.2481,0.0419,0.112363%
C4HJWCG5DL0000-20220124130950-utc.json,4430.38,4506.81,76.43,76.7282,-0.2982,-0.390161%
C4HJWCG5DL0000-20220124143722-utc.json,4506.81,4601.25,94.44,94.4535,-0.0135,-0.0142948%
C4HJWCG5DL0000-20220124161016-utc.json,4601.88,4667.12,65.24,65.4866,-0.2466,-0.377989%
C4HJWCG5DL0000-20220124174554-utc.json,4667.12,4757.22,90.1,90.4263,-0.3263,-0.362153%
C4HJWCG5DL0000-20220124190329-utc.json,4757.22,4810.03,52.81,53.2853,-0.4753,-0.900019%
C4HJWCG5DL0000-20220124195254-utc.json,4810.66,4887.71,77.05,77.8402,-0.7902,-1.02557%
C4HJWCG5DL0000-20220124210700-utc.json,4888.33,4947.98,59.65,60.2644,-0.6144,-1.03001%
C4HJWCG5DL0000-20220124224517-utc.json,4948.6,5023.16,74.56,75.2333,-0.6733,-0.903031%
human@widebody:/mnt/c/Users/human/src/telemetry-obd-log-to-csv$
```

This output can be imported into programs that process CSV data such as Python Pandas and Microsoft Excel.  The data is more easily read after it has been put into tabular format:

|input file name|first distance|last distance|DISTANCE SINCE DTC CLEAR difference|distance calculated from SPEED X duration|difference|difference percent|
|---|---|---|---|---|---|---|
|C4HJWCG5DL0000-20220123150422-utc.json|4061.9|4156.97|95.07|95.3539|-0.2839|-0.298622%|
|C4HJWCG5DL0000-20220123163551-utc.json|4156.97|4184.31|27.34|27.3087|0.0313|0.114484%|
|C4HJWCG5DL0000-20220123173549-utc.json|4184.31|4237.75|53.44|53.6589|-0.2189|-0.409618%|
|C4HJWCG5DL0000-20220123182149-utc.json|4238.37|4311.07|72.7|72.6153|0.0847|0.116506%|
|C4HJWCG5DL0000-20220123192346-utc.json|4311.07|4392.47|81.4|81.5691|-0.1691|-0.20774%|
|C4HJWCG5DL0000-20220123210857-utc.json|4392.47|4429.76|37.29|37.2481|0.0419|0.112363%|
|C4HJWCG5DL0000-20220124130950-utc.json|4430.38|4506.81|76.43|76.7282|-0.2982|-0.390161%|
|C4HJWCG5DL0000-20220124143722-utc.json|4506.81|4601.25|94.44|94.4535|-0.0135|-0.0142948%|
|C4HJWCG5DL0000-20220124161016-utc.json|4601.88|4667.12|65.24|65.4866|-0.2466|-0.377989%|
|C4HJWCG5DL0000-20220124174554-utc.json|4667.12|4757.22|90.1|90.4263|-0.3263|-0.362153%|
|C4HJWCG5DL0000-20220124190329-utc.json|4757.22|4810.03|52.81|53.2853|-0.4753|-0.900019%|
|C4HJWCG5DL0000-20220124195254-utc.json|4810.66|4887.71|77.05|77.8402|-0.7902|-1.02557%|
|C4HJWCG5DL0000-20220124210700-utc.json|4888.33|4947.98|59.65|60.2644|-0.6144|-1.03001%|
|C4HJWCG5DL0000-20220124224517-utc.json|4948.6|5023.16|74.56|75.2333|-0.6733|-0.903031%|

The above data shows how close the rate (```SPEED```) times time equals distance calculation compares to ```DISTANCE_SINCE_DTC_CLEAR``` distance difference in each file.  Less than 1%!.

Next, a comparision between manually collected fuel milage data and the above data set.

|input|first distance|last distance|DISTANCE SINCE DTC CLEAR difference|distance calculated from SPEED X duration|difference|difference percent|Odometer Start|Odometer Stop|Odometer Distance|Sub Total|
|---|---|---|---|---|---|---|---|---|---|---|
|2022/01/23 15:04:22|4061.9|4156.97|95.07|95.3539|-0.2839|-0.298622%||||
|2022/01/23 16:35:51|4156.97|4184.31|27.34|27.3087|0.0313|0.114484%||||
||||||||69,224|69,347|123|122.41|
|2022/01/23 17:35:49|4184.31|4237.75|53.44|53.6589|-0.2189|-0.409618%||||
|2022/01/23 18:21:49|4238.37|4311.07|72.7|72.6153|0.0847|0.116506%||||
|2022/01/23 19:23:46|4311.07|4392.47|81.4|81.5691|-0.1691|-0.20774%||||
||||||||69,347|69,555|208|207.54|
|2022/01/23 21:08:57|4392.47|4429.76|37.29|37.2481|0.0419|0.112363%||||
|2022/01/24 13:09:50|4430.38|4506.81|76.43|76.7282|-0.2982|-0.390161%||||
|2022/01/24 14:37:22|4506.81|4601.25|94.44|94.4535|-0.0135|-0.0142948%||||
||||||||69,555|69,764|209|208.16|
|2022/01/24 16:10:16|4601.88|4667.12|65.24|65.4866|-0.2466|-0.377989%||||
|2022/01/24 17:45:54|4667.12|4757.22|90.1|90.4263|-0.3263|-0.362153%||||
|2022/01/24 19:03:29|4757.22|4810.03|52.81|53.2853|-0.4753|-0.900019%||||
||||||||69,764|69,973|209|208.15|
|2022/01/24 19:52:54|4810.66|4887.71|77.05|77.8402|-0.7902|-1.02557%||||
|2022/01/24 21:07:00|4888.33|4947.98|59.65|60.2644|-0.6144|-1.03001%||||
||||||||69,973|70,112|139|136.7|
|2022/01/24 22:45:17|4948.6|5023.16|74.56|75.2333|-0.6733|-0.903031%||||

The above shows Odometer readings are within 1% of the ```DISTANCE_SINCE_DTC_CLEAR``` distances.

Conclusion:

- Sum generated by rate (```SPEED```) times duration equals distance readings are valid substitutes for odometer readings.
- When supported, ```DISTANCE_SINCE_DTC_CLEAR``` is a valid substitute for odometer readings.

### Unexpected Behavior?

When the car doesn't move during the data collection period represented by the file:

- ```DISTANCE_SINCE_DTC_CLEAR```'s value doesn't change.
- ```SPEED```'s value is always zero.

The result is as follows for one of the files.

```bash
$ bash examples/compare_distance.sh
input_file_name,first_distance,last_distance,DISTANCE_SINCE_DTC_CLEAR_difference,distance_calculated_from_SPEED_X_duration,difference,difference_percent
MAJ6S3KL0KC000000-20220314161103-utc.json,16498,16499.9,1.9,2.09059,-0.19059,-10.0311%
MAJ6S3KL0KC000000-20220314161446-utc.json,16499.9,16618,118.1,260.766,-142.666,-120.801%
MAJ6S3KL0KC000000-20220315133946-utc.json,16618.6,16729.2,110.6,110.605,-0.005,-0.0045208%
MAJ6S3KL0KC000000-20220315152329-utc.json,16730.4,16854.1,123.7,163.564,-39.864,-32.2264%
awk: cmd. line:1: (FILENAME=- FNR=1) fatal: division by zero attempted
MAJ6S3KL0KC000000-20220315184112-utc.json,16854.1,16854.1,0,0,0,%
MAJ6S3KL0KC000000-20220315184301-utc.json,16854.7,17012.5,157.8,157.179,0.621,0.393536%
MAJ6S3KL0KC000000-20220315205749-utc.json,17013.1,17102.6,89.5,89.5553,-0.0553,-0.0617877%
MAJ6S3KL0KC000000-20220315230529-utc.json,17103.9,17104.5,0.6,0.488603,0.111397,18.5662%
MAJ6S3KL0KC000000-20220316114638-utc.json,17104.5,17105.1,0.6,0.754257,-0.154257,-25.7095%
MAJ6S3KL0KC000000-20220316121043-utc.json,17105.1,17185.9,80.8,80.3719,0.4281,0.529827%
MAJ6S3KL0KC000000-20220316155834-utc.json,17344.3,17377.3,33,32.7566,0.2434,0.737576%
MAJ6S3KL0KC000000-20220316190650-utc.json,17468.6,17469.9,1.3,1.37092,-0.07092,-5.45538%
MAJ6S3KL0KC000000-20220316194528-utc.json,17472.3,17475.4,3.1,3.53178,-0.43178,-13.9284%
$
```

This error comes from the shell variable ```delta``` having the value of zero.  This is due to the difference distance based on ```DISTANCE_SINCE_DTC_CLEAR``` being the same as the calculated distance based on ```rate *X* time = distance```.

```bash
export delta=$(echo ${difference_distance},${calculated_distance} | awk -F ',' '// {print $1 - $2}')
export percent=$(echo ${difference_distance},${delta} | awk -F ',' '// {print ($2/$1)*100.0}')
```

## ```distance.py```

Calculate distance from speed and duration for comparison to OBD command ```DISTANCE_SINCE_DTC_CLEAR```.

- distance = rate * time
  
  Where rate is ```SPEED``` in kilometers per hour.

Input for ```distance.py``` comes from ```obd_log_to_csv.obd_log_to_csv``` called with minimal optional arguments ```--commands 'DISTANCE_SINCE_DTC_CLEAR,SPEED'```.   All included commands from ```--commands``` argument are passed through to output without change.  Distance sums are calculated and added into the output stream using these unique column names:

- ```distance``` in kilometers

  Calculated from ```SPEED```  in kilometers per hour times ```duration```, a ```TimeDelta``` value converted to hours.

- ```distance_sum```

  Ongoing sum of ```distance```.

- ```miles```

  ```distance``` converted to miles.

- ```miles_sum```
  
  ```distance_sum``` converted to miles.

### Usage

```bash
$ python3.10 examples/distance.py --help
usage: obd_log_to_csv [-h] [--csv CSV] [--verbose] files [files ...]

distance = rate * time. Calculate distance from speed and time. Compare to
distance since DTC clear.

positional arguments:
  files       obd_log_to_csv generated data files separated by spaces. Data
              file names can include full or relative paths.

optional arguments:
  -h, --help  show this help message and exit
  --csv CSV   CSV output file. File can be either a full or relative path
              name. If the file already exists, it will be overwritten.
              Defaults to terminal output (stdout).
  --verbose   Turn verbose output on. Default is off.

$
```

## ```distance.sh```

This is a Linux bash shell script that will also run on Windows (using [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/) [Ubuntu](https://ubuntu.com/wsl) or [git for Windows](https://gitforwindows.org/)).

Using vehicle data collected by [```telemetry_obd.obd_logger```](https://github.com/thatlarrypearson/telemetry-obd) and then put into CSV format records by [```obd_log_to_csv.obd_log_to_csv```](https://github.com/thatlarrypearson/telemetry-obd-log-to-csv), ```distance.sh``` calculates the distance covered in the input file and then converts distance measures into miles for output.

Before running ```distance.sh```, environment variables must be modified to match the file system of the target machine.

```bash
$ bash examples/distance.sh
output file is C4HJWCG5DL0000-20220124174554-utc.csv
output file is C4HJWCG5DL0000-20220124190329-utc.csv
output file is C4HJWCG5DL0000-20220124195254-utc.csv
output file is C4HJWCG5DL0000-20220124210700-utc.csv
output file is C4HJWCG5DL0000-20220124224517-utc.csv
output file is C4HJWCG5DL0000-20220125000133-utc.csv
$
$ head C4HJWCG5DL0000-20220124174554-utc.csv
DISTANCE_SINCE_DTC_CLEAR,SPEED,iso_ts_pre,iso_ts_post,duration,distance,distance_sum,miles,miles_sum,miles_since_dtc_clear
,14.0,2022-01-24 17:45:56.065328+00:00,2022-01-24 17:45:56.607397+00:00,0:00:00.542069,0.0021080461111111113,0.0021080461111111113,0.0013098791206359833,0.0013098791206359833,
,14.0,2022-01-24 17:45:56.607397+00:00,2022-01-24 17:45:56.923580+00:00,0:00:00.316183,0.0012296005555555555,0.003337646666666667,0.0007640383604302166,0.0020739174810662,
,14.0,2022-01-24 17:45:56.923580+00:00,2022-01-24 17:45:57.238778+00:00,0:00:00.315198,0.00122577,0.004563416666666667,0.0007616581635663,0.0028355756446325,
,14.0,2022-01-24 17:45:57.238778+00:00,2022-01-24 17:45:57.539876+00:00,0:00:00.301098,0.0011709366666666666,0.005734353333333333,0.0007275863099812999,0.0035631619546138,
,14.0,2022-01-24 17:45:57.539876+00:00,2022-01-24 17:45:57.872557+00:00,0:00:00.332681,0.0012937594444444444,0.0070281127777777775,0.0008039048455681832,0.0043670668001819825,
,14.0,2022-01-24 17:45:57.872557+00:00,2022-01-24 17:45:58.218626+00:00,0:00:00.346069,0.001345823888888889,0.008373936666666667,0.0008362561913693167,0.005203322991551299,
7511.0,14.0,2022-01-24 17:45:58.218626+00:00,2022-01-24 17:45:58.529933+00:00,0:00:00.311307,0.0012106383333333331,0.009584575,0.0007522557818429498,0.005955578773394249,4667.11900809
,14.0,2022-01-24 17:45:58.529933+00:00,2022-01-24 17:45:58.860144+00:00,0:00:00.330211,0.0012841538888888888,0.010868728888888889,0.0007979362300820165,0.006753515003476266,
,14.0,2022-01-24 17:45:58.860144+00:00,2022-01-24 17:45:59.202398+00:00,0:00:00.342254,0.0013309877777777778,0.012199716666666667,0.0008270374593532333,0.0075805524628295,
$
$ tail C4HJWCG5DL0000-20220124174554-utc.csv
,108.0,2022-01-24 19:03:24.621924+00:00,2022-01-24 19:03:25.071800+00:00,0:00:00.449876,0.01349628,145.4665906116673,0.0083861995641732,90.38874851361453,
,108.0,2022-01-24 19:03:25.071800+00:00,2022-01-24 19:03:25.515533+00:00,0:00:00.443733,0.01331199,145.4799026016673,0.008271687067568098,90.3970202006821,
,108.0,2022-01-24 19:03:25.515533+00:00,2022-01-24 19:03:26.036181+00:00,0:00:00.520648,0.01561944,145.4955220416673,0.009705470019933599,90.40672567070203,
,109.0,2022-01-24 19:03:26.036181+00:00,2022-01-24 19:03:26.548263+00:00,0:00:00.512082,0.015504705000000002,145.5110267466673,0.00963417699644895,90.41635984769849,
7656.0,109.0,2022-01-24 19:03:26.548263+00:00,2022-01-24 19:03:27.077067+00:00,0:00:00.528804,0.01601101,145.5270377566673,0.0099487803368019,90.42630862803529,4757.21783064
,109.0,2022-01-24 19:03:27.077067+00:00,2022-01-24 19:03:27.523255+00:00,0:00:00.446188,0.01350958111111111,145.54054733777843,0.008394464491412632,90.43470309252672,
,109.0,2022-01-24 19:03:27.523255+00:00,2022-01-24 19:03:27.982024+00:00,0:00:00.458769,0.013890505833333332,145.55443784361177,0.008631160139360274,90.44333425266608,
,109.0,2022-01-24 19:03:27.982024+00:00,2022-01-24 19:03:28.593254+00:00,0:00:00.611230,0.01850668611111111,145.5729445297229,0.011499521571817583,90.4548337742379,
,110.0,2022-01-24 19:03:28.593254+00:00,2022-01-24 19:03:29.114511+00:00,0:00:00.521257,0.01592729722222222,145.5888718269451,0.009896763628455915,90.46473053786634,
,110.0,2022-01-24 19:03:29.114511+00:00,2022-01-24 19:03:29.237322+00:00,0:00:00.122811,0.003752558333333333,145.59262438527844,0.00233173163712775,90.46706226950347,
$
```

## ```miles_since_dtc_clear.sh```

Simple Linux bash program to extract ```DISTANCE_SINCE_DTC_CLEAR``` from ```obd_log_to_csv.obd_log_to_csv``` generated files.  The input files need to be generated with  ```DISTANCE_SINCE_DTC_CLEAR``` being the first OBD command listed in the ```--commands``` argument first before any other commands.  This places ```DISTANCE_SINCE_DTC_CLEAR``` as the first column in the output CSV file.

For example:

```bash
$ python3.10 -m obd_log_to_csv.obd_log_to_csv --csv tmp.csv --commands 'DISTANCE_SINCE_DTC_CLEAR,SPEED'  ../telemetry-obd/data/*/*.json
$ bash miles_since_dtc_clear.sh
file_name,first_distance,last_distance
tmp.csv,2448.82,3018
$
```

In the above output, the input file, ```tmp.csv``` was the only ```csv``` file in the current directory.  ```miles_since_dtc_clear.sh``` is fairly simplistic and it processes all ```csv``` files in the current working directory.
