This project is to help students find courses that fit together of a schedule.

# Setup
To pull the data run the commands:
```
git submodule init
git submodule update
```
To update the data you can run:
```
git submodule foreach git pull origin master
```

Input should go into a json named "classes.json":
```
{
	"year": 202609,
	"classes": [
		"Rcos Open Source Development",
		"Introduction to Formal Logic",
		"Introduction To Algorithms",
		"Principles of Software",
		"__DONT__Graph Theory",
		"__DONT__Computability and Logic",
		"Foundations Of Analysis",
		"Intro Diff Equations",
		"Robotics II",
		"Embedded Control"
	],
	"filters" : {
		"classes to force": [
			"Introduction To Algorithms",			< if you put something here you also need it in the classes list
			"Rcos Open Source Development"
		],
		"cred": {
			"min": 16,
			"max": 20
		},
		"time": {
			"min": 1000,							< this is 10:00am, 10:30am would look like 1030
			"max": 2400
		}
	}
}
```

# Running
Run the main.py and you should see a output that looks like:
```
found 98 combos
Cred l:h     SUBJ:     CRSE:     Title:                           CRIs:
-----------------------------------------------------------------------------------------------------------------------------------------------------
4:4          CSCI      2300      Introduction To Algorithms       72238, 72272, 72602, 72027, 72028, 72284
1:4          CSCI      4700      Rcos Open Source Development     75416
4:4          MATH      2400      Intro Differential Equations     72232, 72233, 72394, 72491, 72297, 72299, 72300, 72298, 72212, 72087, 72088, 72089
4:4          MATH      4090      Foundations Of Analysis          72573
13:16
-----------------------------------------------------------------------------------------------------------------------------------------------------
4:4          CSCI      2300      Introduction To Algorithms       72602, 72028, 72238, 72284
1:4          CSCI      4700      Rcos Open Source Development     75416
4:4          ENGR      2350      Embedded Control                 72016, 74143
4:4          MATH      2400      Intro Differential Equations     72232, 72297, 72233, 72299, 72300, 72394, 72491
13:16
-----------------------------------------------------------------------------------------------------------------------------------------------------
4:4          CSCI      2300      Introduction To Algorithms       72602, 72028, 72238, 72284
1:4          CSCI      4700      Rcos Open Source Development     75416
4:4          ENGR      2350      Embedded Control                 72017, 74143
4:4          MATH      4090      Foundations Of Analysis          72573
13:16
-----------------------------------------------------------------------------------------------------------------------------------------------------
4:4          CSCI      2300      Introduction To Algorithms       72602, 72028, 72238, 72284
1:4          CSCI      4700      Rcos Open Source Development     75416
4:4          ENGR      2350      Embedded Control                 74143
4:4          MATH      2400      Intro Differential Equations     72297, 72299, 72300
4:4          MATH      4090      Foundations Of Analysis          72573
17:20
-----------------------------------------------------------------------------------------------------------------------------------------------------
```
