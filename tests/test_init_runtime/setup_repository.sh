rm -rf $1
mkdir $1
cd $1
git init  &> /dev/null
touch README.md
git add .
git commit -m "Initial Import" &> /dev/null
for i in $(seq 1 $1)
do
    file_name=$(( $RANDOM % 50 ))
    content=$RANDOM
    echo "$content" > $file_name.md;
    
    include_issue=$(( $RANDOM % 10 ))

    if [ $include_issue -eq 1 ]
    then
	git checkout -b $file_name &> /dev/null
        echo -e "---\n@issue $file_name\n@title An Issue\n---" >> $file_name.md
        MESSAGE="Commit $i Creates Issue $file_name"
    else
        MESSAGE="Commit $i"
    fi   
    
    git add  . &> /dev/null
    git commit --quiet -m "$MESSAGE"
    git checkout master &> /dev/null
    echo $MESSAGE
done
cd ..
