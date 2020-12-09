# Setup

SCIIT='git sciit'

rm -rf demo
mkdir demo
cd demo
rm -rf .git/
git init
$SCIIT init
touch README.md
git add README.md
git commit -m "Initial import."


# Add first issue

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
git commit -m "Adds new issue Photo Upload on Claim"
$SCIIT status -f
$SCIIT issue photo-upload-on-claim

# Accept first issue

git checkout master
git merge photo-upload-on-claim
$SCIIT status -f
$SCIIT issue photo-upload-on-claim

# Add three sub-issues


## First sub-issue

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

git add features/claim.feature
git commit -m "Creates new issue to create a scenario for Small JPG Upload on Claims"
$SCIIT issue photo-upload-on-claim-uat

## Second sub-issue

git checkout photo-upload-on-claim
git checkout -b photo-upload-on-claim-db

mkdir insure_and_go
cat > insure_and_go/db.py <<-EOF
"""
@issue photo-upload-on-claim-db
@title Extend Database Schema for Photo Uploads
@description
 Claim schema needs to be updated for photo
 upload meta-data, including
 
 - Filepath
 - Description

"""

EOF

git add insure_and_go/db.py
git commit -m "Creates new issue to update database schema"
$SCIIT issue photo-upload-on-claim-db


## Third sub-issue

git checkout photo-upload-on-claim
git checkout -b photo-upload-on-claim-view

mkdir insure_and_go
cat > insure_and_go/views.py <<-EOF
"""
@issue photo-upload-on-claim-view
@title Extend Claim View to Handle Photos
@description
 Extend claim view and form to handle
 photo attachments.
"""

EOF

git add insure_and_go/views.py
git commit -m "Creates new issue to update claim view"
$SCIIT issue photo-upload-on-claim-view


## Add dependencies to main issue

git checkout photo-upload-on-claim
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
@blockers photo-upload-on-claim-uat, photo-upload-on-claim-db, photo-upload-on-claim-view
@priority medium
---
EOF

git add backlog/photo-upload-on-claim.md
git commit -m "Begins Work on Photo Upload on Claim"
$SCIIT status -f

## Accept sub-issues

git checkout photo-upload-on-claim
git merge photo-upload-on-claim-uat
git merge photo-upload-on-claim-db
git merge photo-upload-on-claim-view

git checkout master
git merge photo-upload-on-claim
$SCIIT tracker

# Make progress on first sub-issue

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
git commit -m "Makes progress on UAT Scenario Photo upload for claims"
$SCIIT issue photo-upload-on-claim-uat


# Close first sub-issue

git checkout photo-upload-on-claim-uat

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
$SCIIT issue photo-upload-on-claim-uat

# Close second sub-issue

git checkout photo-upload-on-claim-db
rm insure_and_go/db.py
touch insure_and_go/db.py
git add insure_and_go/db.py
git commit -m "Closes photo-upload-on-claim-db"

# Close third sub-issue

git checkout photo-upload-on-claim-view
rm insure_and_go/views.py
touch insure_and_go/views.py
git add insure_and_go/views.py
git commit -m "Closes photo-upload-on-claim-view"

$SCIIT tracker

# Merge closed issues to master

git checkout photo-upload-on-claim
git merge photo-upload-on-claim-uat
git merge photo-upload-on-claim-db
git merge photo-upload-on-claim-view

$SCIIT tracker

git checkout master
git merge photo-upload-on-claim
$SCIIT tracker

# Close main issue

git checkout photo-upload-on-claim
git rm backlog/photo-upload-on-claim.md
git commit -m "Closes photo-upload-on-claim"

git checkout photo-upload-on-claim-uat
git merge photo-upload-on-claim

git checkout photo-upload-on-claim-db
git merge photo-upload-on-claim

git checkout photo-upload-on-claim-view
git merge photo-upload-on-claim

git checkout photo-upload-on-claim
$SCIIT issue photo-upload-on-claim

git checkout master
git merge photo-upload-on-claim
$SCIIT issue photo-upload-on-claim

$SCIIT tracker -fa
