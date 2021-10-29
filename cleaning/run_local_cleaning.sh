# clean_data.sh

# remove old
rm -r local_cleaning/

# make new paths
echo "Making a copy of data files..."
mkdir -p local_cleaning/data/speeches
 # copy data
cp -r data/speeches/ local_cleaning/data/speeches/

# remove extra files that dont need cleaning
echo "Remove unecessary files"
rm local_cleaning/data/speeches/Campaign _Speech_Overview.xlsx
rm local_cleaning/data/speeches/Icon?
rm local_cleaning/data/speeches/.dropbox
find local_cleaning/data/ -name "*.DS_Store" -type f -delete

# call cleaning script, and output data into a log file
echo "Cleaning data... (this usually takes a long time)"
python senior-design/cleaning.py local_cleaning/data/speeches/ > local_cleaning/cleaning_log.txt

echo "Done! Check local_cleaning/cleaning_log.txt for output:"
more local_cleaning/cleaning_log.txt
