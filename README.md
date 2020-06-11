# AutomaticBookSortThingy

Small utility to automatically structure files into a folder hierarchy based on their name.

## Usage
Just place all the files (e.g. books) you want sorted into the base directory and create subfolders (e.g. "Mathematics", "Computer Science" etc.) with potential subfolders (e.g. "Algebra", "Analysis" etc.), run the script and it'll sort the files into the folders. The files' names are automatically normalized in some way (e.g. umlauts to digraphs and converted to ASCII). You have to specify a dump folder (the DUMP constant) in case there's files that can't be matched with enough confidence.
You may create a "keywords.txt" file in each folder that lists keywords that are related to the folder and taken into account for the sorting (e.g. a folder "Language Implementation" may have a keywords.txt that lists stuff like "compilers", "type systems" etc.).

## Requirements
[fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/)
