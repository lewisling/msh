#!/bin/bash
# based on http://stackoverflow.com/questions/16541582/finding-multiple-files-recursively-and-renaming-in-linux/27242371#27242371

dir=$1

for file in $(find $dir -name '*.xml') ; do
	mv $file $(echo "$file" | sed -r 's|.xml|-orig.xml|g')
done
