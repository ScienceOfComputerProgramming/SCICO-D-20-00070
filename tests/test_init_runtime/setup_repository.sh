mkdir $1
cd $1
rm -rf .git
rm *.md
git init
for i in $(seq 1 $1)
do
    echo $i
    file_name=$(( $RANDOM % 50 ))
    content=$RANDOM
    echo "$content" > $file_name.md;
    git add  . &> /dev/null
    git commit --quiet -m "Commit $i"
    
    include_issue=$(( $RANDOM % 10 ))
    if [ $include_issue -eq 1 ]
    then
	echo -e "---\n@issue $file_name\n@title An Issue\n---" >> $file_name.md
    fi
done
cd ..
