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
	"year": 202601,
	"classes": [
		"Rcos Open Source Development",
		"Introduction to Formal Logic",
		"Introduction To Algorithms",
		"Principles of Software",
		"__DONT__Graph Theory",
		"__DONT__Computability and Logic",
		"Foundations Of Analysis",
		"Intro Differential Equations",
		"__DONT__Advanced Computer Systems",
		"Robotics II",
		"Computer Components and Operations",
		"Embedded Control"
	],
	"filters" : {
		"classes to force": [
			"Introduction To Algorithms" < if you put something here you also need it in the classes list
		],
		"cred": {
			"min": 16,
			"max": 20
		}
	}
}
```

# Running
Run the main.py and you should see a output that looks like:
```
found 48 combos
Cred l:h     CRSE:     Title:                           CRIs:
---------------------------------------------------------------------------------------------------------------
4:4          2300      Introduction To Algorithms       72238, 72272, 72602, 72027, 72028, 72284
4:4          2400      Intro Differential Equations     72232, 72233, 72394, 72491, 72212, 72087, 72088, 72089
4:4          4090      Foundations Of Analysis          72573
1:4          4700      Rcos Open Source Development     75416
13:16
---------------------------------------------------------------------------------------------------------------
4:4          2300      Introduction To Algorithms       72602, 72028, 72238, 72284
4:4          2350      Embedded Control                 72017, 74143
4:4          4090      Foundations Of Analysis          72573
1:4          4700      Rcos Open Source Development     75416
13:16
---------------------------------------------------------------------------------------------------------------
4:4          2300      Introduction To Algorithms       72284, 72238
4:4          2350      Embedded Control                 72016
4:4          2400      Intro Differential Equations     72232, 72233, 72394, 72491
1:4          4700      Rcos Open Source Development     75416
13:16
---------------------------------------------------------------------------------------------------------------
```
