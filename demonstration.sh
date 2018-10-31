rm -rf demo
mkdir demo
cd demo
rm -rf .git/
git init
git-sciit.exe init
touch README.md
git add README.md
git commit -m "Initial import."

git checkout -b photo-upload-on-claim
mkdir -p docs/issues
cat > docs/issues/photo-upload-on-claim.md <<-EOF
---
@issue photo-upload-on-claim
@title Photo Upload on Claim
@description
 We need a photo upload 
 feature so that customers can
 provide supplemental evidence
 for their insurance claim, 
 e.g. of damage during a Road
 Traffic Accident.
@priority medium
---
EOF
git add docs/issues
git commit -m "Adds Photo Upload on Claim"
git-sciit.exe status -f
git-sciit.exe issue photo-upload-on-claim

git checkout master
git merge photo-upload-on-claim
git-sciit.exe status -f
git-sciit.exe issue photo-upload-on-claim

git checkout photo-upload-on-claim 
mkdir -p ensure
cat > ensure/main.py <<-EOF
"""
@issue photo-upload-on-claim
@title Photo Upload on Claim
@description
 We need a photo upload 
 feature so that customers can
 provide supplemental evidence
 for their insurance claim, 
 e.g. of damage during a Road
 Traffic Accident.
@priority medium
"""
EOF

git add ensure/main.py
git rm docs/issues/photo-upload-on-claim.md
git commit -m "Begins Work on Photo Upload on Claim"
git-sciit.exe status -f
git-sciit.exe issue photo-upload-on-claim

rm ensure/main.py
touch ensure/main.py
git add ensure/main.py
git commit -m "Closes Photo Upload on Claim"
git-sciit.exe status -f
git-sciit.exe issue photo-upload-on-claim

git checkout master
git merge photo-upload-on-claim
git-sciit.exe status -f
git-sciit.exe issue photo-upload-on-claim

