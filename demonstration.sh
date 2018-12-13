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
mkdir -p backlog
cat > backlog/photo-upload-on-claim.md <<-EOF
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

git add backlog
git commit -m "Adds Photo Upload on Claim"
git-sciit.exe status -f
git-sciit.exe issue photo-upload-on-claim

git checkout master
git merge photo-upload-on-claim
git-sciit.exe status -f
git-sciit.exe issue photo-upload-on-claim

git checkout photo-upload-on-claim
git checkout -b photo-upload-on-claim-uat
mkdir features
cat > features/claim.feature <<-EOF
#***
# @issue photo-upload-on-claim-uat
# @title Photo Upload on Claim UAT
# @description
#  Extend existing claim user stories
#   with scenarios that include photo
#   upload.
#***
EOF

cat > backlog/photo-upload-on-claim.md <<-EOF
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
@blockers photo-upload-on-claim-uat, photo-upload-on-claim-db, photo-upload-on-claim-views
@priority medium
---
EOF

git add features/claim.feature
git add backlog/photo-upload-on-claim.md
git commit -m "Begins Work on Photo Upload on Claim"
git-sciit.exe status -f

git checkout photo-upload-on-claim
git merge photo-upload-on-claim-uat
git checkout master
git merge photo-upload-on-claim
git-sciit.exe tracker

git checkout photo-upload-on-claim-uat

cat > features/claim.feature <<-EOF
#***
# @issue photo-upload-on-claim-uat
# @title Photo Upload on Claim UAT
# @description
#  Extend existing claim user stories
#   with scenarios that include photo
#   upload.
#***

Feature: Photo upload for claims
Scenario: Small JPEG Upload with Description
 Given a claim
 And a small JPEG 
 And a description
 When I select the photograph
 And I enter a description
 And I click submit
 Then the photograph is stored
 And a database entry is created.

EOF

git add features/claim.feature
git commit -m "Creates new Scenario for Small JPG Upload on Claims"
git sciit issue photo-upload-on-claim-uat

cat > features/claim.feature <<-EOF

Feature: Photo upload for claims
Scenario: Small JPEG Upload with Description
 Given a claim
 And a small JPEG 
 And a description
 When I select the photograph
 And I enter a description
 And I click submit
 Then the photograph is stored
 And a database entry is created.

EOF

git add features/claim.feature
git commit -m "Closes photo-upload-on-claim-uat"
git sciit issue photo-upload-on-claim-uat

git checkout photo-upload-on-claim
git merge photo-upload-on-claim-uat
git sciit issue photo-upload-on-claim-uat

git checkout master
git merge photo-upload-on-claim
git sciit tracker 

git checkout photo-upload-on-claim
git rm backlog/photo-upload-on-claim.md
git commit -m "Closes photo-upload-on-claim"
git sciit issue photo-upload-on-claim

git checkout master
git merge photo-upload-on-claim
git sciit issue photo-upload-on-claim

git sciit tracker -fa
