job -h > doc/job.txt
for cmd in product sample resample run analyze; do
    job $cmd -h > doc/$cmd.txt
done
