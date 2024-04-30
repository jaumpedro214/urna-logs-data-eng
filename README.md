
# Processing Logs of Electronic Ballot Boxes
This repository contains Python + DuckDB scripts for processing logs from [Brazilian Electronic Ballot Boxes](https://international.tse.jus.br/en/electronic-ballot-box/presentation?set_language=en) to compute several time-related metrics (mean vote time, number of votes computed in 5min, percentage of biometric identification success).

## The Data
The logs from the voting machines can be directly downloaded from the [TSE open data website](https://dadosabertos.tse.jus.br/dataset/resultados-2022-arquivos-transmitidos-para-totalizacao). This repository contains Python scripts that automatically download and extract the logs.

## What are the logs of the Electronic Ballot Boxes?
Files that contain all operations performed on the machine, from the initial setup to the end of voting in the second round (if applicable). The files are stored in plain text, with each line representing an event. See an example below:

```
21/09/2022 17:21:41	INFO	67305985	LOGD	Start of logd operations	                  FDE9B0FC7A079096
21/09/2022 17:21:41	INFO	67305985	LOGD	Machine turned on on 21/09/2022 at 17:20:16	B637C17E565B039B
21/09/2022 17:21:41	INFO	67305985	SCUE	Starting application - Official - 1st round	F82E007ACCAF93A5
21/09/2022 17:21:41	INFO	67305985	SCUE	Application version: 8.26.0.0 - Jaguar	    D499E9A173814A70
```
With these logs, it is possible to extract numerous pieces of information about the electoral process. Due to their verbosity, the logs of the Ballot Boxes are very heavy. In their original format, the set of log files for a single Brazilian state can range from 2GB to over 50GB, with all the files combined reaching 450GB! Therefore, robust processing tools and optimized file formats are indispensable.

## Note on Approximations and Errors
Processing the logs of the voting machines is not a simple task.
Although they are easy to read, defining a process that perfectly isolates each vote is a complex task because numerous situations can occur during the voting process.

The scripts coded here attempt to be as generic and simple as possible, to facilitate understanding, maintenance, and reduce the computational cost of processing. Therefore, they may occasionally not capture ALL votes perfectly. The error rate (uncaptured votes) considering the official count from the TSE is ~3% (experiment conducted with RN data).
