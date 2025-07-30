# Vis

Visualize fuzzy tabular data, no script required.

## Features

### Histograms

```shell
awk 'BEGIN { for (i = 0; i < 1000; i++) print rand() * 100 }' | vis hist --kde
```

<p align="center"><img src="https://raw.githubusercontent.com/hcgatewood/vis/main/assets/vis_hist.png" alt="Vis histograms" width="550"/></p>

### Scatter plots

```shell
echo -e '1 2\n1.5 3\n2 1\n3 1.5\n2 2' | vis scatter --trend
```

<p align="center"><img src="https://raw.githubusercontent.com/hcgatewood/vis/main/assets/vis_scatter.png" alt="Vis scatter plots" width="550"/></p>

### Line plots

```shell
seq 0 0.1 10 | awk '{print $1, sin($1)}' | vis line --xlab "Time" --ylab "sin(t)"
```

<p align="center"><img src="https://raw.githubusercontent.com/hcgatewood/vis/main/assets/vis_line.png" alt="Vis line plots" width="550"/></p>

## Install

```bash
pip install vis_cli
```

## More info

### Example histogram: Kubernetes CPU utilization

```shell
kubectl top nodes | vis hist --static --col 2 --bins 10 --xmax 100 --xlab 'CPU util' --kde
```

<p align="center"><img src="https://raw.githubusercontent.com/hcgatewood/vis/main/assets/k8s_hist.png" alt="Vis histogram Kubernetes CPU utilization" width="550"/></p>

### Example scatter plot: Kubernetes pod CPU vs memory limits

```shell
kubectl resource-capacity --pods | grep -v '\*.*\*' | vis scatter --static --cols 4 6 --xlab "CPU limits" --ylab "Memory limits" --trend
```

<p align="center"><img src="https://raw.githubusercontent.com/hcgatewood/vis/main/assets/k8s_scatter.png" alt="Vis scatter plot Kubernetes pod CPU vs memory limits" width="550"/></p>

### Help pages

```text
$ vis --help
Usage: vis [OPTIONS] COMMAND [ARGS]...

  A fuzzy tabular data visualization tool.

Options:
  -h, --help  Show this message and exit.

Commands:
  clean    Clean the data from a file or stdin and print it to stdout.
  hist     Create a histogram from numerical data.
  line     Create a line plot from tabular data.
  scatter  Create a scatter plot from tabular data.
```
